#!/usr/bin/env python

#===  Autotune Library  ===#
import eplus
import idf
import logs
import operators
#==========================#
import copy
import csv
import difflib        
import inspyred
import logging
import os
import random
import shutil
import tempfile
import threading
import time


def gather_all_parameters(model_filename, param_filename, percent_varied=0.1):
    def find_matching_group(current_parameters, new_identifier):
        matches = []
        for p in current_parameters:
            old_identifier = p['Class'] + p['Object'] + p['Field']
            d = difflib.SequenceMatcher(a=old_identifier, b=new_identifier)
            if d.ratio() > 0.98:
                matches.append((d.ratio(), p['Group']))
        matches.sort(key=lambda x: x[0], reverse=True)
        if len(matches) == 0:
            return ''
        else:
            return matches[0][1]

    with open(model_filename) as idfmodel, open(param_filename, 'w') as paramfile:
        idffile = idf.IDFFile(idfmodel)
        params = []
        group_number = 1
        for object in idffile.idf:
            class_name = object[0]
            object_name_index = idffile.idd.get_field_index(class_name, 'Name')
            object_name = object[object_name_index] if object_name_index is not None else class_name
            fields = idffile.idd.get_fields(class_name)
            field_names = [f.name for f in fields] if fields is not None else []
            for field, field_value, field_name in zip(fields, object[1:], field_names):
                try:
                    if (field.type == 'real' or field.type == 'integer') and len(field_value.strip()) > 0 and \
                       'DesignDay' not in class_name and 'Curve:' not in class_name and 'RunPeriod' not in class_name and \
                       'Schedule:Year' not in class_name and 'North Axis' not in field_name and float(field_value) != 0 and \
                       'Vertex' not in field_name and 'Sequence' not in field_name and 'Timestep' not in class_name:
                        p = {}
                        p['Class'] = class_name
                        p['Object'] = object_name
                        p['Field'] = field_name
                        p['Default'] = field_value
                        p['Minimum'] = float(field_value) * (1 - percent_varied) 
                        p['Maximum'] = float(field_value) * (1 + percent_varied)
                        if float(field_value) < 0:
                            p['Minimum'], p['Maximum'] = p['Maximum'], p['Minimum']
                        p['Type'] = 'Float' if field.type == 'real' else 'Integer'
                        if field.minimum is not None:
                            p['Minimum'] = max(float(field.minimum), p['Minimum'])
                        if field.maximum is not None:
                            p['Maximum'] = min(float(field.maximum), p['Maximum'])
                        
                        p['Group'] = 'G{:03d}'.format(group_number)
                        g = find_matching_group(params, class_name + object_name + field_name)
                        if len(g) > 0:
                            p['Group'] = g
                        else:
                            p['Group'] = 'G{:03d}'.format(group_number)
                            group_number += 1
                        params.append(p)
                except ValueError:
                    pass
        pcsv = csv.DictWriter(paramfile, ['Class', 'Object', 'Field', 'Default', 'Minimum', 'Maximum', 'Type', 'Group'], lineterminator='\n')
        pcsv.writeheader()
        pcsv.writerows(params)
        

def autotune(model_filepath, param_filepath, udata_filepath, weath_filepath, 
             sched_filepath=None, workingdir=None, psize=16, tsize=4, 
             mutation_rate=0.1, mean_variation_rate=0, ncpus=4, seed=None,
             maxevals=1024, maxtime=43200, tunekeys=None, verbose=True):
    logger = logging.getLogger('autotune')
    logger.addHandler(logs.NullHandler())
    if workingdir is None:
        output_dir = tempfile.mkdtemp(prefix='tmp', suffix='.%s' % str(id(threading.current_thread)))
    else:
        output_dir = workingdir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    runner = eplus.EnergyPlus()
    model_path, model_filename = os.path.split(model_filepath)
    param_path, param_filename = os.path.split(param_filepath)
    udata_path, udata_filename = os.path.split(udata_filepath)
    weath_path, weath_filename = os.path.split(weath_filepath)
    shutil.copy(model_filepath, os.path.join(output_dir, model_filename))
    shutil.copy(param_filepath, os.path.join(output_dir, param_filename))
    shutil.copy(udata_filepath, os.path.join(output_dir, udata_filename))
    shutil.copy(weath_filepath, os.path.join(output_dir, weath_filename))
    if sched_filepath is not None:
        sched_path, sched_filename = os.path.split(sched_filepath)
        shutil.copy(sched_filepath, os.path.join(output_dir, sched_filename))
        sched_filepath = os.path.join(output_dir, sched_filename)
    
    with open(os.path.join(output_dir, udata_filename)) as udata_file:
        userdata = eplus.EPlusResults(udata_file).results

    if seed is None:
        rand_seed = time.time()
    else:
        rand_seed = seed
    rand = random.Random()
    rand.seed(rand_seed)
    logger.info('autotune() :: Random seed used was {}.'.format(rand_seed))
    
    with open(os.path.join(output_dir, param_filename)) as paramfile:
        variables = eplus.EPlusCandidate(eplus.EPlusVariableSet(csv.DictReader(paramfile)))
    seedvars = copy.deepcopy(variables)
    seedvars.set_values([seedvars.get_variable(group).default for group in seedvars])
    seeds = [seedvars]
    logger.info('autotune() :: Using {} seed candidates.'.format(len(seeds)))
    
    ec = inspyred.ec.EvolutionaryComputation(rand)
    ec.observer = [inspyred.ec.observers.file_observer]
    ec.terminator = [inspyred.ec.terminators.time_termination, inspyred.ec.terminators.evaluation_termination]
    ec.selector = inspyred.ec.selectors.tournament_selection
    ec.replacer = inspyred.ec.replacers.steady_state_replacement 
    ec.variator = [operators.crossover, operators.mutator, operators.mean_variation]
    if verbose:
        ec.observer.append(inspyred.ec.observers.stats_observer)
        ec.terminator.append(inspyred.ec.terminators.user_termination)
    sfile = open(os.path.join(output_dir, 'stat.csv'), 'w')
    ifile = open(os.path.join(output_dir, 'inds.csv'), 'w')
    final_pop = ec.evolve(generator=operators.generator,
                          evaluator=inspyred.ec.evaluators.parallel_evaluation_mp,
                          bounder=operators.bounder, 
                          seeds=seeds,
                          max_time=maxtime,
                          max_evaluations=maxevals,
                          pop_size=psize,
                          mp_evaluator=operators.evaluator,
                          mp_nprocs=ncpus,
                          maximize=False,
                          num_selected=tsize, 
                          tournament_size=tsize,
                          mutation_usage_rate=1,
                          mutation_rate=mutation_rate,
                          crossover_rate=1,
                          mean_variation_rate=mean_variation_rate,
                          start_time = time.time(),
                          statistics_file=sfile,
                          individuals_file=ifile,
                          
                          # E+/Autotune specific arguments
                          eplus={'variables': variables,
                                 'model': os.path.join(output_dir, model_filename),
                                 'weather': os.path.join(output_dir, weath_filename),
                                 'schedule': sched_filepath,
                                 'tunekeys': tunekeys,
                                 'output_directory': output_dir,
                                 'userdata': userdata})
    
    sfile.close()
    ifile.close()
    
    for i, p in enumerate(reversed(sorted(final_pop))):
        with open(os.path.join(output_dir, model_filename)) as basefile:
            ifile = idf.IDFFile(basefile)
            ifile = p.candidate.values_to_idf(ifile)
            with open(os.path.join(output_dir, 'final_{:03d}.idf'.format(i+1)), 'w') as mfile:
                mfile.write(str(ifile))

    if ec.termination_cause != 'user_termination':
        return True
    else:
        return False
    
    
'''****************************************************************************
****************************     Main Script     ******************************
****************************************************************************'''
def main():
    import argparse
    import getpass
    parser = argparse.ArgumentParser(description='runs the autotune process',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('model', help='the model file to tune (IDF)')
    parser.add_argument('parameters', help='the tuning parameters (CSV)')
    parser.add_argument('userdata', help='the utility data against which to tune (CSV)')
    parser.add_argument('weather', help='the weather location/filename (EPW)')
    parser.add_argument('--tunekeys', help='the keys (column names) in the user data to use for tuning (defaults to all)', nargs='+', default=None)
    parser.add_argument('--schedule', help='the schedule file (CSV)', default=None)
    parser.add_argument('--workingdir', help='the working directory for autotune', default='output')
    parser.add_argument('--loglevel', help='the lowest level (debug, info, warning, error) at which to log events', default='info')
    parser.add_argument('--numcpus', help='the number of CPUs that autotune should use', type=int, default=4)
    parser.add_argument('--popsize', help='the population size for autotune', type=int, default=16)
    parser.add_argument('--tournsize', help='the tournament size for autotune', type=int, default=4)
    parser.add_argument('--mutrate', help='the mutation rate for autotune', type=float, default=0.1)
    parser.add_argument('--mvrate', help='the mean variation rate for autotune', type=float, default=0)
    parser.add_argument('--maxevals', help='the maximum number of fitness evaluations allowed for a job', type=int, default=1024)
    parser.add_argument('--maxtime', help='the maximum time allowed for a job (in seconds)', type=int, default=43200) # 12 hours
    parser.add_argument('--prngseed', help='the seed for the random number generator', type=int, default=None)
    args = parser.parse_args()

    verbose = True
    alogger = logging.getLogger('autotune')
    elogger = logging.getLogger('eplus')
    ilogger = logging.getLogger('inspyred.ec')
    if 'debug' in args.loglevel:
        alogger.setLevel(logging.DEBUG)
        elogger.setLevel(logging.DEBUG)
        ilogger.setLevel(logging.DEBUG)
    elif 'info' in args.loglevel:
        alogger.setLevel(logging.INFO)
        elogger.setLevel(logging.INFO)
        ilogger.setLevel(logging.INFO)
    elif 'warning' in args.loglevel:
        alogger.setLevel(logging.WARNING)
        elogger.setLevel(logging.WARNING)
        ilogger.setLevel(logging.WARNING)
        verbose = False
    elif 'error' in args.loglevel:
        alogger.setLevel(logging.ERROR)
        elogger.setLevel(logging.ERROR)
        ilogger.setLevel(logging.ERROR)
        verbose = False
    logging_filehandler = logging.FileHandler('autotune.log')
    logging_filehandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    alogger.addHandler(logging_filehandler)
    elogger.addHandler(logging_filehandler)
    ilogger.addHandler(logging_filehandler)

    autotune(args.model, args.parameters, args.userdata, args.weather, sched_filepath=args.schedule, 
             workingdir=args.workingdir, psize=args.popsize, tsize=args.tournsize, 
             mutation_rate=args.mutrate, mean_variation_rate=args.mvrate, ncpus=args.numcpus, seed=args.prngseed,
             maxevals=args.maxevals, maxtime=args.maxtime, tunekeys=args.tunekeys, verbose=verbose)

             
if __name__ == '__main__':
    main()
    #gather_all_parameters('bldg3147_v7_as.idf', 'garrett.csv')
            
