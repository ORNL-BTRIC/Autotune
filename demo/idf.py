import csv
import re
import sys


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
        if '\\{0}'.format(name.lower()) in str.lower():
            regex = re.compile(r'\s*{0}\s*'.format(re.escape('\\{0}'.format(name))), flags=re.I)
            parts = regex.split(str)
            if len(parts) > 1:
                p = parts[1].strip().strip(',').strip(';')
                return ' ' if len(p) == 0 else p
            else:
                return ' '
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
    def __init__(self, idf_file=None, idd_file=None):
        self.load(idf_file, idd_file)
        
    def load(self, idf_file=None, idd_file=None):
        if idd_file is None:
            if sys.platform == 'win32':
                with open('C:/EnergyPlusV7-0-0/Energy+.idd') as idd_file:
                    self.idd = IDDFile(idd_file)
            elif sys.platform == 'linux2':
                with open('/usr/local/EnergyPlus-7-0-0/bin/V7-0-0-Energy+.idd') as idd_file:
                    self.idd = IDDFile(idd_file)
        else:
            self.idd = IDDFile(idd_file)
        self.idf = []
        if idf_file is not None:
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
    
        
