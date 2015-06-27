__author__ = 'Mark Adams <adamsmb@ornl.gov>'

from idf import IDF
import building
import geometry
import validation
import output_variables


def generate_idf_string(unsafe_user_inputs):
    cleaned_inputs = validation.Validation().cleaned_inputs(unsafe_user_inputs)

    unicode_idf_file = unicode(IDF(idf_list=building.Building(_geometry_configurations(cleaned_inputs),
                                                              cleaned_inputs).output_EP_list()))
    return unicode_idf_file


def default_output_variables(unsafe_building_type):
    return output_variables.output_variables(unsafe_building_type)


def _geometry_configurations(cleaned_inputs):
    if cleaned_inputs['geometry_configuration'] == u"rectangle":
        return geometry.create_rectangle_zone(cleaned_inputs['number_of_floors'],
                                              floor_height=cleaned_inputs['floor_height'],
                                              plenums=cleaned_inputs['plenums'],
                                              five_zone_plenum=False,
                                              length1=cleaned_inputs['length1'],
                                              width1=cleaned_inputs['width1'],
                                              roof_type=cleaned_inputs['roof_style'])