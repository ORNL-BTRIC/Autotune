#===  Autotune Library  ===#
import eplus
import idf
import inspyred
import logs
import metrics
import utilities
#==========================#
import copy
import csv
import hashlib
import logging
import math
import multiprocessing
import os
import pickle
import tempfile
import threading
import uuid


def bounder(candidate, args):
    def roundsig(x, sig=2):
        y = 0.0 if x == 0 else round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)
        return y
        
    for group in candidate:
        variable = candidate.get_variable(group)
        candidate.set_value(group, max(min(candidate.get_value(group), variable.maximum), variable.minimum))
        if variable.type == 'integer':
            candidate.set_value(group, int(candidate.get_value(group)))
        elif variable.type == 'float':
            candidate.set_value(group, roundsig(candidate.get_value(group), 5))
    return candidate

def generator(random, args):
    eplus_variables = args['eplus']['variables']
    groups = eplus_variables.get_constraint_order()
    candidate = copy.deepcopy(eplus_variables)
    for group in groups:
        variable = candidate.get_variable(group)
        lo, hi = candidate.get_constrained_bounds(group)
        if variable.type == 'integer':
            candidate.set_value(group, random.randint(lo, hi))
        elif variable.type == 'float':
            candidate.set_value(group, random.uniform(lo, hi))
    candidate = args['_ec'].bounder(candidate, args)
    return candidate

@inspyred.ec.variators.mutator
def mutator(random, candidate, args):
    mutation_usage_rate = args.get('mutation_usage_rate', 0.1)
    mutation_rate = args.get('mutation_rate', 0.1)
    bounder = args['_ec'].bounder
    groups = candidate.get_constraint_order()
    mutant = copy.deepcopy(candidate)
    if random.random() < mutation_usage_rate:
        for group in groups:
            variable = candidate.get_variable(group)
            lo, hi = mutant.get_constrained_bounds(group)
            if variable.type == 'integer':
                if random.random() < mutation_rate:
                    options = range(lo, hi + 1)
                    options.remove(candidate.get_value(group))
                    mutant.set_value(group, random.choice(options))
                else:
                    mutant.set_value(group, candidate.get_value(group))
            elif variable.type == 'float':
                mutant.set_value(group, candidate.get_value(group) + random.gauss(0, 1) * mutation_rate * (hi - lo) / 2.0)
    return bounder(mutant, args)

def crossover(random, candidates, args):
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    bounder = args['_ec'].bounder
        
    if len(candidates) % 2 == 1:
        candidates = candidates[:-1]
        
    # Since we don't have fitness information in the candidates, we need 
    # to make a dictionary containing the candidate and its corresponding 
    # individual in the population.
    population = list(args['_ec'].population)
    lookup = dict(zip([hashlib.sha256(pickle.dumps(p.candidate.get_values(), 1)).hexdigest() for p in population], population))
    
    moms = candidates[::2]
    dads = candidates[1::2]
    children = []
    for mom, dad in zip(moms, dads):
        if random.random() < crossover_rate:
            mhash = hashlib.sha256(pickle.dumps(mom.get_values(), 1)).hexdigest()
            dhash = hashlib.sha256(pickle.dumps(dad.get_values(), 1)).hexdigest()
            mom_is_better = lookup[mhash] > lookup[dhash]
            mom_values = mom.get_values()
            dad_values = dad.get_values()
            sis_values = copy.copy(mom_values)
            bro_values = copy.copy(dad_values)
            for i, (m, d) in enumerate(zip(mom_values, dad_values)):
                negpos = 1 if mom_is_better else -1
                val = d if mom_is_better else m
                sis_values[i] = val + random.random() * negpos * (m - d)
                bro_values[i] = val + random.random() * negpos * (m - d)
            sis = copy.deepcopy(mom)
            sis.set_values(sis_values)
            sis = bounder(sis, args)
            bro = copy.deepcopy(dad)
            bro.set_values(bro_values)
            bro = bounder(bro, args)
            children.append(sis)
            children.append(bro)
        else:
            children.append(copy.deepcopy(mom))
            children.append(copy.deepcopy(dad))
    return children
    
def mean_variation(random, candidates, args):
    """Averages the population to create a new candidate.
    
    This method averages the individuals in the current population to 
    create a new candidate, which is used as a replacement for a 
    randomly selected existing candidate.
    
    Optional keyword arguments in args:
    
    - *mean_variation_rate* -- the rate at which variation is performed 
      (default 1.0)
    
    """
    rate = args.setdefault('mean_variation_rate', 1.0)
    if random.random() < rate:
        pop = args['_ec'].population
        vals = pop[0].candidate.get_values()
        average = [0 for _ in range(len(vals))]
        for p in pop:
            pvals = p.candidate.get_values()
            for i, v in enumerate(pvals):
                average[i] += v
        for i in range(len(average)):
            average[i] /= float(len(pop))
        rep_index = random.randrange(0, len(candidates))
        candidates[rep_index].set_values(average)
    return candidates
    
@inspyred.ec.evaluators.evaluator   
def evaluator(candidate, args):
    def rmse(predicted, actual):
        error = {}
        count = {}
        for pred_row, act_row in zip(predicted, actual):
            for key in act_row:
                if 'Date/Time' not in key:
                    try:
                        p = float(pred_row[key])
                        a = float(act_row[key])
                        if key not in error:
                            error[key] = 0
                        if key not in count:
                            count[key] = 0
                        error[key] += (p - a)**2
                        count[key] += 1
                    except TypeError, ValueError:
                        pass
        error = {k:math.sqrt(error[k] / float(count[k])) for k in error}
        return error

    logger = logging.getLogger('autotune')
    logger.addHandler(logs.NullHandler())

    eplus_params = args['eplus']
    eplus_weather = eplus_params['weather']
    eplus_model = eplus_params['model']
    user_data = eplus_params['userdata']
    eplus_schedule = eplus_params.setdefault('schedule', None)
    eplus_tune_keys = eplus_params.setdefault('tunekeys', None)
    
    if eplus_schedule is not None:
        eplus_schedule = [(eplus_schedule, os.path.split(eplus_schedule)[1])]
    
    WORST_FITNESS = float('inf') 
    fitness = WORST_FITNESS
    constraints = [candidate.evaluate_constraint(group) for group in candidate]
    if not all(constraints):
        constraints_failed = [candidate.get_variable(group).constraint.constraint for constraint, group in zip(constraints, candidate) if not constraint]
        fitness = len(constraints_failed) * 10000000000.0
        logger.debug('evaluator() :: {} constraints failed. The candidate is {} and the failed constraints are {}.'.format(len(constraints_failed), 
                                                                                                                           str(candidate), 
                                                                                                                           str(constraints_failed)))
    else:
        candidate_idf = None
        with open(eplus_model) as mfile:
            candidate_idf = idf.IDFFile(mfile)
            candidate_idf = candidate.values_to_idf(candidate_idf)
        cfile, candidate_filepath = tempfile.mkstemp(suffix='.{0}.idf'.format(str(id(threading.current_thread))), dir=eplus_params['output_directory'])
        os.write(cfile, str(candidate_idf))
        os.close(cfile)
        runner = eplus.EnergyPlus()
        eplus_data = runner.run(candidate_filepath, eplus_weather, eplus_schedule, eplus_params['output_directory'])
        if eplus_data is None or user_data is None: 
            if eplus_data is None:
                logger.error('evaluator() :: EnergyPlus output is None.')
            elif user_data is None:
                logger.error('evaluator() :: User data is None.')
            fitness = WORST_FITNESS
        else:
            ep = utilities.column_vectors(eplus_data)
            ud = utilities.column_vectors(user_data)
            errors = {}
            for key in ud:
                if 'Date/Time' not in key:
                    errors[key] = metrics.rmse(ep[key], ud[key])
            if eplus_tune_keys is None or len(eplus_tune_keys) == 0:
                fitness = sum([errors[k] for k in errors if errors[k] is not None])
            else:
                fitness = 0
                for k in eplus_tune_keys:
                    k = k.strip()
                    try:
                        fitness += errors[k]
                    except KeyError:
                        logger.warning('evaluator() :: Tune key {} does not exist in model output.'.format(k))
                    except TypeError:
                        logger.warning('evaluator() :: Tune key {} has error value None and is excluded from fitness.'.format(k))
        try:
            os.remove(candidate_filepath)
        except:
            pass    
            
    return fitness

def observer(population, num_generations, num_evaluations, args):
    stats = inspyred.ec.analysis.fitness_statistics(population)
    worst_fit = '{0:0.5}'.format(stats['worst'])
    best_fit = '{0:0.5}'.format(stats['best'])
    avg_fit = '{0:0.5}'.format(stats['mean'])
    med_fit = '{0:0.5}'.format(stats['median'])
    std_fit = '{0:0.5}'.format(stats['std'])
            
    print('Generation Evaluation      Worst       Best     Median    Average    Std Dev')
    print('---------- ---------- ---------- ---------- ---------- ---------- ----------')
    print('{0:>10} {1:>10} {2:>10} {3:>10} {4:>10} {5:>10} {6:>10}\n'.format(num_generations, 
                                                                             num_evaluations, 
                                                                             worst_fit, 
                                                                             best_fit, 
                                                                             med_fit, 
                                                                             avg_fit, 
                                                                             std_fit))
    population.sort(reverse=True)
    print('{0}'.format(population[0]))



