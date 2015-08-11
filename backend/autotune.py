#!/usr/bin/env python

# This script relies on /etc/init/autotune.conf to keep it running
# in case of crashes.

import os
import copy
import csv
import datetime
from email.mime.text import MIMEText
import hashlib
import inspyred
import io
import itertools
import logging
import math    
import multiprocessing
import MySQLdb
import os
import pickle
import random
import re
import requests
import shutil
import smtplib
import string
import StringIO
import subprocess
import sys
import tempfile
import threading
import time
import zipfile

# Database login information
DBHOST = 'autotune_host'
DBUSER = 'autotune_user'
DBPASS = 'autotune_password'
DBNAME = 'autotune_db'
ERROR_DIRECTORY = os.getcwd()
SENDMAIL_SERVER = 'localhost'
SENDMAIL_USER = None
SENDMAIL_PASS = None
WEBSITE_URL = 'http://yourdomain.com/autotune'
DOWNLOAD_URL = '{}/service/download.php'.format(WEBSITE_URL)

# Logging for the daemon and evolutionary processes.
logger = logging.getLogger('autotune')
logger.setLevel(logging.INFO)
logging.getLogger('inspyred.ec').setLevel(logging.WARNING) # Use logging.DEBUG for more information or logging.WARNING for less.
logging_filehandler = logging.FileHandler('autotune.log')
logging_filehandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger('inspyred.ec').addHandler(logging_filehandler)
logger.addHandler(logging_filehandler)


'''****************************************************************************
*****************************     IDF Classes     *****************************
****************************************************************************'''
class Field(object):
    """Represents a field in an E+ IDD file.
    
    This class represents an IDD field, which holds the details for an actual
    IDF parameter. For instance, the following excerpt from an IDD file:
    
    Building,
           \unique-object
           \required-object
           \min-fields 8
      A1 , \field Name
           \required-field
           \retaincase
           \default NONE
      N1 , \field North Axis
           \note degrees from true North
           \units deg
           \type real
           \default 0.0
        
    In IDD terminology, the "Building" element would be the object. Both the
    A1 and N1 elements are fields.
    
    """
    def __init__(self, name=None):
        self.name = name
        self.position = None
        self.note = ''
        self.required = False
        self.units = None
        self.minimum = None
        self.maximum = None
        self.include_minimum = True
        self.include_maximum = True
        self.default = None
        self.autosizable = False
        self.autocalculatable = False
        self.type = None
        self.retain_case = False
        self.choices = []
        self.object_list = None
        self.reference = None
    def __str__(self):
        if self.units is not None and 'See Below' not in self.units:
            return '%s {%s}' % (self.name, self.units)
        else:
            return self.name

class Object(object):
    """Represents an object in an E+ IDD file.
    
    This class represents an IDD object, which holds the set of fields
    for an IDF element. For instance, the following excerpt from an IDD file:
    
    Building,
           \unique-object
           \required-object
           \min-fields 8
      A1 , \field Name
           \required-field
           \retaincase
           \default NONE
      N1 , \field North Axis
           \note degrees from true North
           \units deg
           \type real
           \default 0.0
        
    In IDD terminology, the "Building" element would be the object. Both the
    A1 and N1 elements are fields.
    
    """
    def __init__(self, name=None):
        self.name = name
        self.memo = ''
        self.unique = False
        self.required = False
        self.minimum_fields = 0
        self.format = None
        self.fields = {}
    def __str__(self):
        return self.name

class Group(object):
    """Represents a group in an E+ IDD file.
    
    This class represents an IDD group, which is simply a named collection
    of objects.
    
    """
    def __init__(self, name=None):
        self.name = name
        self.objects = []
    def __str__(self):
        return self.name
        
class IDDFile(object):
    """Represents an E+ IDD file.
    
    This class contains all of the information for an IDD file, which defines
    the types and format of data that an IDF file can hold. When an IDDFile
    instance is created, the file is parsed and all data definitions are 
    compiled using the Field/Object/Group classes above.
    
    This is the class that contains all of the orientation information. Its
    complementary class, IDFFile, is simply a repository of information. It
    contains an IDDFile instance inside of it that can be used to make 
    determinations about what the particular data represents, but the IDFFile,
    itself, cannot interpret the data.
    
    As a way of example, consider the following segment of an IDF file:
    
    Building,
        ZEBRAlliance House number 1 SIP House,  !- Name
        -37,                     !- North Axis {deg}
        Suburbs,                 !- Terrain
        0.04,                    !- Loads Convergence Tolerance Value
        0.4,                     !- Temperature Convergence Tolerance Value {deltaC}
        FullExteriorWithReflections,  !- Solar Distribution
        25,                      !- Maximum Number of Warmup Days
        6;                       !- Minimum Number of Warmup Days
    
    For the IDD file, "Building" would be considered an object, and all of the
    components that follow are considered fields.
    
    For the IDF file, "Building" would be considered the class, 
    "ZEBRAlliance House number 1 SIP House" would be considered
    the name of the object (instance of the class), and the remaining
    elements are considered fields.
    
    """
    def __init__(self, idd_file):
        """Create a new IDD file from a file-type object.
        
        This constructor takes a file-type object that represents the IDD file
        and simply calls the load method with the file.
        
        """
        self.load(idd_file)
    
    def _get(self, name, str):
        if '\\%s' % name in str:
            parts = str.split('\\%s' % name)
            if len(parts) > 1:
                return parts[1].strip().strip(',').strip(';')
            else:
                return True
        else:
            return None
    
    def load(self, idd_file):
        """Load the IDD file from a file-type object.
        
        This function takes a file-type object that represents the IDD file
        and parses it to create the Field/Object/Group elements.
        
        """
        self.groups = []
        field_pattern = re.compile(r'([AN]\d+\s*[,;])+')
        no_comments = re.sub(r'!.*\n', '', ''.join(idd_file.readlines()))
        lines = no_comments.split('\n')
        current_group = None
        current_object = None
        current_field = None
        for line in lines[5:]:
            line = line.strip()
            if len(line) > 0:
                if self._get('group', line): 
                    group_name = self._get('group', line)
                    current_group = Group(group_name)
                    self.groups.append(current_group)
                    current_object = None
                    current_field = None
                elif current_group is not None and not line.startswith('\\') and field_pattern.search(line) is None:
                    object_name = line.strip(',').strip(';')
                    current_object = Object(object_name)
                    current_group.objects.append(current_object)
                    current_field = None
                    field_position = 0
                elif self._get('memo', line):
                    current_object.memo += self._get('memo', line) + ' '
                elif self._get('unique-object', line):
                    current_object.unique = True
                elif self._get('required-object', line):
                    current_object.required = True
                elif self._get('min-fields', line):
                    current_object.minimum_fields = int(self._get('min-fields', line))
                elif self._get('format', line):
                    current_object.format = self._get('format', line)
                elif current_object is not None and field_pattern.search(line):
                    field_name = self._get('field', line)
                    m = field_pattern.search(line)
                    for g in m.groups():
                        if field_name is None:
                            field_name = g[:-1]
                        current_field = Field(field_name)
                        current_field.position = field_position
                        current_object.fields[field_name] = current_field
                        field_position += 1
                elif self._get('note', line):
                    current_field.note += self._get('note', line) + ' '
                elif self._get('required-field', line):
                    current_field.required = True
                elif self._get('unitsBasedOnField', line):
                    current_field.units = 'See Below'
                elif self._get('units', line):
                    current_field.units = self._get('units', line)
                elif self._get('minimum>', line):
                    current_field.minimum = float(self._get('minimum>', line))
                    current_field.include_minimum = False
                elif self._get('minimum', line):
                    current_field.minimum = float(self._get('minimum', line))
                elif self._get('maximum<', line):
                    current_field.maximum = float(self._get('maximum<', line))
                    current_field.include_maximum = False
                elif self._get('maximum', line):
                    current_field.maximum = float(self._get('maximum', line))
                elif self._get('default', line):
                    current_field.default = self._get('default', line)
                elif self._get('autosizable', line):
                    current_field.autosizable = True
                elif self._get('autocalculatable', line):
                    current_field.autocalculatable = True
                elif self._get('type', line):
                    current_field.type = self._get('type', line)
                elif self._get('retaincase', line):
                    current_field.retain_case = True
                elif self._get('key', line):
                    current_field.choices.append(self._get('key', line))
                elif self._get('object-list', line):
                    current_field.object_list = self._get('object-list', line)
                elif self._get('reference', line):
                    current_field.reference = self._get('reference', line)
                        
    def get_fields(self, object_name):
        """Returns a list of fields that are contained in a given object.
        
        This function returns a list of fields contained in an object,
        sorted by position. If the object cannot be found, the function
        returns None.
        
        """    
        for g in self.groups:
            try:
                index = [o.name.upper() for o in g.objects].index(object_name.upper())
                fields = [g.objects[index].fields[f] for f in g.objects[index].fields]
                fields.sort(key=lambda x: x.position)
                return fields
            except ValueError:
                pass
        return None
    
    def get_field_index(self, object_name, field_name):
        """Returns the index of a specified field within the specified object.
        
        This function returns the position of a field within an object. Objects
        are simply named collections of fields, and those fields have a pre-defined
        order as specified in the IDD file. This function determines that position
        and returns it, or it returns None if the object/field pair cannot be found.
        
        """    
        for g in self.groups:
            try:
                index = [o.name.upper() for o in g.objects].index(object_name.upper())
                return g.objects[index].fields[field_name].position + 1
            except (ValueError, KeyError):
                pass
        return None
        
class IDFFile(object):
    """Represents an E+ IDF file.
    
    This class contains all of the raw information for an IDF file. It contains
    an instance of IDDFile that it uses to interpret the information it holds,
    but this class, itself, is just a data repository. Essentially, if a user
    wants to find a particular object/field combination, this class would 
    have to first determine the index locations for the name of the object
    and the name of the field, which it accomplishes by looking at the IDD
    file. 
    
    As a way of example, consider the following segment of an IDF file:
    
    Building,
        ZEBRAlliance House number 1 SIP House,  !- Name
        -37,                     !- North Axis {deg}
        Suburbs,                 !- Terrain
        0.04,                    !- Loads Convergence Tolerance Value
        0.4,                     !- Temperature Convergence Tolerance Value {deltaC}
        FullExteriorWithReflections,  !- Solar Distribution
        25,                      !- Maximum Number of Warmup Days
        6;                       !- Minimum Number of Warmup Days
    
    For the IDD file, "Building" would be considered an object, and all of the
    components that follow are considered fields.
    
    For the IDF file, "Building" would be considered the class, 
    "ZEBRAlliance House number 1 SIP House" would be considered
    the name of the object (instance of the class), and the remaining
    elements are considered fields.
    
    """
    def __init__(self, idf_file, idd_file=None):
        self.load(idf_file, idd_file)
        
    def load(self, idf_file, idd_file=None):
        if idd_file is None:
            if sys.platform == 'win32':
                with open('C:/EnergyPlusV7-0-0/Energy+.idd') as idd_file:
                    self.idd = IDDFile(idd_file)
            elif sys.platform == 'linux2':
                with open('/usr/local/EnergyPlus-7-0-0/bin/V7-0-0-Energy+.idd') as idd_file:
                    self.idd = IDDFile(idd_file)
        self.idf = []
        no_extra_space = re.sub(r'[ \t\f\v]+', ' ', ''.join(idf_file.readlines()))
        no_comments = re.sub(r'!.*', '', no_extra_space)
        idf_lines = no_comments.split(';')
        for line in idf_lines:
            line = line.strip()
            if len(line) > 0:
                parts = line.split(',')
                parts = [p.strip() for p in parts]
                self.idf.append(parts)
    
    def __str__(self):
        s = ''
        prev_obj = None
        for object in self.idf:
            oname = object[0]
            if prev_obj != oname:
                s += '\n!-   ===========  ALL OBJECTS IN CLASS: %s ===========\n\n' % oname.upper()
            prev_obj = oname
            s += '%s,\n' % oname
            fields = self.idd.get_fields(oname)
            field_names = [str(f) for f in fields] if fields is not None else []
            lines = []
            for field, field_name in zip(object[1:], field_names):
                field_val = '{0},'.format(field)
                if len(field_val) > 25:
                    field_val += '  '
                lines.append('    {0:<25}!- {1}'.format(field_val, field_name))
            s += '\n'.join(lines)
            temp = s.rsplit(',', 1)
            s = ';'.join(temp)
            s += '\n\n'
        return s
    
    def save(self, idf_file):
        idf_file.write(str(self))
            
    def _find(self, class_name, object_name=None, field_name=None):
        objs = []
        for object in self.idf:
            if object[0].upper() == class_name.upper():
                objs.append(object)
        if object_name is None and field_name is None:
            return objs
        else:
            the_object = None
            name_index = self.idd.get_field_index(class_name, 'Name')
            for obj in objs:
                if obj[name_index].upper() == object_name.upper():
                    the_object = obj
            if field_name is None:
                return the_object
            elif field_name is not None and the_object is not None:
                field_index = self.idd.get_field_index(class_name, field_name)
                return the_object[field_index]
            else:
                return None
    
    def find(self, class_name, object_name, field_name):
        """Returns the value associated with the specified class/object/field.
        
        This function returns the value in the IDF file for a given
        class/object/field designation. If no such element can be found, the
        function returns None. If there are multiple values that match the
        criteria, only the first is returned.
        
        As an example, a search for 
        ("Building", "ZEBRAlliance House number 1 SIP House", "North Axis")
        would return a value of -37 from the segment listed above.
        
        """    
        name_index = self.idd.get_field_index(class_name, 'Name')
        field_index = self.idd.get_field_index(class_name, field_name)
        objects = self._find(class_name)
        for obj in sorted(objects):
            if name_index is None or obj[name_index].upper() == object_name.upper():
                return obj[field_index]
        return None
    
    def update(self, class_name, object_name, field_name, value):
        """Returns the value associated with the specified class/object/field.
        
        This function operates similarly to the find method. Given the
        class/object/field specification, all matching elements in the IDF
        file are updated with the new value. The function returns the total 
        number of fields that were updated.
        
        """    
        name_index = self.idd.get_field_index(class_name, 'Name')
        field_index = self.idd.get_field_index(class_name, field_name)
        objects = self._find(class_name)
        count = 0
        for obj in sorted(objects):
            if name_index is None or obj[name_index].upper() == object_name.upper():
                obj[field_index] = value
                count += 1
        return count
     

'''****************************************************************************
*************************     EnergyPlus Classes     **************************
****************************************************************************'''     
class EnergyPlus(object):
    """Represents the Energy Plus command-line software.

    This class provides a consistent interface to the Energy Plus
    software. With it, command-line processes can be run on IDF
    files and their results can be processed. Instantiating
    this class requires specification of the EPlus runner script
    and the installed weather file directory.
    
    For the Windows and Ubuntu operating systems, the following 
    instantiations should work for default Energy Plus installations:
    
    eplus_ubuntu  = EnergyPlus("/usr/local/bin/runenergyplus", "/usr/local/EnergyPlus-7-0-0/WeatherData")
    eplus_windows = EnergyPlus("C:\\EnergyPlus-7-0-0\\RunEPlus.bat", "C:\\EnergyPlus-7-0-0\\WeatherData")
    
    """    
    def __init__(self, runner_script = None, weather_directory = None):
        if sys.platform == 'win32':
            if runner_script is None:
                runner_script = 'C:\\EnergyPlusV7-0-0\\RunEPlus.bat'
            if weather_directory is None:
                weather_directory = 'C:\\EnergyPlusV7-0-0\\WeatherData\\'
        elif sys.platform == 'linux2':
            if runner_script is None:
                runner_script = '/usr/local/bin/runenergyplus'
            if weather_directory is None:
                weather_directory = '/usr/local/EnergyPlus-7-0-0/WeatherData'
        else:
            print('Unsupported Platform')
        self.runner_script = runner_script
        self.weather_directory = weather_directory
        self.current_output_directory = None
        
    def run(self, idf_filename, weather_filename, output_directory):
        """Run EnergyPlus on the specified IDF file.
        
        This function runs the EnergyPlus command-line script on the
        given IDF file. The IDF file should exist in the specified
        output directory (which is also where the EPlus temporary
        and output files will be placed). The specified weather file
        should exist in the EnergyPlus installation weather files
        directory.
        
        The function returns True if the EnergyPlus simulation could
        be executed and False (with a stdout message) otherwise.
        
        """
        if self.runner_script is not None and self.weather_directory is not None and os.path.isfile(self.runner_script) and os.path.isdir(self.weather_directory):
            if self.current_output_directory is not None and os.path.exists(self.current_output_directory):
                # Cleanup the files in this directory.
                # For now, and possibly always, do nothing.
                pass
            if os.path.isabs(output_directory):
                self.current_output_directory = output_directory
            else:
                self.current_output_directory = os.path.join(os.getcwd(), output_directory)
            if not os.path.exists(self.current_output_directory):
                os.mkdir(self.current_output_directory)
            #Remove the extentions of the files if they exist
            idf_filename = idf_filename.replace('.idf', '') 
            weather_filename = weather_filename.replace('.epw', '')
            
            weather_location = os.path.join(self.weather_directory, weather_filename + '.epw')
            idf_location = os.path.join(self.current_output_directory, idf_filename + '.idf')
            
            if not os.path.isfile(idf_location) and os.path.isfile(os.path.join(os.getcwd(), idf_filename + '.idf')):
                shutil.copy(os.path.join(os.getcwd(), idf_filename + '.idf'), self.current_output_directory)
            
            if os.path.isfile(idf_location) and os.path.isfile(weather_location):
                previous_dir = os.getcwd()
                os.chdir(self.current_output_directory)
                cmd = [self.runner_script,  idf_filename, weather_filename]
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                
                # Load the err file and see if there was a fatal error.
                fatal_error = False
                with open(os.path.join(self.get_results_directory(), idf_filename + '.err')) as errfile:
                    errtext = errfile.read()
                    if ' Fatal ' in errtext:
                        fatal_error = True
                        
                os.chdir(previous_dir)
                return not fatal_error
            elif not os.path.isfile(idf_location):
                logger.error('EnergyPlus.run() :: The file {0} does not exist.'.format(idf_location))
                return False
            else:
                logger.error('EnergyPlus.run() :: The file {0} does not exist.'.format(weather_location))
                return False                
        else:
            logger.error('EnergyPlus.run() :: The EnergyPlus configuration (weather file location, installation directory, etc.) is not valid.')
            return False

    def get_results_directory(self):
        directory = self.current_output_directory
        if sys.platform.startswith('linux'): 
            directory = os.path.join(self.current_output_directory, 'Output')
        return directory
        
    def get_results(self, output_filename):
        """Get the results from a given Energy Plus CSV file.
        
        This method returns the values from a given E+ CSV output file.
        This file should exist in the output directory of the 
        `EnergyPlus` object. However, you should not specify these 
        directories via the function parameter. You should only specify
        the name of the output file under consideration. This filename
        should always be the name of the IDF file used for simulation,
        except with a .csv extension, rather than .idf.
        
        """
        if os.path.isabs(output_filename):
            i = output_filename.rfind(os.sep)
            self.current_output_directory = output_filename[:i]
            output_filename = output_filename[i+1:]
            i = self.current_output_directory.rfind(os.sep)
            self.current_output_directory = self.current_output_directory[:i]
        csv_file = os.path.join(self.current_output_directory, output_filename)
        if sys.platform.startswith('linux'): 
            csv_file = os.path.join(self.current_output_directory, 'Output', output_filename)
        if os.path.isfile(csv_file):
            reader = csv.DictReader(open(csv_file, 'rb'))
            unit_data = [{key: row[key] for key in row} for row in reader]
            return unit_data
        else:
            return None

class EPlusVariable(object):
    """Represents an EnergyPlus variable for autotuning.
    
    This class defines an EnergyPlus variable that can be autotuned.
    Each variable has information on the IDF location of the variable;
    value type; minimum, maximum, and default values; frequency distribution;
    group name; constraint; and value.
    
    """
    def __init__(self, idfclass=None, idfobject=None, idffield=None, default=None, minimum=None, maximum=None, distribution=None, type=None):
        self.idfclass = idfclass
        self.idfobject = idfobject
        self.idffield = idffield
        self.type = type.lower()    # 'float' or 'integer'
        if self.type == 'integer':
            self.default = int(default)
            self.minimum = int(minimum)
            self.maximum = int(maximum)
        else:
            self.default = float(default)
            self.minimum = float(minimum)
            self.maximum = float(maximum )
        self.distribution = distribution
        self.group = None
        self.constraint = None
        self.value = 0

    def __str__(self):
        return '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9} {10}'.format(self.idfclass, self.idfobject, self.idffield, self.default, 
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
        self.EPSILON = 0.0000000001
        self.constraint = constraint.strip()
        self.variables = []
        self.comparator = None
        self.lhs = None
        self.rhs = None
        parts = self.constraint.split()
        if len(parts) > 0:
            for p in parts:
                if p[0] in string.lowercase or p[0] in string.uppercase:
                    self.variables.append(p)
                elif p in ['>=', '<=', '>', '<']:
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
        return '{0} ==> {1}'.format(self.variables, self.constraint)
        
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
            newvar = EPlusVariable(variable.idfclass, variable.idfobject, variable.idffield, variable.default, 
                                   variable.minimum, variable.maximum, variable.distribution, variable.type)
            newvar.group = variable.group
            newvar.constraint = EPlusConstraint(variable.constraint.constraint)
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
        sorted by their variable ranges (max - min). This ordering of the
        variables allows us to process the constraints so that the "least
        flexible" (i.e., smallest range) of the components is satisfied 
        first.
        
        """    
        order = []
        for group in self.variables:
            variable = self.get_variable(group)
            range = variable.maximum - variable.minimum
            order.append((group, range))
        order.sort(key=lambda x: x[1])
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
        variable = self.variables[group][0]
        constraint = variable.constraint
        if constraint.is_valid():
            var_dict = {}
            for varname in constraint.variables:
                var_dict[varname] = self.get_value(varname)
            lhv = self._evaluate(constraint.lhs, var_dict)
            rhv = self._evaluate(constraint.rhs, var_dict)
            remainder = rhv - lhv
            if '<=' in constraint.comparator:
                return (min(variable.minimum, remainder), min(variable.maximum, remainder))
            elif '<' in constraint.comparator:
                return (min(variable.minimum, remainder - constraint.EPSILON), min(variable.maximum, remainder - constraint.EPSILON))
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
        
    def clone(self, values=None):
        """Creates a deep copy of the candidate, optionally initialized with values.
        
        """
        vars = []
        for group in self.variables:
            for v in self.variables[group]:
                vars.append(v)
        candidate = EPlusCandidate(vars)
        if values is not None:
            candidate.set_values(values)
        return candidate
        
    def values_from_idf(self, idffile):
        """Initializes the candidate with values from the open IDF file.
        
        This method takes a file-like object representing an IDF file and
        initializes the values of the candidate to those pulled from the 
        IDF file. The candidate must already exist before this method can
        be used. Remember that the actual candidate elements must come from
        a parameter file. Otherwise, this method would not know which values
        to pull from the IDF file.
        
        """
        idf = IDFFile(idffile)
        for group in self.variables:
            for i, v in enumerate(self.variables[group]):
                val = idf.find(v.idfclass, v.idfobject, v.idffield)
                self.variables[group][i].value = int(val) if v.type == 'integer' else float(val)
       
    def values_to_idf(self, idffile):
        """Loads the open IDF file with the candidate's values and returns the contents as a string.
        
        This method takes a file-like object representing an IDF file and
        replaces the values in the file with those from the candidate.
        The method returns the full, modified IDF file as a string.
        
        """        
        idf = IDFFile(idffile)
        for group in self.variables:
            for i, v in enumerate(self.variables[group]):
                idf.update(v.idfclass, v.idfobject, v.idffield, self.variables[group][i].value)
        return str(idf)
        
    def __str__(self):
        return str(self.get_values())
        
    def __repr__(self):
        return str(self)


'''****************************************************************************
***********************     Evolutionary Operators     ************************
****************************************************************************'''     
        
def autotune_bounder(candidate, args):
    def roundsig(x, sig=2):
        y = 0.0 if x == 0 else round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)
        return y
        
    for group in candidate:
        variable = candidate.get_variable(group)
        candidate.set_value(group, max(min(candidate.get_value(group), variable.maximum), variable.minimum))
        if variable.type == 'integer':
            candidate.set_value(group, int(candidate.get_value(group)))
        else: # variable.type == 'float'
            candidate.set_value(group, roundsig(candidate.get_value(group), 5))
    return candidate

def autotune_generator(random, args):
    eplus_variables = args['eplus']['variables']
    groups = eplus_variables.get_constraint_order()
    candidate = eplus_variables.clone()
    for group in groups:
        variable = candidate.get_variable(group)
        lo, hi = candidate.get_constrained_bounds(group)
        if variable.type == 'integer':
            candidate.set_value(group, random.randint(lo, hi))
        else: # self.type == 'float'
            candidate.set_value(group, random.uniform(lo, hi))
    candidate = args['_ec'].bounder(candidate, args)
    return candidate
    
@inspyred.ec.variators.mutator
def autotune_mutator(random, candidate, args):
    mutation_usage_rate = args.get('mutation_usage_rate', 0.1)
    maximum_mutation_rate = args.get('maximum_mutation_rate', 0.1)
    numevals = args['_ec'].num_evaluations
    #maxevals = args['max_evaluations']
    popsize = len(args['_ec'].population)
    # Rational function used for mutation rate
    mutation_rate = maximum_mutation_rate #* popsize / float(numevals)
    bounder = args['_ec'].bounder
    groups = candidate.get_constraint_order()
    mutant = candidate.clone()
    for group in groups:
        variable = candidate.get_variable(group)
        lo, hi = mutant.get_constrained_bounds(group)
        if random.random() < mutation_usage_rate:
            if variable.type == 'integer':
                if random.random() < mutation_rate:
                    options = range(lo, hi + 1)
                    options.remove(candidate.get_value(group))
                    mutant.set_value(group, random.choice(options))
                else:
                    mutant.set_value(group, candidate.get_value(group))
            else: # variable.type == 'float'
                mutant.set_value(group, candidate.get_value(group) + random.gauss(0, 1) * mutation_rate * (hi - lo) / 2.0)
        else:
            mutant.set_value(group, candidate.get_value(group))
    return bounder(mutant, args)

def autotune_crossover(random, candidates, args):
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
            bro_values = copy.copy(dad_values)
            sis_values = copy.copy(mom_values)
            for i, (m, d) in enumerate(zip(mom_values, dad_values)):
                negpos = 1 if mom_is_better else -1
                val = d if mom_is_better else m
                bro_values[i] = val + random.random() * negpos * (m - d)
                sis_values[i] = val + random.random() * negpos * (m - d)
            bro = dad.clone(bro_values)
            sis = mom.clone(sis_values)
            bro = bounder(bro, args)
            sis = bounder(sis, args)
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom)
            children.append(dad)
    return children

@inspyred.ec.evaluators.evaluator   
def autotune_evaluator(candidate, args):
    eplus_params = args['eplus']
    eplus_runner = eplus_params['runner']
    eplus_weather = eplus_params['weather']
    eplus_model = eplus_params['model']
    eplus_schedule = eplus_params.setdefault('schedule', None)
    eplus_error_function = eplus_params['error_function']
    user_data = eplus_params['user_data']
    tracking_id = eplus_params['tracking_id']
    WORST_FITNESS = 999999999 
    
    fitness = WORST_FITNESS
    constraints = [candidate.evaluate_constraint(group) for group in candidate]
    if not all(constraints):
        constraints_failed = [candidate.get_variable(group).constraint.constraint for constraint, group in zip(constraints, candidate) if not constraint]
        fitness = len(constraints_failed) * 1000000.0
        logger.info('autotune_evaluator() :: Tracking ID {} :: {} constraints failed. The candidate is {} and the failed constraints are {}.'.format(tracking_id, len(constraints_failed), str(candidate), str(constraints_failed)))
    else:
        output_directory = tempfile.mkdtemp(suffix='.%s' % str(id(threading.current_thread)), dir=os.path.join(eplus_params['output_directory']))
        shutil.copy(os.path.join(eplus_params['output_directory'], eplus_model), os.path.join(output_directory, eplus_model))
        if eplus_schedule is not None:
            shutil.copy(os.path.join(eplus_params['output_directory'], eplus_schedule), os.path.join(output_directory, eplus_schedule))
        with open(os.path.join(output_directory, eplus_model)) as idfmodel:
            idf = IDFFile(idfmodel)
        for group in candidate:
            for variable in candidate.variables[group]:
                idf.update(variable.idfclass, variable.idfobject, variable.idffield, candidate.get_value(group))
        output_filename = 'eplusinspyred'
        with open(os.path.join(output_directory, output_filename + '.idf'), 'w') as outfile:
            idf.save(outfile)
            
        # Run EnergyPlus and make sure that it worked correctly.
        logger.info('autotune_evaluator() :: Tracking ID {} :: Starting EnergyPlus in directory {}.'.format(tracking_id, output_directory))
        success = eplus_runner.run(output_filename, eplus_weather, output_directory)
        logger.info('autotune_evaluator() :: Tracking ID {} :: EnergyPlus completed in directory {} with success={}.'.format(tracking_id, output_directory, success))
        
        # If there was a problem with the simulation, save it to a file.
        if not success:
            ezname = os.path.join(ERROR_DIRECTORY, '{}.error.zip'.format(os.path.basename(os.path.normpath(output_directory))))
            zipit(output_directory, ezname)
            logger.error('autotune_evaluator() :: Tracking ID {} :: EnergyPlus failed to execute. Full information can be found in {}.'.format(tracking_id, ezname))
            fitness = WORST_FITNESS
        else:
            eplus_data = load_eplus_user_data(os.path.join(eplus_runner.get_results_directory(), output_filename + '.csv'))
            if eplus_data is None or user_data is None: 
                ezname = os.path.join(ERROR_DIRECTORY, '{}.error.zip'.format(os.path.basename(os.path.normpath(output_directory))))
                zipit(output_directory, ezname)
                if eplus_data is None:
                    logger.error('autotune_evaluator() :: Tracking ID {} :: EnergyPlus output is None. Full information can be found in {}.'.format(tracking_id, ezname))
                elif user_data is None:
                    logger.error('autotune_evaluator() :: Tracking ID {} :: User data is None. Full information can be found in {}.'.format(tracking_id, ezname))
                fitness = WORST_FITNESS
            else:
                fitness = eplus_error_function(eplus_data, user_data)
        
        cleanup = True
        try:
            cleanup = eplus_params['cleanup']
        except KeyError:
            cleanup = True
            
        if cleanup:
            try:
                shutil.rmtree(output_directory)
                logger.info('autotune_evaluator() :: Tracking ID {} :: Successfully removed directory tree {}.'.format(tracking_id, output_directory))
            except:
                logger.warning('autotune_evaluator() :: Tracking ID {} :: Unable to clean up directory tree {}.'.format(tracking_id, output_directory))
        
    return fitness

def autotune_observer(population, num_generations, num_evaluations, args):
    """Replaces the old population with the new one in the database.
    
    Replace all of the current files and fitness values for this tracking 
    number with the current population.
    
    """
    tracking_id = args['eplus']['tracking_id']
    eplus_model = args['eplus']['model']
    eplus_output_dir = args['eplus']['output_directory']
    db = database_connect(DBHOST, DBUSER, DBPASS, DBNAME)
    cursor = db.cursor()
    
    # Pull the last generation's models in order to update them (if any).
    cursor.execute('SELECT Model.id FROM Tracking, TrackingModel, Model WHERE Tracking.id = TrackingModel.trackingId AND TrackingModel.modelId = Model.id AND Tracking.id = %s', tracking_id)
    model_ids = cursor.fetchall()
    
    for i, individual in enumerate(reversed(sorted(population))):
        with open(os.path.join(eplus_output_dir, eplus_model)) as basefile:
            ifile = individual.candidate.values_to_idf(basefile)
        sfile = StringIO.StringIO()
        tempzip = zipfile.ZipFile(sfile, 'w', zipfile.ZIP_DEFLATED)
        tempzip.writestr('tuned.idf', ifile)
        tempzip.close()
        zfile = sfile.getvalue()
        sfile.close()
        ifit = individual.fitness
        try:
            # If the position of the current candidate is less than the
            # number of existing models, then we should update that record.
            # Otherwise, we should just add a new record.
            if len(model_ids) > i:
                cursor.execute('UPDATE Model SET file = %s, fit = %s WHERE id = %s', (zfile, ifit, model_ids[i][0]))
            else:
                cursor.execute('INSERT INTO Model (file, fit) VALUES (%s, %s)', (zfile, ifit))
                cursor.execute('SELECT LAST_INSERT_ID()')
                mid = cursor.fetchone()[0]
                cursor.execute('INSERT INTO TrackingModel (trackingId, modelId) VALUES (%s, %s)', (tracking_id, mid))
            db.commit()
        except database_error(), e:
            logger.error('autotune_observer() :: Tracking ID {} :: Could not insert new generation individual {}. Error number {}: {}.'.format(tracking_id, i, e[0], e[1]))
            db.rollback()
    start_time = args.setdefault('start_time', None)
    if start_time is not None:
        cursor.execute('SELECT runtime FROM Tracking WHERE Tracking.id = %s', tracking_id)
        previous_runtime = cursor.fetchall()[0][0]
        current_runtime = previous_runtime + time.time() - start_time
        try:
            cursor.execute('UPDATE Tracking SET runtime = %s WHERE id = %s', (current_runtime, tracking_id))
            db.commit()
        except database_error(), e:
            logger.error('autotune_observer() :: Tracking ID {} :: Could not update runtime to {}. Error number {}: {}.'.format(tracking_id, current_runtime, e[0], e[1]))
            db.rollback()
    db.close()

def autotune_termination(population, num_generations, num_evaluations, args):
    tracking_id = args['eplus']['tracking_id']
    db = database_connect(DBHOST, DBUSER, DBPASS, DBNAME)
    cursor = db.cursor()
    cursor.execute('SELECT id, terminate FROM Tracking WHERE id = %s', tracking_id)
    next_job = cursor.fetchone()
    terminate = next_job[1]
    db.close()
    return (terminate == 1)

    
'''****************************************************************************
*****************************     Utilities     *******************************
****************************************************************************''' 
# These two methods are an attempt to separate the MySQL-specific parts from
# the rest. This is nearly impossible to do, given the query statements that
# are DBMS-specific, but it's an attempt.
def database_connect(dbhost, dbuser, dbpass, dbname):
    return MySQLdb.connect(dbhost, dbuser, dbpass, dbname)
    
def database_error():
    return MySQLdb.Error
    

def error_function(predicted, actual):
    error = 0
    count = 0
    pred = []
    # Initialize i here so that it doesn't start back at the beginning of the
    # year every time through the loop.
    i = 0
    for act_row in actual:
        p = {k: 0 for k in act_row}
        # Add up any finer-grained predicted data to match up with the actual data.
        while i < len(predicted) and predicted[i]['Date/Time'] <= act_row['Date/Time']:
            for key in act_row:
                if 'Date/Time' not in key:
                    p[key] += predicted[i][key]
            i += 1
        pred.append(p)
        
    for pred_row, act_row in zip(pred, actual):
        for key in act_row:
            if 'Date/Time' not in key:
                p = pred_row[key]
                a = act_row[key]
                error += (p - a)**2
                count += 1
    try:
        error = math.sqrt(error / float(count))
    except ZeroDivisionError:
        error = 999999998
    return error

def load_variables(param_filename):
    group_num = 1
    vars = []
    with open(param_filename, 'r') as param_file: 
        reader = csv.DictReader(param_file)
        for row in reader:
            v = EPlusVariable(row['Class'], row['Object'], row['Field'], 
                              row['Default'], row['Minimum'], row['Maximum'], 
                              row['Distribution'], row['Type'])
            if 'Group' in row and len(row['Group'].strip()) > 0:
                v.group = row['Group'].strip()
            else:
                v.group = 'InspyredGroup{0:03d}'.format(group_num)
                group_num += 1
            if 'Constraint' in row and len(row['Constraint'].strip()) > 0:
                v.constraint = EPlusConstraint(row['Constraint'].strip())
            else:
                v.constraint = EPlusConstraint()
            vars.append(v)
    return vars

    
def zipit(file_or_dir, ziploc):
    zip = zipfile.ZipFile(ziploc, 'w', zipfile.ZIP_DEFLATED)
    if os.path.isfile(file_or_dir):
        zip.write(file_or_dir)
    else:
        for root, dirs, files in os.walk(file_or_dir):
            for file in files:
                zip.write(os.path.join(root, file))
    zip.close()


def convert_to_datetime(eplus_string, year=None):
    if year is None:
        year = datetime.datetime.now().year
    parts = eplus_string.split()
    month, day = [int(x) for x in parts[0].split('/')]
    hour, minute, second = [int(x) for x in parts[1].split(':')]
    if hour == 24:
        actual_day = datetime.date(year, month, day) + datetime.timedelta(days=1)
        return datetime.datetime(actual_day.year, actual_day.month, actual_day.day,
                                 0, minute, second)
    else:
        return datetime.datetime(year, month, day, hour, minute, second)
    

def load_eplus_user_data(filename):
    last_year = datetime.datetime.now().year - 1
    data = []
    with open(filename) as datafile:
        datacsv = csv.DictReader(datafile)
        for i, row in enumerate(datacsv):
            d = {}
            for key in row:
                if 'Date/Time' in key:
                    d[key.strip()] = convert_to_datetime(row[key], last_year)
                else:
                    try:
                        d[key.strip()] = float(row[key])
                    except ValueError:
                        d[key.strip()] = 0
            data.append(d)
    return data


def upload_experiment(title, description, machine, stats_file, inds_file, proxy=None):
    url = 'http://yourdomain.com/main/?q=content/autotune-experiment-upload-status'
    data = {'key': 'enter a key here',
            'expmt_title': title,
            'expmt_desc': description,
            'machine_name': machine}
    files = {'expmt_statstfile': (stats_file, open(stats_file, 'rb')),
             'expmt_inpfile': (inds_file, open(inds_file, 'rb'))}

    response = requests.post(url, data=data, files=files, proxies=proxy)
    try:
        lines = response.content.split('<p>')
        for line in lines:
            if 'data was uploaded successfully and was assigned an experiment number' in line:
                return True
        return False
    except:
        return False
    
    
'''****************************************************************************
****************************     Main Script     ******************************
****************************************************************************'''
def main():
    import argparse
    import getpass
    parser = argparse.ArgumentParser(description='initiates the autotune service to begin checking the database for tuning jobs',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--mailserver', help='the mail server to use (gmail or localhost)', default='localhost')
    parser.add_argument('--loglevel', help='the lowest level (info, debug, warning, error) at which to log events', default='warning')
    parser.add_argument('--numcpus', help='the number of CPUs that autotune should use', type=int, default=4)
    parser.add_argument('--popsize', help='the population size for autotune', type=int, default=16)
    parser.add_argument('--tournsize', help='the tournament size for autotune', type=int, default=4)
    parser.add_argument('--maxtime', help='the maximum time allowed for a job (in seconds)', type=int, default=43200) # 12 hours
    args = parser.parse_args()

    SENDMAIL_SERVER = args.mailserver
    if 'gmail' in SENDMAIL_SERVER:
        SENDMAIL_USER = raw_input('Enter the Gmail username: ').strip()
        SENDMAIL_PASS = getpass.getpass('Enter the Gmail password: ').strip()

    if args.loglevel == 'info':
        logger.setLevel(logging.INFO)
    elif args.loglevel == 'debug':
        logger.setLevel(logging.DEBUG)
    elif args.loglevel == 'warning':
        logger.setLevel(logging.WARNING)
    elif args.loglevel == 'error':
        logger.setLevel(logging.ERROR)
    
    NCPUS = args.numcpus
    PSIZE = args.popsize
    TSIZE = args.tournsize
    MAXTIME = args.maxtime

    keep_running = True
    while keep_running:        
        # Get the next job to tune, if there is one.
        # First, see if there are any non-terminated jobs that are at position 0.
        # If there are, then run those first. If not, decrement all queue positions
        # and go back to the top of the loop.
        db = database_connect(DBHOST, DBUSER, DBPASS, DBNAME)
        cursor = db.cursor()
        cursor.execute('SELECT id, terminate, weather, email, runtime, baseModel, parameters, schedule, userData FROM Tracking WHERE queuePosition = 0')
        next_jobs = cursor.fetchall()
        if len(next_jobs) == 0:
            try:
                cursor.execute('UPDATE Tracking SET queuePosition = queuePosition - 1 WHERE queuePosition >= 0')
                db.commit()
            except database_error(), e:
                logger.error('main() :: Could not decrement queue positions. Error number {}: {}.'.format(e[0], e[1]))
                db.rollback()
            db.close()
            # Sleep for a short time to not overload the database with queries.
            time.sleep(1)
        else:
            db.close()
            for next_job in next_jobs:
                tracking_id = next_job[0]
                terminate = next_job[1]
                weather = next_job[2]
                email = next_job[3]
                runtime = float(next_job[4])
                # The files in the database are the model, parameters, schedule, and user data.
                db_filenames = [None for _ in range(4)]
                
                # If the terminate flag is set, just skip the processing.
                # Otherwise, process the submission.
                if not terminate:
                    # Make a new directory for the tracking number. Use it as the base output directory.
                    output_dir = '{}'.format(tracking_id)
                    if not os.path.exists(output_dir):
                        os.mkdir(output_dir)
                    for i in range(4):
                        if next_job[i + 5] is None:
                            db_filenames[i] = None
                        else:
                            zf = zipfile.ZipFile(StringIO.StringIO(next_job[i + 5]))
                            fn = zf.namelist()[0]
                            db_filenames[i] = fn
                            zf.extract(fn, output_dir)
                        
                    user_data = load_eplus_user_data(os.path.join(output_dir, db_filenames[3]))

                    rand_seed = time.time()
                    rand = random.Random()
                    rand.seed(rand_seed)
                    logger.info('main() :: Tracking ID {} :: Random seed used was {}.'.format(tracking_id, rand_seed))
                    
                    runner = EnergyPlus()
                    variables = EPlusCandidate(load_variables(os.path.join(output_dir, db_filenames[1])))
                    
                    # Determine whether we're resuming a previous tuning. If we are, 
                    # we need to pull the previous models to use as seeds in the 
                    # first generation. If we're not, we'll just use a single seed
                    # pulled from the default values of the base model.
                    db = database_connect(DBHOST, DBUSER, DBPASS, DBNAME)
                    cursor = db.cursor()
                    cursor.execute('SELECT Model.id, fit, file FROM Tracking, TrackingModel, Model WHERE Tracking.id = TrackingModel.trackingId AND TrackingModel.modelId = Model.id AND Tracking.id = %s', tracking_id)
                    existing_models = cursor.fetchall()
                    db.close()
                    seeds = []
                    for emodel in existing_models:
                        # All files stored in the database are zip-compressed.
                        zfile = zipfile.ZipFile(StringIO.StringIO(emodel[2]))
                        mfile = zfile.open(zfile.namelist()[0])
                        vclone = variables.clone()
                        vclone.values_from_idf(mfile)
                        seeds.append(vclone)
                        mfile.close()
                    if len(seeds) == 0:
                        seeds = [variables.clone([variables.get_variable(group).default for group in variables])]
                    logger.info('main() :: Tracking ID {} :: Using {} seed candidates.'.format(tracking_id, len(seeds)))
                    
                    ec = inspyred.ec.EvolutionaryComputation(rand)
                    ec.observer = [autotune_observer, inspyred.ec.observers.file_observer]
                    ec.terminator = [inspyred.ec.terminators.time_termination, autotune_termination]
                    ec.selector = inspyred.ec.selectors.tournament_selection
                    ec.replacer = inspyred.ec.replacers.steady_state_replacement 
                    ec.variator = [autotune_crossover, autotune_mutator]
                    sfile = open(os.path.join(output_dir, 'stat{:09}.csv'.format(tracking_id)), 'w')
                    ifile = open(os.path.join(output_dir, 'inds{:09}.csv'.format(tracking_id)), 'w')
                    final_pop = ec.evolve(generator=autotune_generator,
                                          evaluator=inspyred.ec.evaluators.parallel_evaluation_mp,
                                          bounder=autotune_bounder, 
                                          seeds=seeds,
                                          max_time=MAXTIME - runtime,
                                          pop_size=PSIZE,
                                          mp_evaluator=autotune_evaluator,
                                          mp_nprocs=NCPUS,
                                          maximize=False,
                                          num_selected=TSIZE, 
                                          tournament_size=TSIZE,
                                          mutation_usage_rate=1,
                                          maximum_mutation_rate=0.2,
                                          start_time = rand_seed,
                                          statistics_file=sfile,
                                          individuals_file=ifile,
                                          
                                          # E+/Autotune specific arguments
                                          eplus={'runner': runner, 
                                                 'variables': variables,
                                                 'weather': weather,
                                                 'model': db_filenames[0],
                                                 'schedule': db_filenames[2],
                                                 'output_directory': output_dir,
                                                 'cleanup': True,
                                                 'error_function': error_function,
                                                 'tracking_id': tracking_id,
                                                 'user_data': user_data} )
                    
                    sfile.close()
                    ifile.close()
                    
                    # Upload the results to the Autotune server.
                    submitter_name = email if email is not None else 'anonymous'
                    #upload_success = upload_experiment('Autotune Server {}'.format(tracking_id), 
                    #                                   'Tracking ID {} submitted by {}'.format(tracking_id, submitter_name), 
                    #                                   'Autotune Server', 
                    #                                   os.path.join(output_dir, 'stat{:09}.csv'.format(tracking_id)), 
                    #                                   os.path.join(output_dir, 'inds{:09}.csv'.format(tracking_id)))
                    #
                    # Send an email to the user to let them know that the job is finished.
                    # Call the sendmail function here.
                    if email is not None and '@' in email:
                        if 'gmail' in SENDMAIL_SERVER:
                            mail_server = smtplib.SMTP('smtp.gmail.com:587')
                            mail_server.starttls()
                            mail_server.login(SENDMAIL_USER, SENDMAIL_PASS)
                        else:
                            mail_server = smtplib.SMTP('smtpserver')

                        mail_from = 'youremail'
                        mail_to = email
                        msg_body = '\n'.join(['Your Autotune job (tracking# {}) has completed.'.format(tracking_id),
                                             'You can view the tuned models by visiting the Autotune website and using the tracking number.',
                                             'You can also download all tuned models as a single zip file at {}?tracking={}'.format(DOWNLOAD_URL, tracking_id)])
                        #if upload_success:
                        #    msg_body += '\n'.join(['\n\nThe results of the tuning have been submitted to the Autotune web dashboard.',
                        #                           'http://yourdomain.com/main/?q=content/autotune-dashboard',
                        #                           'The title for your tuning is "Autotune Server {}".'.format(tracking_id)])
                        
                        msg = MIMEText(msg_body)
                        msg['Subject'] = 'Autotune results ready (Tracking ID {})'.format(tracking_id)
                        msg['From'] = mail_from
                        msg['To'] = mail_to
                        mail_server.sendmail(mail_from, [mail_to], msg.as_string())
                        mail_server.quit()
                    
                    
                    # Delete the temporary directory.
                    try:
                        shutil.rmtree(output_dir)
                    except:
                        pass
                
                
                # Decrement the queue position of the tracking id so that it will be
                # marked as "finished" (queue position < 0).
                db = database_connect(DBHOST, DBUSER, DBPASS, DBNAME)
                cursor = db.cursor()
                try:
                    cursor.execute('UPDATE Tracking SET queuePosition = -1 WHERE id = %s', tracking_id)
                    db.commit()
                except database_error(), e:
                    logger.error('main() :: Tracking ID {} :: Could not set queue position to -1. Error number {}: {}.'.format(tracking_id, e[0], e[1]))
                    db.rollback()
                db.close()

                # Sleep the thread for a short time.
                time.sleep(1)
            
        # Give ourselves a way to shut down the program gracefully.
        # Just add a file into the same directory with the name 'killautotune'.
        if os.path.exists('killautotune'):
            keep_running = False
        
                 
if __name__ == '__main__':
    main()
            
