import csv
import eplus
import idf
import idfxml
import metrics
import multiprocessing
import os
import random
import shutil
import tempfile
import threading
import xml.etree.ElementTree

def random_model(basexml, randomxml):
    basexmlstr = None
    with open(basexml) as basexmlfile:
        basexmlstr = basexmlfile.read()
    varset = idfxml.xml_to_variables(basexmlstr)
    candidate = eplus.EPlusCandidate(varset)
    randcand = candidate.permutation()
    baseidf = idfxml.xml_to_idf(basexmlstr)
    randidf = randcand.values_to_idf(baseidf)
    randomxmlstr = idfxml.idf_to_xml(randidf)
    randomxmlstr = idfxml.variables_to_xml(varset, randomxmlstr)
    with open(randomxml, 'w') as randfile:
        randfile.write(randomxmlstr)
    
def autocreate_model(basexml, weather, randomxml='random.xml', schedule=None):
    randompath = os.path.split(os.path.abspath(randomxml))[0]
    found = False
    while not found:
        random_model(basexml, randomxml)
        randomxmlstr = None
        with open(randomxml) as randomxmlfile:
            randomxmlstr = randomxmlfile.read()
        idf = idfxml.xml_to_idf(randomxmlstr)
        idfname = '{}.idf'.format(randomxml)
        with open(idfname, 'w') as idffile:
            idffile.write(str(idf))
        if schedule is not None:
            schedule = [(schedule, os.split(schedule)[1])]
        runner = eplus.EnergyPlus()
        results = runner.run(idfname, weather, 
                             supplemental_files=schedule, 
                             working_directory=randompath)
        if results is not None:
            found = True
            try:
                os.remove(idfname)
            except:
                pass
            return results
    
def pull_tune_variables(targetxml, referencexml=None):
    refxml = targetxml
    if referencexml is not None:
        refxml = referencexml
    
    variables = None
    with open(refxml) as rfile:
        refxmlstr = rfile.read()
        variables = idfxml.xml_to_variables(refxmlstr)
    
    if referencexml is not None:
        xmlroot = xml.etree.ElementTree.parse(targetxml)
        for variable in variables:
            if variable.idfobject == variable.idfclass:
                node = xmlroot.find('./{0}/{1}'.format(idfxml.tagconvert(variable.idfclass), 
                                                       idfxml.tagconvert(variable.idffield)))
            else:
                nodes = xmlroot.findall('./{0}'.format(idfxml.tagconvert(variable.idfclass)))
                node = None
                for n in nodes:
                    name = n.find('./Name')
                    if name is not None and name.text.strip() == variable.idfobject:
                        node = n.find('./{0}'.format(idfxml.tagconvert(variable.idffield)))
                        break
            if node is not None:
                variable.value = node.text.strip()
    return variables
    
    
def input_metrics(targetxml, referencexml):
    rvars = pull_tune_variables(referencexml)
    tvars = pull_tune_variables(targetxml, referencexml)
    rvars.variables.sort(key=lambda x: x.group)
    tvars.variables.sort(key=lambda x: x.group)
    data = {'target': [], 'reference': [], 'min': [], 'max': [], 'key': []}
    for r, t in zip(rvars.variables, tvars.variables):
        if r.group == t.group:
            key = ';'.join([r.idfclass, r.idfobject, r.idffield])
            data['target'].append(float(t.value))
            data['reference'].append(float(r.value))
            data['min'].append(r.minimum)
            data['max'].append(r.maximum)
            data['key'].append(key)
    paes = metrics.pae(data['target'], data['reference'], data['min'], data['max'])
    m = {'pae': {},
         'rmse': {},
         'cvrmse': {},
         'mbe': {},
         'nmbe': {},
         'mape': {}}
    for k, p in zip(data['key'], paes):
        m['pae'][k] = p
    m['rmse']['all inputs'] = metrics.rmse(data['target'], data['reference'])
    m['cvrmse']['all inputs'] = metrics.cvrmse(data['target'], data['reference'])
    m['mbe']['all inputs'] = metrics.mbe(data['target'], data['reference'])
    m['nmbe']['all inputs'] = metrics.nmbe(data['target'], data['reference'])
    m['mape']['all inputs'] = metrics.mape(data['target'], data['reference'])
    return m
    

def output_metrics(estresults, actresults):
    m = {'rmse': {},
         'cvrmse':{}, 
         'mbe': {},
         'nmbe':{},
         'mape': {}}
    estres = column_vectors(estresults)
    actres = column_vectors(actresults)
    for col in actres:
        try:
            m['rmse'][col] = metrics.rmse(estres[col], actres[col])
            m['cvrmse'][col] = metrics.cvrmse(estres[col], actres[col])
            m['mbe'][col] = metrics.mbe(estres[col], actres[col])
            m['nmbe'][col] = metrics.nmbe(estres[col], actres[col])
            m['mape'][col] = metrics.mape(estres[col], actres[col])
        except:
            # If anything crashes it here, just ignore the column in the output.
            pass
    return m

def column_vectors(list_of_dicts):
    allkeys = set()
    for row in list_of_dicts:
        allkeys |= set(list(row.keys()))
    dict_of_lists = {}
    for k in allkeys:
        dict_of_lists[k] = []
    for row in list_of_dicts:
        for k in row:
            dict_of_lists[k].append(row[k])
    return dict_of_lists
    
def run_eplus(model, weather, schedule=None):
    if schedule is not None:
        schedule = [(schedule, os.path.split(schedule)[1])]
    runner = eplus.EnergyPlus()
    results = runner.run(model, weather, schedule)
    if results is not None:
        directory, model_filename = os.path.split(model)
        rfilename = os.path.splitext(model_filename)[0] + '.csv'
        with open(os.path.join(directory, rfilename), 'wb') as resultsfile:
            resultsfile.write(str(results))
        return True
    else:
        return False

def run_eplus_batch(models, weather, schedule=None, nprocs=None):
    if nprocs is None:
        nprocs = min(len(models), multiprocessing.cpu_count())
    pool = multiprocessing.Pool(processes=nprocs)
    results = [pool.apply_async(run_eplus, (model, weather, schedule)) for model in models]
    pool.close()
    pool.join()
    success = [r.get() for r in results]
    return success
    
def models_from_inspyred(inspyred_filename, basemodel_filename, parameter_filename):
    models = []
    variables = None
    with open(parameter_filename) as pfile:
        reader = csv.DictReader(pfile)
        variables = eplus.EPlusVariableSet(reader)
    candidates = []
    with open(inspyred_filename) as ifile:
        lines = ifile.readlines()
        last_gen = int(lines[-1].split(',')[0])
        for line in reversed(lines):
            parts = line.split(',')
            gen = int(parts[0])
            if gen == last_gen:
                num = int(parts[1])
                fit = float(parts[2])
                candidate = [float(p.replace('[', '').replace(']', '').strip()) for p in parts[3:]]
                candidates.append((candidate, num))
            else:
                break
    candidates.sort(key=lambda x: x[1])
    candidates = [c[0] for c in candidates]
    for candidate in candidates:
        model = idf.IDFFile(open(basemodel_filename))
        for i, variable in enumerate(variables):
            model.update(variable.idfclass, variable.idfobject, variable.idffield, candidate[i])
        models.append(model)
    return models
    
def post_average(inspyred_filename, basemodel_filename, parameter_filename):
    variables = None
    with open(parameter_filename) as pfile:
        reader = csv.DictReader(pfile)
        variables = eplus.EPlusVariableSet(reader)
    mean_candidate = [0 for _ in range(len(variables))]
    num_candidates = 0
    with open(inspyred_filename) as ifile:
        lines = ifile.readlines()
        last_gen = int(lines[-1].split(',')[0])
        for line in reversed(lines):
            parts = line.split(',')
            gen = int(parts[0])
            if gen == last_gen:
                candidate = [float(p.replace('[', '').replace(']', '').strip()) for p in parts[3:]]
                for i, c in enumerate(candidate):
                    mean_candidate[i] += c
                num_candidates += 1
            else:
                break
    mean_candidate = [c / float(num_candidates) for c in mean_candidate]
    candidate = eplus.EPlusCandidate(variables)
    candidate.set_values(mean_candidate)
    model = None
    with open(basemodel_filename) as bfile:
        model = idf.IDFFile(bfile)
    model = candidate.values_to_idf(model)
    return model
        

if __name__ == '__main__':
    d = 'C:/Users/agarrett/Downloads/temp'
    import logging
    logger = logging.getLogger('eplus')
    logger.setLevel(logging.DEBUG)
    logging_filehandler = logging.FileHandler(os.path.join(d, 'eplus.log'))
    logging_filehandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(logging_filehandler)

    r = autocreate_model(os.path.join(d, 'WarehouseBase.xml'), 
                         os.path.join(d, 'weather.epw'), 
                         randomxml=os.path.join(d, 'WarehouseSubmission.xml'))
    with open(os.path.join(d, 'WarehouseResults.csv'), 'wb') as rfile:
        rfile.write(str(r))
        
        