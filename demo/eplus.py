#===  Autotune Library  ===#
import logs
#==========================#
import copy
import csv
import logging
import os
import random
import shutil
import string
import StringIO
import sys
import subprocess
import tempfile
import threading


class EnergyPlus(object):
    """Represents the Energy Plus command-line software.
    
    This class provides a consistent interface to the Energy Plus
    software. With it, command-line processes can be run on IDF
    files and their results can be processed. Instantiating
    this class requires specification of the EPlus runner program,
    postprocess program, and data definition file.
    
    For the Windows and Ubuntu operating systems, the following 
    instantiations should work for default Energy Plus installations:
    
    eplus_ubuntu  = EnergyPlus("/usr/local/bin/energyplus", 
                               "/usr/local/bin/runreadvars", 
                               "/usr/local/EnergyPlus-7-0-0/Energy+.idd")
    eplus_windows = EnergyPlus("C:\\EnergyPlus-7-0-0\\EnergyPlus.exe", 
                               "C:\\EnergyPlusV7-0-0\\PostProcess\\ReadVarsESO.exe", 
                               "C:\\EnergyPlus-7-0-0\\Energy+.idd")
    
    """
    
    def __init__(self, runner=None, postprocessor=None, iddfile=None):
        if sys.platform == 'win32':
            if runner is None:
                runner = 'C:\\EnergyPlusV7-0-0\\EnergyPlus.exe'
            if postprocessor is None:
                postprocessor = 'C:\\EnergyPlusV7-0-0\\PostProcess\\ReadVarsESO.exe'
            if iddfile is None:
                iddfile = 'C:\\EnergyPlusV7-0-0\\Energy+.idd'
        elif sys.platform == 'linux2':
            if runner is None:
                runner = '/usr/local/bin/energyplus'
            if postprocessor is None:
                postprocessor = '/usr/local/bin/runreadvars'
            if iddfile is None:
                iddfile = '/usr/local/EnergyPlus-7-0-0/bin/Energy+.idd'
        else:
            raise OSError('Unsupported Platform')
        self.runner = runner
        self.postprocessor = postprocessor
        self.iddfile = iddfile
        
    def run(self, model_filename, weather_filename, 
            supplemental_files=None, working_directory=None):
        """Run Energy Plus on the specified model file.
        
        This function runs the Energy Plus command-line script on the
        given IDF model and EPW weather files. If specified, the `supplemental_files`
        should be a list of tuples of the form [(srcfilename, dstfilename),...].
        The srcfilename should be the location of the supplemental file, and the
        dstfilename should be what that file should be called in the EnergyPlus
        running directory. (This is useful for schedule files which may have
        hard-coded names in a model file.)
        
        The function returns an EPlusResults object for the results
        if the Energy Plus simulation could be executed and None otherwise.
        
        """
        logger = logging.getLogger('eplus')
        logger.addHandler(logs.NullHandler())
        if (self.runner is not None and self.postprocessor is not None and 
            self.iddfile is not None and os.path.isfile(self.runner) and 
            os.path.isfile(self.postprocessor) and os.path.isfile(self.iddfile)):
            if working_directory is None:
                working_directory = os.getcwd()
            elif not os.path.isabs(working_directory):
                working_directory = os.path.join(os.getcwd(), working_directory)
            if not os.path.exists(working_directory):
                os.makedirs(working_directory)
            output_directory = tempfile.mkdtemp(suffix='.%s' % str(id(threading.current_thread)), dir=working_directory)
            shutil.copy(self.iddfile, os.path.join(output_directory, 'Energy+.idd'))
            shutil.copy(weather_filename, os.path.join(output_directory, 'in.epw'))
            if model_filename is not None and os.path.exists(model_filename):
                shutil.copy(model_filename, os.path.join(output_directory, 'in.idf'))
            if supplemental_files is not None:
                for (srcfilename, dstfilename) in supplemental_files:
                    dstbasename = os.path.basename(dstfilename)
                    if os.path.exists(srcfilename):
                        shutil.copy(srcfilename, os.path.join(output_directory, dstbasename))
                
            if os.path.isfile(model_filename) and os.path.isfile(weather_filename):
                previous_dir = os.getcwd()
                os.chdir(output_directory)
                p = subprocess.Popen([self.runner], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                logger.debug('EnergyPlus.run() :: The runner stdout was \n{0}'.format(stdout.strip()))
                logger.debug('EnergyPlus.run() :: The runner stderr was \n{0}'.format(stderr.strip()))
                # The post-processing script on Linux works differently and requires
                # the filename. The Windows batch file will allow arguments, but
                # they are variable names to be collected instead of a filename.
                if sys.platform == 'linux2':
                    ppargs = [self.postprocessor, 'eplusout.eso']
                else:
                    ppargs = [self.postprocessor]
                p = subprocess.Popen(ppargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                logger.debug('EnergyPlus.run() :: The postprocess stdout was \n{0}'.format(stdout.strip()))
                logger.debug('EnergyPlus.run() :: The postprocess stderr was \n{0}'.format(stderr.strip()))
                results = None
                errtext = ''
                # Load the err file and see if there was a fatal error.
                with open(os.path.join(output_directory, 'eplusout.err')) as errfile:
                    errtext = errfile.read()
                if ' Fatal ' in errtext:
                    logger.error('EnergyPlus.run() :: The model file {0} produced errors.'.format(model_filename))
                    logger.error('EnergyPlus.run() :: The error file contained \n{0}'.format(errtext.strip()))
                else:
                    results_filename = os.path.join(output_directory, 'eplusout.csv')
                    with open(results_filename, 'r') as resultsfile:
                        results = EPlusResults(resultsfile)
                        
                os.chdir(previous_dir)
                try:
                    shutil.rmtree(output_directory)
                except:
                    pass
                return results                    
            elif not os.path.isfile(model_filename):
                logger.error('EnergyPlus.run() :: The file {0} does not exist.'.format(model_filename))
                return None
            else:
                logger.error('EnergyPlus.run() :: The file {0} does not exist.'.format(weather_filename))
                return None                
        else:
            logger.error('EnergyPlus.run() :: The EnergyPlus configuration (installation directory, etc.) is not valid.')
            return None


            
class EPlusVariable(object):
    def __init__(self, idfclass=None, idfobject=None, idffield=None, default=None, minimum=None, maximum=None, distribution=None, type=None):
        self.idfclass = idfclass
        self.idfobject = idfobject
        self.idffield = idffield
        if type is not None:
            self.type = type.lower()    # 'float' or 'integer'
            if self.type == 'integer':
                self.default = int(default)
                self.minimum = int(minimum)
                self.maximum = int(maximum)
            elif self.type == 'float':
                self.default = float(default)
                self.minimum = float(minimum)
                self.maximum = float(maximum)
        else:
            self.type = type
            self.default = default
            self.minimum = minimum
            self.maximum = maximum
        self.distribution = distribution.lower() if distribution is not None else distribution
        self.group = None
        self.constraint = None
        self.value = self.default

    def get_random_value(self, random):
        # Need to consider the distribution here.
        if self.type == 'integer':
            return random.randint(self.minimum, self.maximum)
        else: # self.type == 'float'
            return random.uniform(self.minimum, self.maximum)
        
    def get_center(self):
        if self.type == 'integer':
            return int((self.maximum + self.minimum) / 2.0)
        else: # self.type == 'float':
            return (self.maximum + self.minimum) / 2.0
            
    def __str__(self):
        return '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}'.format(self.idfclass, self.idfobject, self.idffield, self.default, 
                                                                               self.minimum, self.maximum, self.distribution, self.type, 
                                                                               self.group, self.constraint, self.value)

    def __repr__(self):
        return str(self)


class EPlusConstraint(object):
    """Represents a complex constraint on EnergyPlus variable values.
    
    This class defines a constraint on the variables in an EnergyPlus candidate.
    These constraints are complex in that they have interaction with other
    variables. Simple constraints, such as the variable being within some legal 
    range, are handled using the minimum and maximum values for the variable.
    A constraint is essentially an expression of inequality (< or <=) that 
    contains variable names (group names for the E+ variables).
    
    """
    def __init__(self, constraint=''):
        comparators = ['>=', '<=', '>', '<']
        operators = ['+', '-', '*', '/']
        self.EPSILON = 0.0000000001
        self.constraint = constraint.strip()
        self.variables = []
        self.comparator = None
        self.lhs = None
        self.rhs = None
        # Because of the pain of having to deal with both >= and >,
        # we can simply rely on the fact that any legitimate constraint
        # will only have ONE of those.
        for c in comparators:
            s = self.constraint.replace(c, ' {0} '.format(c))
            if len(s) != len(self.constraint):
                self.constraint = s;
                break
        for o in operators:
            self.constraint = self.constraint.replace(o, ' {0} '.format(o))
        self.constraint = ' '.join(self.constraint.split())
        parts = self.constraint.split()
        if len(parts) > 0:
            for p in parts:
                if p[0] in string.lowercase or p[0] in string.uppercase:
                    self.variables.append(p)
                elif p in comparators:
                    self.comparator = p
            sides = self.constraint.split(self.comparator)
            self.lhs = sides[0].strip()
            self.rhs = sides[1].strip()
                
    def is_valid(self):
        """Determines whether the constraint is valid (i.e., is well-formed).
        
        This method returns True if the constraint is valid. Validity here
        means that the constraint is a well-formed inequality in that it
        contains variable names and a comparator.
        
        """
        return self.constraint is not None and len(self.constraint) > 0 and len(self.variables) > 0 and self.comparator is not None
            
    def __str__(self):
        if self.is_valid():
            return self.constraint
        else:
            return ''
        
    def __repr__(self):
        return str(self)
        
            
class EPlusCandidate(object):
    """Represents an EnergyPlus candidate.
    
    This class defines a candidate solution. Each candidate is essentially a
    dictionary of lists of EnergyPlus variables keyed to their group names.
    For instance, if there were 5 variables and 3 groups, the candidate might
    look like the following:
    
    {'grp1': [var1], 'grp2': [var2, var4], 'grp3': [var3, var5]}
    
    Variables in the same group have exactly the same values. As far as the 
    evolutionary computation is concerned, the groups are the candidate components.
    The class provides methods for retrieving and storing only the variable values 
    (as a list in ascending order by group name), as well as for evaluating any
    constraints on the variables.
    
    The __iter__ method is overridden in this class, which allows a user to create
    code such as the following:
    
    for group in candidate:
        var = candidate.get_variable(group)
    
    """
    def __init__(self, variables):
        """Constructs a candidate solution from a list of EPlusVariable objects.
        
        This constructor accepts a list of EnergyPlus variables and creates a 
        dictionary of those variables keyed to their groups.
        
        """
        self.variables = {}
        for variable in variables:
            newvar = copy.deepcopy(variable)
            if variable.group not in self.variables:
                self.variables[variable.group] = [newvar]
            else:
                self.variables[variable.group].append(newvar)
                
    def __iter__(self):
        return iter(sorted(self.variables))
    
    def _evaluate(self, expression, variables):
        # Remove the variables before we assign.
        for varname in variables:
            try:
                exec('del {0}'.format(varname))
            except NameError:
                pass
        for varname in variables:
            exec('{0} = {1}'.format(varname, variables[varname]))
        result = eval(expression)
        # Remove the variables after we're done.
        for varname in variables:
            exec('del {0}'.format(varname))
        return result        
    
    def get_variable(self, group):
        """Returns the representative variable for the group.
        
        If a group contains more than one variable, only the first is
        returned.
        
        """
        return self.variables[group][0]
    
    def get_value(self, group):
        """Returns the representative value for the group.

        If a group contains more than one variable, only the first 
        variable's value is returned.
        
        """
        return self.variables[group][0].value
                
    def set_value(self, group, value):
        """Sets all variables in the group to the specified value.

        """
        for i, v in enumerate(self.variables[group]):
            self.variables[group][i].value = value
            
    def get_constraint_order(self):
        """Returns a list of the groups in the candidate in ascending order of range.
        
        This method returns a list of the groups (keys) in the candidate,
        sorted by the flexibility of their constraints. Variables that appear
        in many constraints should be higher in the order than those in fewer
        constraints. Likewise, variables with small ranges should appear 
        higher in the order than those with large ranges.
        
        """    
        constraint_count = {}
        for g in sorted(self.variables):
            constraint_count[g] = 0
        for group in sorted(self.variables):
            variable = self.get_variable(group)
            if variable.constraint is not None:
                for cvar in variable.constraint.variables:
                    if cvar in constraint_count:
                        constraint_count[cvar] += 1
        order = []
        for group in sorted(self.variables):
            variable = self.get_variable(group)
            range = variable.maximum - variable.minimum
            order.append((group, constraint_count[group], range))
        order.sort(key=lambda x: x[2])
        order.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in order]
    
    def get_constrained_bounds(self, group):
        """Returns the current bounds for a given variable group's constraints.
        
        This method returns a (min, max) tuple representing the bounds for a
        given variable group. The reason this method is included is because,
        during constraint evaluation, the setting of one variable's value will
        likely impact the actual range of another constrained variable. This
        method, when paired with the get_constraint_order method, can be called 
        before each variable group is set.
        
        """
        variable = self.get_variable(group)
        constraint = variable.constraint
        if constraint.is_valid():
            var_dict = {}
            for varname in constraint.variables:
                var_dict[varname] = self.get_value(varname)
            var_dict[variable.group] = variable.minimum
            remainder = self._evaluate(constraint.lhs, var_dict) - self._evaluate(constraint.rhs, var_dict)
            var_dict[variable.group] = variable.maximum
            sign_check = self._evaluate(constraint.lhs, var_dict) - self._evaluate(constraint.rhs, var_dict)
            
            # So we now have our free variable X along with a vector of 
            # other variables V, and we know that Xmin + REMAINDER + V = 0.
            # So if we require that Xmin + REMAINDER + V < 0, then X can
            # at most be Xmin + REMAINDER.
            # But what if it's -Xmin + REMAINDER + V = 0?
            # In that case, if we require that -Xmin + REMAINDER + V < 0,
            # then X must be at least Xmin + REMAINDER.
            if sign_check < remainder:
                # We have a negative sign on the free variable.
                new_bounds = (remainder + variable.minimum, variable.maximum)
            else:
                # We have a positive sign on the free variable.
                new_bounds = (variable.minimum, variable.minimum - remainder)
            if '<=' in constraint.comparator:
                bounds = (max(variable.minimum, new_bounds[0]), min(variable.maximum, new_bounds[1]))
                return (min(bounds[0], variable.maximum), max(bounds[1], variable.minimum))
            elif '<' in constraint.comparator:
                bounds = (max(variable.minimum, new_bounds[0] + constraint.EPSILON), min(variable.maximum, new_bounds[1] - constraint.EPSILON))
                return (min(bounds[0], variable.maximum), max(bounds[1], variable.minimum))
            else:
                raise NotImplementedError('{0} constraints are not currently supported.'.format(constraint.comparator))
        else:
            return (variable.minimum, variable.maximum)
        
    def evaluate_constraint(self, group):
        """Returns True if the constraint is currently satisfied for the specified group.
        
        """
        variable = self.variables[group][0]
        constraint = variable.constraint
        if constraint.is_valid():
            var_dict = {}
            for varname in constraint.variables:
                var_dict[varname] = self.get_value(varname)
            return self._evaluate(constraint.constraint, var_dict)
        else:
            return True
        
    def get_values(self):
        """Returns a group-sorted list of the variable values in the candidate.
        
        """
        vals = []
        for group in sorted(self.variables):
            vals.append(self.get_value(group))
        return vals
        
    def set_values(self, values):
        """Sets the variable values in the candidate according to the group-sorted list.
        
        """
        for val, group in zip(values, sorted(self.variables)):
            self.set_value(group, val)
        
    def permutation(self, prng=None):
        """Creates a new candidate that is a random permutation of the candidate.
        
        """
        if prng is None:
            prng = random
        perm = copy.deepcopy(self)
        groups = perm.get_constraint_order()
        for group in groups:
            variable = perm.get_variable(group)
            perm.set_value(group, variable.get_center())
        for group in groups:
            variable = perm.get_variable(group)
            lo, hi = perm.get_constrained_bounds(group)
            if variable.type == 'integer':
                perm.set_value(group, prng.randint(lo, hi))
            elif variable.type == 'float':
                perm.set_value(group, prng.uniform(lo, hi))
        return perm
        
    def values_from_idf(self, idffile):
        """Initializes the candidate with values from the IDFFile object.
        
        This method takes an IDFFile object representing an IDF file and
        initializes the values of the candidate to those pulled from the 
        IDFFile. The candidate must already exist before this method can
        be used. Remember that the actual candidate elements must come from
        a parameter file. Otherwise, this method would not know which values
        to pull from the IDFFile object.
        
        """
        for group in self.variables:
            for i, v in enumerate(self.variables[group]):
                val = idffile.find(v.idfclass, v.idfobject, v.idffield)
                self.variables[group][i].value = int(val) if v.type == 'integer' else float(val)
       
    def values_to_idf(self, idffile):
        """Loads the IDFFile object with the candidate's values and returns the modified IDFFile.
        
        This method takes an IDFFile object, makes a deep copy and replaces its 
        values with those from the candidate. The method returns the full, 
        modified IDFFile copy.
        
        """
        idffile = copy.deepcopy(idffile)
        for group in self.variables:
            for i, v in enumerate(self.variables[group]):
                idffile.update(v.idfclass, v.idfobject, v.idffield, str(v.value))
        return idffile
        
    def __str__(self):
        return str(self.get_values())
        
    def __repr__(self):
        return str(self)
        
        
class EPlusVariableSet(object):
    def __init__(self, param_iterable=None):
        self.load(param_iterable)

    def __iter__(self):
        return iter(self.variables)
        
    def __getitem__(self, i):
        return self.variables[i]

    def __setitem__(self, i, value):
        self.variables[i] = value
        
    def __len__(self):
        return len(self.variables)
        
    def load(self, param_iterable=None):
        self.variables = []
        if param_iterable is not None:
            group_num = 1
            for p in param_iterable:
                v = EPlusVariable(p['Class'], p['Object'], p['Field'], 
                                  p['Default'], p['Minimum'], p['Maximum'], 
                                  p['Distribution'], p['Type'])
                if 'Group' in p and len(p['Group'].strip()) > 0:
                    v.group = p['Group'].strip()
                else:
                    v.group = 'EnergyPlusGroup{0:03d}'.format(group_num)
                    group_num += 1
                if 'Constraint' in p and len(p['Constraint'].strip()) > 0:
                    v.constraint = EPlusConstraint(p['Constraint'].strip())
                else:
                    v.constraint = EPlusConstraint()
                self.variables.append(v)
        return self.variables
        
    def __str__(self):
        dicts = []
        for v in self.variables:
            d = {'Class': v.idfclass, 'Object': v.idfobject, 'Field': v.idffield,
                 'Default': v.default, 'Minimum': v.minimum, 'Maximum': v.maximum,
                 'Distribution': v.distribution, 'Type': v.type, 'Group': v.group,
                 'Constraint': v.constraint}
            dicts.append(d)
        for d in dicts:
            if 'EnergyPlusGroup' in d['Group']:
                d['Group'] = ''
        strfile = StringIO.StringIO()
        writer = csv.DictWriter(strfile, ['Class', 'Object', 'Field', 'Default', 
                                          'Minimum', 'Maximum', 'Distribution', 
                                          'Type', 'Group', 'Constraint'])
        writer.writeheader()
        writer.writerows(dicts)
        return strfile.getvalue()

class EPlusResults(object):
    def __init__(self, resultsfile):
        self.results = []
        self.load(resultsfile)
        
    def __iter__(self):
        return iter(self.results)
        
    def __getitem__(self, i):
        return self.results[i]

    def __setitem__(self, i, value):
        self.results[i] = value
        
    def __len__(self):
        return len(self.results)
        
    def load(self, resultsfile):
        self.results = []
        resultstr = resultsfile.read()
        resultcsv = csv.DictReader(resultstr.splitlines())
        for i, row in enumerate(resultcsv):
            r = {}
            for key in row:
                if 'Date/Time' in key:
                    r[key.strip()] = row[key].strip()
                else:
                    try:
                        r[key.strip()] = float(row[key])
                    except ValueError:
                        r[key.strip()] = None
            self.results.append(r)

    def __str__(self):
        strfile = StringIO.StringIO()
        header = ['Date/Time'] + [k for k in sorted(self.results[0]) if k != 'Date/Time']
        writer = csv.DictWriter(strfile, header)
        writer.writer.writerow(header)
        writer.writerows(self.results)
        return strfile.getvalue()
                

        
