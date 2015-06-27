__author__ = 'Mark Adams <adamsmb@ornl.gov>'

'''
Original source code by
Dr. Aaron Garrett, Assistant Professor, Jacksonville State University

Modified by
Mark Adams, Assistant R&D Staff, Oak Ridge National Laboratory

'''

from idd import IDD
import os
import re
import collections


IDD_OBJECTS = {"7.0": IDD(os.path.join(os.path.join(os.path.split(__file__)[0]), 'idd_files', '7.0', 'Energy+.idd'))
               #"7.1": IDD('idd_files/7.1/Energy+.idd'),
               #"7.2": IDD('idd_files/7.2/Energy+.idd'),
               #"8.0": IDD('idd_files/8.0/Energy+.idd')
}


class IDF(object):
    def __init__(self, idf_filename=None, idf_list=None):
        self.idf = []
        if idf_filename is not None:
            self.load(idf_filename)
        if idf_list is not None:
            self.load_lists(idf_list)
        self._ep_version = self._find_ep_version()
        self._idd = IDD_OBJECTS[self._ep_version]
        self.sort_idf()

    def load(self, idf_filename):
        with open(idf_filename, 'r') as idf_file:
            no_extra_space = re.sub(r'[ \t\f\\]+', ' ', ''.join(idf_file.readlines()))
            no_comments = re.sub(r'!.*', '', no_extra_space)
            idf_lines = no_comments.split(';')
            for line in idf_lines:
                line = line.strip()
                if len(line) > 0:
                    parts = line.split(',')
                    parts = [p.strip() for p in parts]
                    self.idf.append(parts)

    def load_lists(self, idf_list):
        self.flatten(idf_list, self.idf)

    def flatten(self, l, idf_list):
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
                self.flatten(el, idf_list)
            else:
                idf_list.append(l)
                break

    def sort_idf(self):
        self.idf = sorted(self.idf, key=lambda x: self._idd.all_ep_objects_upper.index(x[0].upper()))

    def _find_ep_version(self):
        for idf_object in self.idf:
            if idf_object[0].upper() == u"VERSION":
                return idf_object[1]
        return u"7.0"

    #TODO: Try to find a better to IDF method, this takes 1.410 sec in Run
    def __unicode__(self):
        s = ''
        prev_obj = None
        for idf_object in self.idf:
            oname = idf_object[0]
            if prev_obj != oname:
                s += u'\n!-   ===========  ALL OBJECTS IN CLASS: %s ===========\n\n' % oname.upper()
            prev_obj = oname
            s += u'%s,\n' % oname
            fields = self._idd.get_fields(oname)
            field_names = [unicode(f) for f in fields] if fields is not None else []
            lines = []
            for field, field_name in zip(idf_object[1:], field_names):
                field_val = u'{0},'.format(field)
                if len(field_val) >= 24:
                    field_val += '  '
                lines.append(u'    {0:<25}!- {1}'.format(field_val, field_name))
            s += u'\n'.join(lines)
            temp = s.rsplit(u',', 1)
            s = u';'.join(temp)
            s += u'\n\n'
        return s

    def save(self, idf_filename):
        with open(idf_filename, 'w') as idffile:
            idffile.write(unicode(self))

    def find(self, class_name, object_name=None, field_name=None):
        objs = []
        for idf_object in self.idf:
            if idf_object[0].upper() == class_name.upper():
                objs.append(idf_object)
        if object_name is None and field_name is None:
            return objs
        else:
            the_object = None
            name_index = self._idd.get_field_index(class_name, 'Name')
            for obj in objs:
                if obj[name_index].upper() == object_name.upper():
                    the_object = obj
            if field_name is None:
                return the_object
            elif field_name is not None and the_object is not None:
                field_index = self._idd.get_field_index(class_name, field_name)
                return the_object[field_index]
            else:
                return None

    def update(self, class_name, object_name, field_name, value):
        name_index = self._idd.get_field_index(class_name, 'Name')
        field_index = self._idd.get_field_index(class_name, field_name)
        objects = self.find(class_name)
        count = 0
        for obj in sorted(objects):
            if name_index is None or obj[name_index].upper() == object_name.upper():
                obj[field_index] = value
                count += 1
        return count

    def add(self, ep_object):
        self.idf.extend(ep_object)