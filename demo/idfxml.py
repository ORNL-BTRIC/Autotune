#!/usr/bin/env python

#===  Autotune Library  ===#
import eplus
import idf
#==========================#
import csv
import xml.etree.ElementTree
import xml.dom.minidom


def tagconvert(s, toxml=True):
    replacements = [(' ', '_s_'), (':', '_C_'), ('?', '_q_'), ('/', '_S_'),
                    (',', '_c_'), ('(', '_p_'), (')', '_P_'), ('[', '_b_'),
                    (']', '_B_'), ('**', '_E_'), ('*', '_m_'), ('+', '_a_'),
                    ('=', '_e_'), ('100%', '_h_'), ('%', '_r_'), ('#', '_n_')]
    
    if not toxml:
        replacements.reverse()
    for idf, xml in replacements:
        if toxml:
            s = s.replace(idf, xml)
        else:
            s = s.replace(xml, idf)
    return s.strip()
    
    
def idd_to_xsd(idd):
    xmls = '<?xml version="1.0"?><xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
    xmls += '<xs:element name="EnergyPlus"><xs:complexType><xs:sequence>'
    for group in idd.groups:
        for obj in group.objects:
            req = ' minOccurs="0"' if not obj.required else ''
            xmls += '<xs:element name="{0}"{1} maxOccurs="unbounded"><xs:complexType><xs:sequence>'.format(tagconvert(str(obj)), req)
            fields = [obj.fields[f] for f in obj.fields]
            fields.sort(key=lambda x: x.position)
            for field in fields:
                req = ' minOccurs="0"' if not field.required else ''
                xmls += '<xs:element name="{0}"{1} maxOccurs="unbounded">'.format(tagconvert(str(field.name)), req)
                xmls += '</xs:element>'
            xmls += '</xs:sequence></xs:complexType></xs:element>'
    xmls += '</xs:sequence></xs:complexType></xs:element>'
    xmls += '</xs:schema>'
    return xmls
    
def idf_to_xml(idf):
    xmls = '<?xml version="1.0"?>'
    xmls += '<EnergyPlus xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="eplus.xsd">\n'
    for object in idf.idf:
        oname = object[0]
        xmls += '    <{0}>'.format(tagconvert(oname))
        fields = idf.idd.get_fields(oname)
        field_names = [f.name for f in fields] if fields is not None else []
        xmls += '\n' if len(field_names) > 0 else ''
        for field, field_name in zip(object[1:], field_names):
            field_value = ''
            if field is not None and len(field.strip()) > 0:
                field_value = field.strip()
            xmls += '        <{0}>{1}</{0}>\n'.format(tagconvert(field_name), field_value)
        xmls += '    ' if len(field_names) > 0 else ''
        xmls += '</{0}>\n'.format(tagconvert(oname))
    xmls += '</EnergyPlus>'
    return xmls

def xml_to_idf(xmlstr):
    idffile = idf.IDFFile()
    xmlroot = xml.etree.ElementTree.fromstring(xmlstr)
    for node in xmlroot.findall('*'):
        object = [tagconvert(node.tag, toxml=False)]
        for field in node.findall('*'):
            if field.text is not None:
                object.append(field.text.strip())
            else:
                object.append('')
        idffile.idf.append(object)
    return idffile

def xml_to_variables(xmlstr):
    def get_elements_with_attribute(parent_element, name, value=None):
        elements = []
        if parent_element is not None and parent_element.nodeType == parent_element.ELEMENT_NODE:
            if parent_element.hasAttribute(name):
                if value is None or parent_element.getAttribute(name) == value:
                    elements.append(parent_element)
            for node in parent_element.childNodes:
                e = get_elements_with_attribute(node, name, value)
                elements.extend(e)
        return elements
        
    def get_name_element(parent_element):
        if parent_element is not None and parent_element.nodeType == parent_element.ELEMENT_NODE:
            for node in parent_element.childNodes:
                if node.nodeType == node.ELEMENT_NODE and node.tagName == 'Name':
                    return node
        return None

    parameters = []
    xmldom = xml.dom.minidom.parseString(xmlstr)
    tunable_elements = get_elements_with_attribute(xmldom.documentElement, 'tuneType')
    for i, e in enumerate(tunable_elements):
        name_element = get_name_element(e.parentNode)
        object_name = tagconvert(str(e.parentNode.tagName), toxml=False) if name_element is None else str(" ".join(t.nodeValue for t in name_element.childNodes if t.nodeType == t.TEXT_NODE))
        legitimate_type = False
        p = {}
        p['Field'] = tagconvert(str(e.tagName), toxml=False)
        p['Object'] = object_name.strip()
        p['Class'] = tagconvert(str(e.parentNode.tagName), toxml=False)
        p['Type'] = str(e.getAttribute('tuneType'))
        p['Default'] = " ".join(t.nodeValue for t in e.childNodes if t.nodeType == t.TEXT_NODE).strip()
        if p['Type'] == 'integer':
            p['Minimum'] = int(e.getAttribute('tuneMin'))
            p['Maximum'] = int(e.getAttribute('tuneMax'))
            p['Default'] = int(p['Default'])
            legitimate_type = True
        elif p['Type'] == 'float':
            p['Minimum'] = float(e.getAttribute('tuneMin'))
            p['Maximum'] = float(e.getAttribute('tuneMax'))
            p['Default'] = float(p['Default'])
            legitimate_type = True
        if legitimate_type:
            p['Distribution'] = str(e.getAttribute('tuneDistribution')) if e.hasAttribute('tuneDistribution') else 'uniform'
            p['Group'] = str(e.getAttribute('tuneGroup')) if e.hasAttribute('tuneGroup') else ''
            p['Constraint'] = str(e.getAttribute('tuneConstraint')) if e.hasAttribute('tuneConstraint') else ''
            parameters.append(p)
    return eplus.EPlusVariableSet(parameters)    
    
def variables_to_xml(variables, xmlstr):
    xmlroot = xml.etree.ElementTree.fromstring(xmlstr)
    for variable in variables:
        if variable.idfobject == variable.idfclass:
            node = xmlroot.find('./{0}/{1}'.format(tagconvert(variable.idfclass), 
                                                   tagconvert(variable.idffield)))
        else:
            nodes = xmlroot.findall('./{0}'.format(tagconvert(variable.idfclass)))
            node = None
            for n in nodes:
                name = n.find('./Name')
                if name is not None and name.text.strip() == variable.idfobject:
                    node = n.find('./{0}'.format(tagconvert(variable.idffield)))
                    break
        if node is not None:
            node.set('tuneType', variable.type)
            node.set('tuneMin', str(variable.minimum))
            node.set('tuneMax', str(variable.maximum))
            if len(variable.distribution) > 0:
                node.set('tuneDistribution', variable.distribution)
            if len(variable.group) > 0:
                node.set('tuneGroup', variable.group)
            if len(variable.constraint.constraint) > 0:
                node.set('tuneConstraint', variable.constraint.constraint)
    return xml.etree.ElementTree.tostring(xmlroot)
    
def main():
    import argparse
    import getpass
    parser = argparse.ArgumentParser(description='converts between IDF and XML',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', help='the name of the file to convert')
    parser.add_argument('conversion', help='the type of conversion', choices=['idf2xml', 'xml2idf'], default='idf2xml')
    parser.add_argument('--varfile', help='the CSV file containing tuning variables', default=None)
    args = parser.parse_args()

    if args.conversion == 'idf2xml':
        xmlstr = None
        with open(args.filename, 'r') as idffile:
            i = idf.IDFFile(idffile)
            xmlstr = idf_to_xml(i)
        if args.varfile is not None:
            with open(args.varfile) as vfile:
                reader = csv.DictReader(vfile)
                vars = eplus.EPlusVariableSet(reader)
                xmlstr = variables_to_xml(vars, xmlstr)
        with open('{}.xml'.format(args.filename), 'w') as xmlfile:
            xmlfile.write(xmlstr)
    elif args.conversion == 'xml2idf':
        xmlstr = ''
        with open(args.filename) as xmlfile:
            xmlstr = xmlfile.read()
        i = xml_to_idf(xmlstr)
        with open('{}.idf'.format(args.filename), 'w') as idffile:
            idffile.write(str(i))
        vars = xml_to_variables(xmlstr)
        with open('{}.csv'.format(args.filename), 'wb') as paramfile:
            paramfile.write(str(vars))
    
    

if __name__ == '__main__':
    main()
