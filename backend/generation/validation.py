__author__ = 'm5z'

import json
from datetime import datetime
import unicodedata
from ashrae import _ASHRAE_DEFAULTS
from climate_zones import _CLIMATE_ZONES

_BUILDING_TYPES = [u'medium_office']  # u'Small_Office', u'Warehouse', u'Residential'
_GEOMETRY_CONFIGURATIONS = [u'rectangle']  # u'Courtyard', u'L_Shape', u'H_Shape', u'T_Shape', u'U_Shape'
_ZONE_LAYOUTS = [u'five_zone']
_ROOF_STYLES = [u'flat', u'gable', u'hip']
_WALL_TYPES = [u'Steel_Frame_Non_Res', u'Metal_Building_Non_Res', u'Wood_Framed', u'Concrete_Non_Res']
_ROOF_TYPES = [u'IEAD_Non_Res', u'Attic_Roof_Non_Res']
_WINDOW_TYPES = [u'Reference', u'Single_Clear', u'Single_Bronze', u'Single_Clear_LowE', u'Double_Clear',
                 u'Double_Bronze', u'Double_Clear_LowE', u'Triple_Clear', u'Triple_Clear_LowE']
_COIL_TYPES = [u'electric', u'gas']
_HVAC_TYPES = [u'vav', u'psz_onoff', u'psz_cav']
_NIGHT_CYCLES = [u'CycleOnAny', u'CycleOnAnyZoneFansOnly', u'StayOff']
_WEEKEND_TYPES = [u'Saturday', u'Sunday', u'Weekend']
_ECONOMIZER_TYPES = [u'NoEconomizer', u'DifferentialDryBulb']
_BUILDING_AGES = [u'new2004', u'post1980']  # , u'pre1980']
_BUILDING_TYPES_DEFAULTS = {
    u'medium_office': {
        'number_of_floors': 3, 'plenums': True, 'roof_style': u"flat", 'wall_type': u"steel_frame_non_res",
        'roof_type': u"iead_non_res", 'south_wwr': 0.477, 'east_wwr': 0.477, 'north_wwr': 0.477, 'west_wwr': 0.477,
        'hvac_type': u"vav", 'heating_coil': u"Gas", 'has_reheat': True, 'cooling_cop': 3.23372055845678,
        'fan_efficiency': 0.5915, 'fan_static_pressure': 1109.648, 'ext_lighting_intensity': 14804, },
    u'small_office': {
        'number_of_floors': 1, 'plenums': False, 'roof_style': u"hip", 'wall_type': u"concrete_non_res",
        'roof_type': u"attic_roof_non_res", 'south_wwr': 0.477, 'east_wwr': 0.477, 'north_wwr': 0.477,
        'west_wwr': 0.477,
        'hvac_type': u"psz_cav", 'heating_coil': u"Gas", 'has_reheat': False, 'cooling_cop': 3.66668442928701,
        'fan_efficiency': 0.53625, 'fan_static_pressure': 622.0, 'ext_lighting_intensity': 2303, }}
_COMMON_DEFAULTS = {
    'climate_zone': u"5a", 'building_age': 2004, 'timestep': 6, 'floor_height': 3.9624, 'orientation': 0.,
    'geometry_configuration': u"rectangle", 'length1': 49.911, 'length2': 0., 'width1': 33.275, 'width2': 0.,
    'south_win_type': u"reference", 'east_win_type': u"reference", 'north_win_type': u"reference",
    'west_win_type': u"reference", 'end1': 0., 'end2': 0., 'offset1': 0., 'offset2': 0., 'offset3': 0.,
    'has_weekend_occupancy': True, 'weekend_occupancy_type': u"Saturday", 'weekday_start_time': u"06:00",
    'weekday_end_time': u"22:00", 'weekend_start_time': u"06:00", 'weekend_end_time': u"18:00",
    'gas_plug_intensity': 1.0, 'zone_layout': u"Five_Zone", 'reheat_coil': u"Electric", 'heating_efficiency': 0.8,
    'elec_plug_intensity': 10.76, 'int_lighting_intensity': 10.76, 'people_density': 18.58,
    'infiltration_per_ext_sur_area': 0.000302, 'oa_vent_per_person': 0.0125, 'oa_vent_per_area': 0.,
    'has_setback': True, 'has_night_cycle': True, 'night_cycle': u"CycleOnAny", 'has_dcv': False,
    'cooling_setback': 26.7, 'heating_setback': 15.6, 'cooling_setpoint': 24.0, 'heating_setpoint': 21.0,
    'use_mechanical_vent': False}

_OUTPUT_VARIABLES = [
    u'Output:Variable', u'Output:Meter', u'Output:SQLite', u'OutputControl:Table:Style', u"Output:Table:SummaryReports",
    u"Output:Table:Monthly", u"Output:Table:TimeBins", u"Output:VariableDictionary", u"Output:Surfaces:List",
    u"Output:Surfaces:Drawing", u"Output:Constructions", u"OutputControl:ReportingTolerances"]


class Validation(object):
    def __init__(self):
        self.cleaned_data = {}
        self.unsafe_data = {}

    def cleaned_inputs(self, unsafe_user_data):
        if isinstance(unsafe_user_data, dict):
            self.unsafe_data = unsafe_user_data
        else:
            self.unsafe_data = json.loads(unsafe_user_data)
        self.cleaned_data['building_type'] = self._clean_building_type()
        self._clean()
        return self.cleaned_data

    def _clean(self):
        self.cleaned_data['run_number'] = 1
        self.cleaned_data['output_variables'] = None

        self.cleaned_data['climate_zone'] = self._clean_collections('climate_zone', _CLIMATE_ZONES)
        self.cleaned_data['state'] = _CLIMATE_ZONES[self.cleaned_data['climate_zone']]['state']
        self.cleaned_data['city'] = _CLIMATE_ZONES[self.cleaned_data['climate_zone']]['city']
        self.cleaned_data['building_age'] = self._check_is_greater_or_equal_zero('building_age')
        self.cleaned_data['building_age_category'] = self._building_age_conversion(self.cleaned_data['building_age'])

        self.cleaned_data['glass_u_factor'] = self._check_defaults('glass_u_factor', use_ashrae_defaults=True)
        self.cleaned_data['glass_shgc'] = self._check_defaults('glass_shgc', use_ashrae_defaults=True)
        self.cleaned_data['glass_visible_transmittance'] = self._check_defaults('glass_visible_transmittance',
                                                                                use_ashrae_defaults=True)

        self.cleaned_data.update({
            'number_of_floors': self._check_is_greater_or_equal_zero('number_of_floors'),
            'timestep': self._check_is_greater_or_equal_zero('timestep'),
            'floor_height': self._check_is_greater_or_equal_zero('floor_height'),
            'plenums': self._check_is_bool('plenums'),
            'orientation': self._clean_orientation(),
            'geometry_configuration': self._clean_collections('geometry_configuration', _GEOMETRY_CONFIGURATIONS),
            'zone_layout': self._clean_collections('zone_layout', _ZONE_LAYOUTS),
            'roof_style': self._clean_collections('roof_style', _ROOF_STYLES),
            'wall_type': self._clean_collections('wall_type', _WALL_TYPES),
            'roof_type': self._clean_collections('roof_type', _ROOF_TYPES),
            'south_wwr': self._check_is_percentage('south_wwr'),
            'east_wwr': self._check_is_percentage('east_wwr'),
            'north_wwr': self._check_is_percentage('north_wwr'),
            'west_wwr': self._check_is_percentage('west_wwr'),
            'south_win_type': self._clean_collections('south_win_type', _WINDOW_TYPES),
            'east_win_type': self._clean_collections('east_win_type', _WINDOW_TYPES),
            'north_win_type': self._clean_collections('north_win_type', _WINDOW_TYPES),
            'west_win_type': self._clean_collections('west_win_type', _WINDOW_TYPES),
            'hvac_type': self._clean_collections('hvac_type', _HVAC_TYPES),
            'heating_coil': self._clean_collections('heating_coil', _COIL_TYPES),
            'has_reheat': self._check_is_bool('has_reheat'),
            'reheat_coil': self._clean_collections('reheat_coil', _COIL_TYPES),
            'heating_efficiency': self._check_is_percentage('heating_efficiency', use_ashrae_defaults=True),
            'cooling_cop': self._check_is_greater_or_equal_zero('cooling_cop', use_ashrae_defaults=True),
            'fan_efficiency': self._check_is_percentage('fan_efficiency'),
            'fan_static_pressure': self._check_is_greater_or_equal_zero('fan_static_pressure'),
            'elec_plug_intensity': self._check_is_greater_or_equal_zero('elec_plug_intensity'),
            'int_lighting_intensity': self._check_is_greater_or_equal_zero('int_lighting_intensity',
                                                                           use_ashrae_defaults=True),
            'ext_lighting_intensity': self._check_is_greater_or_equal_zero('ext_lighting_intensity',
                                                                           use_ashrae_defaults=True),
            'people_density': self._check_is_greater_or_equal_zero('people_density'),
            'infiltration_per_ext_sur_area': self._check_is_greater_or_equal_zero('infiltration_per_ext_sur_area',
                                                                                  use_ashrae_defaults=True),
            'oa_vent_per_person': self._check_is_greater_or_equal_zero('oa_vent_per_person'),
            'oa_vent_per_area': self._check_is_greater_or_equal_zero('oa_vent_per_area'),
            'length1': self._check_is_greater_or_equal_zero('length1'),
            'length2': self._check_is_greater_or_equal_zero('length2'),
            'width1': self._check_is_greater_or_equal_zero('width1'),
            'width2': self._check_is_greater_or_equal_zero('width2'),
            'end1': self._check_is_greater_or_equal_zero('end1'),
            'end2': self._check_is_greater_or_equal_zero('end2'),
            'offset1': self._check_is_greater_or_equal_zero('offset1'),
            'offset2': self._check_is_greater_or_equal_zero('offset2'),
            'offset3': self._check_is_greater_or_equal_zero('offset3'),
            'has_setback': self._check_is_bool('has_setback'),
            'has_night_cycle': self._check_is_bool('has_night_cycle'),
            'night_cycle': self._clean_collections('night_cycle', _NIGHT_CYCLES),
            'has_dcv': self._check_is_bool('has_dcv'),
            'cooling_setback': self._check_is_greater_or_equal_zero('cooling_setback'),
            'heating_setback': self._check_is_greater_or_equal_zero('heating_setback'),
            'cooling_setpoint': self._check_is_greater_or_equal_zero('cooling_setpoint'),
            'heating_setpoint': self._check_is_greater_or_equal_zero('heating_setpoint'),
            'has_weekend_occupancy': self._check_is_bool('has_weekend_occupancy'),
            'weekend_occupancy_type': self._clean_collections('weekend_occupancy_type', _WEEKEND_TYPES),
            'weekday_start_time': self._check_is_time('weekday_start_time'),
            'weekday_end_time': self._check_is_time('weekday_end_time'),
            'weekend_start_time': self._check_is_time('weekend_start_time'),
            'weekend_end_time': self._check_is_time('weekend_end_time'),
            'dhw_efficiency': self._check_is_percentage('dhw_efficiency', use_ashrae_defaults=True),
            'has_economizer': self._check_is_bool('has_economizer', use_ashrae_defaults=True),
            'economizer': self._clean_collections('economizer', _ECONOMIZER_TYPES, use_ashrae_defaults=True),
            'wall_insulation': self._check_is_greater_or_equal_zero('wall_insulation', use_ashrae_defaults=True),
            'roof_insulation': self._check_is_greater_or_equal_zero('roof_insulation', use_ashrae_defaults=True),
            'use_mechanical_vent': self._check_is_bool('use_mechanical_vent'), })

    def _check_is_greater_or_equal_zero(self, input_object, use_ashrae_defaults=False):
        if input_object in self.unsafe_data:
            data = self._check_is_number(input_object)
            if data < 0.:
                raise ValueError(u"Value (%s) must be greater than or equal to 0" % data)
            return data
        else:
            return self._check_defaults(input_object, use_ashrae_defaults)

    def _check_is_greater_than_zero(self, input_object, use_ashrae_defaults=False):
        if input_object in self.unsafe_data:
            data = self._check_is_number(input_object)
            if data > 0.:
                return data
            else:
                raise ValueError(u"Value (%s) must be greater than 0" % data)
        else:
            return self._check_defaults(input_object, use_ashrae_defaults)

    def _check_is_percentage(self, input_object, use_ashrae_defaults=False):
        if input_object in self.unsafe_data:
            data = self._check_is_number(input_object)
            if not 0. <= data <= 1.:
                raise ValueError(u"Value (%s) must be between 0 and 1" % data)
            return data
        else:
            return self._check_defaults(input_object, use_ashrae_defaults)

    def _check_is_string(self, input_object):
        data = self.unsafe_data[input_object]
        if not isinstance(data, basestring):
            raise TypeError(u"Parameter (%s) is not a string" % input_object)
        return data

    def _check_is_bool(self, input_object, use_ashrae_defaults=False):
        if input_object in self.unsafe_data:
            data = self.unsafe_data[input_object]
            if not isinstance(data, bool):
                try:
                    data = bool(data)
                except ValueError:
                    raise TypeError(u"Parameter (%s) is not a boolean" % input_object)
            return data
        else:
            return self._check_defaults(input_object, use_ashrae_defaults)

    def _check_is_number(self, input_object):
        data = self.unsafe_data[input_object]
        if not isinstance(data, int):
            if not isinstance(data, float):
                try:
                    data = float(data)
                except ValueError:
                    try:
                        data = unicodedata.numeric(data)
                    except (TypeError, ValueError):
                        raise TypeError(u"Parameter (%s) is not a float or integer" % input_object)
        return data

    def _clean_collections(self, input_object, list_collection, use_ashrae_defaults=False):
        if input_object in self.unsafe_data:
            input_value = self._check_is_string(input_object).lower()
            if input_value in map(unicode.lower, list_collection):
                return input_value
            else:
                error_msg_object = input_object.replace('_', ' ')
                raise ValueError((error_msg_object.capitalize() + u" (%s) is not one of valid " +
                                  error_msg_object + u"s (%s)") %
                                 (self.unsafe_data[input_object], ", ".join(list_collection)))
        else:
            return self._check_defaults(input_object, use_ashrae_defaults)

    def _check_is_time(self, input_object, use_ashrae_defaults=False):
        if input_object in self.unsafe_data:
            data = self.unsafe_data[input_object]
            if not isinstance(data, datetime):
                try:
                    data = datetime.strptime(data, u"%H:%M")
                except ValueError:
                    raise TypeError(u"Parameter (%s) is not a valid time" % input_object)
            return data.strftime(u"%H:%M")
        else:
            return self._check_defaults(input_object, use_ashrae_defaults)

    def _clean_building_type(self):
        if 'building_type' in self.unsafe_data:
            building_type = self._check_is_string('building_type').lower()
            if building_type in _BUILDING_TYPES:
                return building_type
            else:
                raise ValueError(u"Building type (%s) is not one of valid building types (%s)" %
                                 (self.unsafe_data['building_type'], ", ".join(_BUILDING_TYPES)))
        else:
            raise ValueError(u"Building type key/value pair (building_type) not found in inputs")

    def _clean_orientation(self):
        if 'orientation' in self.unsafe_data:
            data = self._check_is_number('orientation')
            if not 0. <= data <= 360.:
                raise ValueError(u"Value (%s) must be between 0 and 360" % data)
            return data
        else:
            return self._defaults('orientation')

    def _clean_output_variables(self):
        if 'output_variables' in self.unsafe_data:
            data = self.unsafe_data['output_variables']
            if not isinstance(data, list):
                raise TypeError(u"Parameter (%s) is not a list" % 'output_variables')

            if len(data) > 0:
                for output_variables in data:
                    if len(output_variables) > 0:
                        idf_object = output_variables[0]
                        if not isinstance(idf_object, basestring):
                            raise TypeError(u"Output variable (%s) is not a string" % idf_object)
                        if not idf_object.lower() in map(unicode.lower, _OUTPUT_VARIABLES):
                            raise ValueError(u"Output variable (%s) is not one of valid output variables (%s)" %
                                             (idf_object, ", ".join(_OUTPUT_VARIABLES)))
                    else:
                        raise ValueError(u"Nested list cannot be empty")

                return data
            else:
                raise ValueError(u"List cannot be empty")
        else:
            return None

    def _check_defaults(self, input_object, use_ashrae_defaults):
        if use_ashrae_defaults:
            return self._ashrae_defaults(input_object)
        else:
            return self._defaults(input_object)

    def _defaults(self, input_object):
        if input_object in _BUILDING_TYPES_DEFAULTS[self.cleaned_data['building_type']]:
            return _BUILDING_TYPES_DEFAULTS[self.cleaned_data['building_type']][input_object]
        if input_object in _COMMON_DEFAULTS:
            return _COMMON_DEFAULTS[input_object]
        raise NotImplementedError(u"Default value for (%s) not implemented" % input_object)

    def _ashrae_defaults(self, input_object):
        if input_object in _ASHRAE_DEFAULTS[self.cleaned_data['climate_zone']][
            self.cleaned_data['building_age_category']][self.cleaned_data['building_type']]:
            return _ASHRAE_DEFAULTS[self.cleaned_data['climate_zone']][
                self.cleaned_data['building_age_category']][self.cleaned_data['building_type']][input_object]
        if input_object in _ASHRAE_DEFAULTS[self.cleaned_data['climate_zone']][
            self.cleaned_data['building_age_category']][u'common']:
            return _ASHRAE_DEFAULTS[self.cleaned_data['climate_zone']][
                self.cleaned_data['building_age_category']][u'common'][input_object]
        return self._defaults(input_object)

    def _building_age_conversion(self, building_age):
        if building_age <= 1980:
            raise NotImplementedError(u"pre1980 building age is not implemented yet")
            #return u'pre1980'
        elif 1980 < building_age < 2004:
            return u'post1980'
        else:
            return u'new2004'