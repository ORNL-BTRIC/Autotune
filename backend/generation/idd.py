__author__ = 'Mark Adams <adamsmb@ornl.gov>'

'''
Original source code by
Dr. Aaron Garrett, Assistant Professor, Jacksonville State University

Modified by
Mark Adams, Assistant R&D Staff, Oak Ridge National Laboratory

'''

import re
import time


class Field(object):
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

    def __unicode__(self):
        if self.units is not None and 'See Below' not in self.units:
            return u'%s {%s}' % (self.name, self.units)
        else:
            return self.name


class Object(object):
    def __init__(self, name=None):
        self.name = name
        self.memo = ''
        self.unique = False
        self.required = False
        self.minimum_fields = 0
        self.format = None
        self.fields = {}

    def __unicode__(self):
        return self.name


class Group(object):
    def __init__(self, name=None):
        self.name = name
        self.objects = []

    def __unicode__(self):
        return self.name


class IDD(object):
    def __init__(self, filename):
    #TODO: At future point, try to optimize IDD load and parsing if needed
        self.load(filename)
        self.all_ep_objects_upper = self._all_ep_objects()

    def _get(self, name, line):
        if '\\%s' % name in line:
            parts = line.split('\\%s' % name)
            if len(parts) > 1:
                return parts[1].strip().strip(',').strip(';')
            else:
                return True
        else:
            return None

    def _all_ep_objects(self):
        return [o.name.upper() for g in self.groups for o in g.objects]

    def load(self, filename):
        self.groups = []
        field_pattern = re.compile(r'([AN]\d+\s*[,;])+')
        with open(filename, 'r') as iddfile:
            no_comments = re.sub(r'!.*\n', '', ''.join(iddfile.readlines()))
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
        for g in self.groups:
            try:
                index = [o.name.upper() for o in g.objects].index(object_name.upper())
                return g.objects[index].fields[field_name].position + 1
            except (ValueError, KeyError):
                pass
        return None