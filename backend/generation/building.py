__author__ = 'm5z'

import numpy as np
import swh
import schedules
import constructions
import building_types
import utilities
import hvac
import output_variables
import climate_zones


class Building(object):
    def __init__(self, building_geometry_vertices, idf_generation_inputs, building_fenestration_vertices=None):
        self._zones = []
        self.building_info = {'num_of_floors': 1}
        self.floors = {}
        self.idf_generation_inputs = idf_generation_inputs
        self.calculate_zones(building_geometry_vertices)

    def calculate_zones(self, vertices):
        #zone_num = 1
        #for zone_num in range(len(vertices)):
        #    self._zones.append(Zone(vertices[surf_num], self.zone_info, self.idf_generation_inputs, zone_num))
        #    zone_num += 1
        self._zones = [Zone(vertices[zone_num], zone_num + 1, self.building_info, self.idf_generation_inputs)
                       for zone_num in range(len(vertices))]
        self.update_surfaces()

    def update_adjacency(self):
        for zone in self._zones:
            for surface in zone.surfaces:
                adjacency = self.check_adjacency(surface)
                has_adjacent = adjacency[0]
                if has_adjacent:
                    surface.adjacent_surface = adjacency[1]

        for zone in self._zones:
            is_interior_zone = []
            for surface in zone.surfaces:
                if surface.adjacent_surface is None:
                    adjacency = self.check_offset_adjacency(surface)
                    has_adjacent = adjacency[0]
                    if has_adjacent:
                        surface.adjacent_surface = adjacency[1]
                else:
                    has_adjacent = True

                if has_adjacent:
                    if surface.is_wall:
                        is_interior_zone.append(True)
                else:
                    if surface.is_wall:
                        is_interior_zone.append(False)
                surface.update_adjacent_surface()
            zone.update_zone_location(all(is_interior_zone))

    def check_adjacency(self, surface):
        has_adjacent = False
        adjacent_surface = None
        for adjacency_zone in self._zones:
            for adjacent in adjacency_zone.surfaces:
                # TODO: Need to check if any surface is above and parallel but not directly or offset adjacent

                # check if directly above
                # if not directly above, check directly above but offset
                # if not offset, check if any surface is above that is coplanar (building within building)

                surface_check = adjacent.vertices[::-1]
                is_directly_adjacent = np.array_equal(surface.vertices, surface_check)
                if is_directly_adjacent:
                    has_adjacent = is_directly_adjacent
                    adjacent_surface = adjacent

        return [has_adjacent, adjacent_surface]

    # TODO: Need to add wall offset check eventually (maybe for warehouse model)
    def check_offset_adjacency(self, surface):
        has_adjacent = False
        adjacent_surface = None
        offset_check = []
        if surface.is_wall:
            pass
        else:
            surface_height = list(set(surface.vertices[:, 2]))[0]
        for adjacency_zone in self._zones:
            for adjacent in adjacency_zone.surfaces:
                #if adjacent.adjacent_surface is None:
                is_parallel = np.array_equal(np.absolute(surface.cross_vector),
                                             np.absolute(adjacent.cross_vector))
                is_same_surface = np.array_equal(surface.vertices, adjacent.vertices)
                if is_parallel and not is_same_surface:
                    if surface.is_wall:
                        pass
                        # maybe check translation of two surfaces? that should be offset
                    else:
                        surface_check = adjacent.vertices[::-1, :2]
                        surface_verts = surface.vertices[:, :2]
                        is_offset_adjacent = np.array_equal(surface_verts, surface_check)
                        if is_offset_adjacent:
                            translation = adjacent.vertices[::-1] - surface.vertices
                            offset_float = list(set(translation[:, 2]))[0]
                            adjacent_height = list(set(adjacent.vertices[:, 2]))[0]
                            offset = {'translation': translation, 'offset': offset_float,
                                      'is_offset_adjacent': True, 'adjacent_vertices': adjacent.vertices,
                                      'adjacent_object': adjacent, 'adjacent_height': adjacent_height}
                            offset_check.append(offset)

        is_lowest_floor = all([adjacent['offset'] > 0. for adjacent in offset_check])
        is_highest_ceiling = all([adjacent['offset'] < 0. for adjacent in offset_check])
        if not is_lowest_floor and not is_highest_ceiling:
            if surface.is_ceiling:
                adjacent_index = [n for n, i in enumerate(offset_check) if i['offset'] > 0.][0]
                adjacent_surface = offset_check[adjacent_index]['adjacent_object']
                surface.is_offset_adjacent = offset_check[adjacent_index]['is_offset_adjacent']
                surface.offset = offset_check[adjacent_index]['offset']
                adjacent_surface.is_offset_adjacent = offset_check[adjacent_index]['is_offset_adjacent']
                adjacent_surface.offset = -offset_check[adjacent_index]['offset']
            elif surface.is_floor:
                reverse_offset_check = offset_check[::-1]
                adjacent_index = [n for n, i in enumerate(reverse_offset_check) if i['offset'] < 0.][0]
                adjacent_surface = reverse_offset_check[adjacent_index]['adjacent_object']
                surface.is_offset_adjacent = reverse_offset_check[adjacent_index]['is_offset_adjacent']
                surface.offset = reverse_offset_check[adjacent_index]['offset']
                #adjacent_surface.is_offset_adjacent = reverse_offset_check[adjacent_index]['is_offset_adjacent']
                #adjacent_surface.offset = -reverse_offset_check[adjacent_index]['offset']

            has_adjacent = True
        return [has_adjacent, adjacent_surface]

    def update_surfaces(self):
        self.update_adjacency()
        #zone_counter = 1
        for zone in self._zones:
            zone.update_zone_info()

        all_zone_abs_heights = []
        all_plenum_abs_heights = []
        for zone in self._zones:
            if not zone.zone_info['is_plenum']:
                all_zone_abs_heights.append(zone.zone_info['absolute_zone_height'])
            else:
                all_plenum_abs_heights.append(zone.zone_info['absolute_zone_height'])
        per_flr_zn_abs_heights = set(all_zone_abs_heights)
        #per_flr_pl_abs_heights = set(all_plenum_abs_heights)
        total_num_zn_floors = len(per_flr_zn_abs_heights)
        #total_num_pl_floors = len(per_flr_pl_abs_heights)
        # might need to change with attic
        #if total_num_zn_floors == total_num_pl_floors:
        self.building_info['num_of_floors'] = total_num_zn_floors

        all_floors = []
        for zone in self._zones:
            for surface in zone.surfaces:
                if surface.is_ceiling and not surface.zone_info['is_plenum']:
                    zone_height = surface.zone_info['zone_height']
                    plenum_height = 0.
                    if surface.adjacent_surface is not None and surface.adjacent_surface.zone_info['is_plenum']:
                        plenum_height = surface.adjacent_surface.zone_info['zone_height']
                    floor_height = zone.zone_info['floor_to_floor_height'] = zone_height + plenum_height
                    if zone.zone_info['absolute_zone_height'] < floor_height:
                        zone.zone_info['floor_num'] = int(
                            np.ceil(zone.zone_info['absolute_zone_height'] / floor_height))
                    else:
                        zone.zone_info['floor_num'] = int(
                            np.round(zone.zone_info['absolute_zone_height'] / floor_height))
                elif surface.is_floor and surface.zone_info['is_plenum']:
                    zone_height = 0.
                    plenum_height = surface.zone_info['zone_height']
                    if surface.adjacent_surface is not None and not surface.adjacent_surface.zone_info['is_plenum']:
                        zone_height = surface.adjacent_surface.zone_info['zone_height']
                    floor_height = zone.zone_info['floor_to_floor_height'] = zone_height + plenum_height
                    if zone.zone_info['absolute_zone_height'] < floor_height:
                        zone.zone_info['floor_num'] = int(
                            np.ceil(zone.zone_info['absolute_zone_height'] / floor_height))
                    else:
                        zone.zone_info['floor_num'] = int(
                            np.round(zone.zone_info['absolute_zone_height'] / floor_height))
            if not zone.zone_info['is_attic']:
                all_floors.append(zone.zone_info['floor_num'])

            if zone.zone_info['is_attic']:
                zone.zone_info['num_zone_per_floor'] = 1
                zone.zone_info['zone_num'] = 1
                #ceiling_counter = 0
                #floor_counter = 0
                #for surface in zone.surfaces:
                #        if surface.adjacent_surface is None and surface.is_ceiling:
                #            ceiling_counter += 1
                #            surface.surface_num = ceiling_counter
                #        elif surface.adjacent_surface is None and surface.is_floor:
                #            surface.is_soffit = True
                #            floor_counter += 1
                #            surface.surface_num = floor_counter
                #        elif not surface.adjacent_surface is None and surface.is_floor:
                #            floor_counter += 1
                #            surface.surface_num = floor_counter

        unique_floors = list(set(all_floors))

        for floor in unique_floors:
            self.floors[floor] = []
            for zone in self._zones:
                if zone.zone_info['floor_num'] == floor:
                    self.floors[floor].append(zone)
            zones = self.floors[floor]
            zone_counter = 0
            #surface_counter = 0
            plenum_counter = 0
            for zone in zones:
                if not zone.zone_info['is_plenum']:
                    zone_counter += 1
                    zone.zone_info['zone_num'] = zone_counter
                else:
                    plenum_counter += 1
                    zone.zone_info['zone_num'] = plenum_counter
                    #for surface in zone.surfaces:
                    #    if surface.adjacent_surface is None and surface.is_ceiling:
                    #        surface_counter += 1
                    #        surface.surface_num = surface_counter

            for zone in zones:
                if zone.zone_info['is_plenum']:
                    zone.zone_info['num_zone_per_floor'] = plenum_counter
                else:
                    zone.zone_info['num_zone_per_floor'] = zone_counter

        max_floor = max(self.floors)
        min_floor = min(self.floors)
        for floor in self.floors:
            is_max_floor = np.allclose(floor, max_floor)
            is_min_floor = np.allclose(floor, min_floor)
            if not is_max_floor and not is_min_floor:
                ceiling_zone_multiplier = []
                floor_zone_multiplier = []
                for zone in self.floors[floor]:
                    for surface in zone.surfaces:
                        if surface.is_ceiling and surface.is_offset_adjacent:
                            ceiling_zone_multiplier.append(
                                abs(surface.offset) / zone.zone_info['floor_to_floor_height'])
                        elif surface.is_floor and surface.is_offset_adjacent:
                            floor_zone_multiplier.append(abs(surface.offset) / zone.zone_info['floor_to_floor_height'])
                ceiling_zone_multiplier = list(set(ceiling_zone_multiplier))
                floor_zone_multiplier = list(set(floor_zone_multiplier))
                zone_multiplier = 1.0
                if len(ceiling_zone_multiplier) == 0:
                    zone_multiplier += 0.
                else:
                    zone_multiplier += ceiling_zone_multiplier[0]

                if len(floor_zone_multiplier) == 0:
                    zone_multiplier += 0.
                else:
                    zone_multiplier += floor_zone_multiplier[0]

                for zone in self.floors[floor]:
                    zone.zone_info['zone_multiplier'] = zone_multiplier

    def output_EP_list(self):
        EP_building = [building_types.common(self.idf_generation_inputs, self.floors),
                       hvac.output_hvac_list(self.floors, self.idf_generation_inputs),
                       constructions.all_constructions(self.idf_generation_inputs),
                       swh.swh_system(self.floors, self.idf_generation_inputs),
                       schedules.all_schedules(self.idf_generation_inputs),
                       utilities.output_utilities()]
        if self.idf_generation_inputs['output_variables'] is None:
            EP_building.extend(output_variables._output_variables(self.idf_generation_inputs['building_type']))
        else:
            EP_building.extend(self.idf_generation_inputs['output_variables'])

        [EP_building.append(climate_zones._CLIMATE_ZONES[self.idf_generation_inputs['climate_zone']]['tmy2'][weather])
         for weather in climate_zones._CLIMATE_ZONES[self.idf_generation_inputs['climate_zone']]['tmy2']]

        EP_building.extend([zone.output_zone_list() for zone in self._zones])
        return EP_building


class Zone(object):
    def __init__(self, vertices, zone_num, building_info, idf_generation_inputs):
        self.zone_info = {'zone_num': zone_num, 'zone_type': u"zn", 'zone_location': None,
                          'floor_level': None, 'floor_num': 1, 'zone_height': 0., 'absolute_zone_height': 0.,
                          'is_plenum': False, 'is_interior_zone': False,
                          'num_zone_per_floor': 5, 'floor_to_floor_height': 0., 'zone_multiplier': 1.0,
                          'is_attic': False}
        self.building_info = building_info
        self.idf_generation_inputs = idf_generation_inputs
        self.zone_floor_area = 0.
        self.surfaces = []
        self.init_zone_name(vertices)
        self.calculate_surfaces(vertices)
        self.calc_zone_floor_area()

    def init_zone_name(self, vertices):
        for surface_num in range(len(vertices)):
            surface_vertices = vertices[surface_num]
            num_of_vertices = len(vertices[surface_num])
            for i in range(num_of_vertices - 1):
                zone_height = surface_vertices[i][2] - surface_vertices[i + 1][2]
                if abs(zone_height) > self.zone_info['zone_height']:  # self.zone_height:
                    if zone_height < 0:
                        self.zone_info['absolute_zone_height'] = surface_vertices[i + 1][2]
                    else:
                        self.zone_info['absolute_zone_height'] = surface_vertices[i][2]
                    self.zone_info['zone_height'] = abs(zone_height)
                    break

    def calc_zone_floor_area(self):
        area = 0.
        for surface in self.surfaces:
            if surface.is_floor:
                area = poly_area(surface.vertices)
                break
        self.zone_floor_area = area

    def update_zone_info(self):
        determined_zone_type = False
        #probable_zone_heights = []
        #probable_plenum_heights = []
        #probable_zone_height = 0.
        #probable_plenum_height = 0.
        is_zone = []
        #plenum_zone_num = []
        is_interior_zone = []
        floor_adjacnecies = []
        has_angled_surface = []
        for surface in self.surfaces:
            if surface.adjacent_surface is None:
                has_adjacent = False
            else:
                has_adjacent = True

            if has_adjacent and (surface.is_floor or surface.is_ceiling):
                equal_heights = np.allclose(surface.zone_info['zone_height'],
                                            surface.adjacent_surface.zone_info['zone_height'])
                if not equal_heights:
                    surface_larger_height = surface.zone_info['zone_height'] > surface.adjacent_surface.zone_info[
                        'zone_height']
                    surface_lower_abs_height = \
                        surface.zone_info['absolute_zone_height'] < surface.adjacent_surface.zone_info[
                            'absolute_zone_height']
                    surface_higher_abs_height = \
                        surface.zone_info['absolute_zone_height'] > surface.adjacent_surface.zone_info[
                            'absolute_zone_height']

                    if surface_larger_height and surface_lower_abs_height and surface.is_ceiling:
                        is_zone.append(True)
                        #probable_zone_heights.append(surface.zone_info['zone_height'])
                        #probable_plenum_heights.append(surface.adjacent_surface.zone_info['zone_height'])
                        #probable_absolute_height = surface.adjacent_surface.zone_info['absolute_zone_height']
                    elif surface_larger_height and surface_higher_abs_height and surface.is_floor:
                        is_zone.append(True)
                        #probable_zone_heights.append(surface.zone_info['zone_height'])
                        #probable_plenum_heights.append(surface.adjacent_surface.zone_info['zone_height'])
                        #probable_absolute_height = surface.adjacent_surface.zone_info['absolute_zone_height']
                    else:
                        is_zone.append(False)
                        #probable_plenum_heights.append(surface.zone_info['zone_height'])
                        #probable_zone_heights.append(surface.adjacent_surface.zone_info['zone_height'])
                        #probable_absolute_height = surface.zone_info['absolute_zone_height']
                        #if surface.is_floor:
                        #    plenum_zone_num.append(surface.adjacent_surface.zone_info['zone_num'])
                else:
                    is_zone.append(True)
                    #probable_zone_heights.append(surface.zone_info['zone_height'])
                    #probable_plenum_heights.append(surface.adjacent_surface.zone_info['zone_height'])
                if surface.is_floor:
                    floor_adjacnecies.append(True)
                if surface.is_angled_surface:
                    has_angled_surface.append(True)
                determined_zone_type = True
            elif has_adjacent and not (surface.is_floor or surface.is_ceiling):
                is_interior_zone.append(True)
                if surface.is_angled_surface:
                    has_angled_surface.append(True)
            elif not has_adjacent and (surface.is_floor or surface.is_ceiling):
                if surface.is_floor:
                    floor_adjacnecies.append(False)
                    determined_zone_type = True
                if surface.is_angled_surface:
                    has_angled_surface.append(True)
                    is_interior_zone.append(False)
            elif not has_adjacent and not (surface.is_floor or surface.is_ceiling):
                is_interior_zone.append(False)
                if surface.is_angled_surface:
                    has_angled_surface.append(True)

            surface.update_adjacent_surface()

        self.update_zone_location(all(is_interior_zone))

        if determined_zone_type:
            #if len(probable_zone_heights) > 0 and all(probable_zone_heights):
            #    probable_zone_height = probable_zone_heights[0]
            #if len(probable_plenum_heights) > 0 and all(probable_plenum_heights):
            #    probable_plenum_height = probable_plenum_heights[0]
            #probable_floor_height = probable_zone_height + probable_plenum_height

            #if has_plenum:
            #    self.floor_num = int(probable_absolute_height // probable_floor_height)
            #else:
            #floor_num = int(probable_absolute_height // probable_floor_height)
            #self.zone_info['floor_num'] = floor_num
            #if floor_num > self.building_info['num_of_floors']:
            #    self.building_info['num_of_floors'] = floor_num

            if all(is_zone):
                if any(has_angled_surface) and (all(floor_adjacnecies) or any(floor_adjacnecies)):
                    self.zone_info['is_attic'] = True
                    self.zone_info['is_plenum'] = False
                    self.zone_info['zone_type'] = u"attic"
                else:
                    self.zone_info['zone_type'] = u"zn"
                    self.zone_info['is_plenum'] = False
            else:
                self.zone_info['zone_type'] = u"pl"
                self.zone_info['is_plenum'] = True

    def zone_name(self):
        #self.zone_name = u"_".join(filter(None, [self.zone_location, self.floor_level, self.zone_type,
        #                                         unicode(self.zone_num)]))
        if self.zone_info['num_zone_per_floor'] != 1:
            return u"_".join(filter(None, [self.zone_info['zone_location'], u"flr",
                                           unicode(self.zone_info['floor_num']), self.zone_info['zone_type'],
                                           unicode(self.zone_info['zone_num'])]))
        else:
            return u"_".join(filter(None, [u"flr", unicode(self.zone_info['floor_num']), self.zone_info['zone_type']]))

    def calculate_surfaces(self, vertices):
        #self.surfaces = [Surface(vertices[surface_num], self.zone_name, self.zone_num, self.zone_height,
        #                         self.zone_height_absolute) for surface_num in range(len(vertices))]
        surface_num = 1
        for surf_num in range(len(vertices)):
            self.surfaces.append(Surface(vertices[surf_num], self.zone_info, self.idf_generation_inputs, surface_num))
            surface_num += 1
            #self.surfaces = [Surface(vertices[surface_num], self.zone_info, self.idf_generation_inputs)
            #                 for surface_num in range(len(vertices))]

    #def update_floor_level(self):
    #    self.zone_info['floor_level'] = self.floor_num_to_string(self.zone_info['floor_num'])

    #def floor_num_to_string(self, floor_num):
    #    if floor_num == 1:
    #        return u"bot"
    #    elif floor_num == self.building_info['num_of_floors']:
    #        return u"top"
    #    else:
    #        return u"mid"

    def update_zone_location(self, is_interior_zone):
        #self.is_interior_zone = is_interior_zone
        self.zone_info['is_interior_zone'] = is_interior_zone
        if is_interior_zone:
            #self.zone_location = u'core'
            self.zone_info['zone_location'] = u'core'
        else:
            #self.zone_location = u'perimeter'
            self.zone_info['zone_location'] = u'perimeter'

    #def all_surfaces_complete(self):
    #    for surface in self.surfaces:
    #        if not surface.is_complete_surface():
    #            return False
    #    return True

    def create_fenestration(self, idf_generation_inputs):
        fenestration = []
        if not self.zone_info['is_plenum']:
            for surface in self.surfaces:
                if surface.is_wall and surface.is_external:
                    if 45 < surface.angle <= 135:
                        scale_factor = idf_generation_inputs['south_wwr']
                        window_construction = idf_generation_inputs['south_win_type']
                    elif 315 < surface.angle <= 360 or 0 <= surface.angle <= 45:
                        scale_factor = idf_generation_inputs['east_wwr']
                        window_construction = idf_generation_inputs['east_win_type']
                    elif 225 < surface.angle <= 315:
                        scale_factor = idf_generation_inputs['north_wwr']
                        window_construction = idf_generation_inputs['north_win_type']
                    elif 135 < surface.angle <= 225:
                        scale_factor = idf_generation_inputs['west_wwr']
                        window_construction = idf_generation_inputs['west_win_type']
                    else:
                        raise ValueError(u"Surface angle (%s) is invalid" % surface.angle)
                        #surface_centroid = calculate_polygon_centroid(surface.vertices)
                    #fenestration_vertices = np.array([scale_factor, scale_factor, scale_factor]) * \
                    #    np.array(surface.vertices)
                    #fenestration_centroid = calculate_polygon_centroid(fenestration_vertices)
                    #translation = surface_centroid - fenestration_centroid
                    #f_c = fenestration_vertices + translation
                    f_c = scale_polygon(surface.vertices, scale_factor)

                    fenestration.append([u"FenestrationSurface:Detailed", surface.surface_name() + u"_Window",
                                         u"Window", window_construction, surface.surface_name(), u"", u"autocalculate",
                                         u"", u"", u"1.0000", u"4",
                                         unicode(f_c[0, 0]), unicode(f_c[0, 1]), unicode(f_c[0, 2]),
                                         unicode(f_c[1, 0]), unicode(f_c[1, 1]), unicode(f_c[1, 2]),
                                         unicode(f_c[2, 0]), unicode(f_c[2, 1]), unicode(f_c[2, 2]),
                                         unicode(f_c[3, 0]), unicode(f_c[3, 1]), unicode(f_c[3, 2])])
        return fenestration

    def create_zone_list(self):
        zone = []
        # zone object
        zone.append([u"Zone", self.zone_name(), u"0.0000", u"0.0000", u"0.0000", u"0.0000", u"1",
                     self.zone_info['zone_multiplier'], u"", u"", u"autocalculate", u"", u"",
                     (u"No" if self.zone_info['is_plenum'] or self.zone_info['is_attic'] else u"Yes")])
        # zone surfaces
        zone.extend([surface.output_surface_list() for surface in self.surfaces])
        # zone fenestrations
        zone.extend(self.create_fenestration(self.idf_generation_inputs))
        # zone internal mass (zones only)
        if not self.zone_info['is_plenum'] and not self.zone_info['is_attic']:
            zone.append([u"InternalMass", self.zone_name() + u"_Internal Mass", u"InteriorFurnishings",
                         self.zone_name(), unicode(self.zone_floor_area)])
            # electric equipment object
            zone.append(
                [u"ElectricEquipment", self.zone_name() + u"_PlugMisc_Equip", self.zone_name(), u"BLDG_EQUIP_SCH",
                 u"Watts/Area", u"", unicode(self.idf_generation_inputs['elec_plug_intensity']), u"", u"0.0000",
                 u"0.5000", u"0.0000", u"MiscPlug"])
            # interior lights object
            zone.append([u"Lights", self.zone_name() + u"_Lights", self.zone_name(), u"BLDG_LIGHT_SCH",
                         u"Watts/Area", u"", unicode(self.idf_generation_inputs['int_lighting_intensity']), u"",
                         u"0.4000",
                         u"0.4000", u"0.2000", u"1.0000", u"General", u"No"])
            # people object
            zone.append([u"People", self.zone_name() + u"_People", self.zone_name(), u"BLDG_OCC_SCH",
                         u"Area/Person", u"", u"", unicode(self.idf_generation_inputs['people_density']), u"0.3000",
                         u"autocalculate", u"ACTIVITY_SCH", u"", u"No",
                         u"ZoneAveraged", u"", u"WORK_EFF_SCH", u"CLOTHING_SCH", u"AIR_VELO_SCH", u"FANGER"])
        if not self.zone_info['is_attic']:
            # zone infiltration design flow rate object
            zone.append([u"ZoneInfiltration:DesignFlowRate", self.zone_name() + u"_Infiltration", self.zone_name(),
                         u"INFIL_QUARTER_ON_SCH",
                         u"Flow/ExteriorArea", u"", u"",
                         unicode(self.idf_generation_inputs['infiltration_per_ext_sur_area']), u"", u"1.0000",
                         u"0.0000",
                         u"0.0000", u"0.0000"])
        return zone

    def output_zone_list(self):
        return self.create_zone_list()

        #def output_surface_list(self):
        #zone = [u"zone", self.zone_name(), u"0.0000", u"0.0000", u"0.0000", u"1", u"Zone_Multiplier",
        #        u"", u"", u"autocalculate", u"", u"", (u"no" if self.zone_info['is_plenum'] else u"yes")]
        #return [surface.output_surface_list() for surface in self.surfaces]
        #zone.extend(surfaces)
        #return zone


class Surface(object):
    def __init__(self, vertices, zone_info, idf_generation_inputs, surface_num):
        self.zone_info = zone_info
        self.surface_type = None
        self.surface_num = surface_num
        self.construction_name = None
        self.outside_boundary_condition = None
        self.obc_object = None
        self.adjacent_surface = None
        self.is_offset_adjacent = False
        self.offset = 0.
        self.sun_exposure = None
        self.wind_exposure = None
        self.num_of_vertices = unicode(len(vertices))
        self.vertices = np.array(vertices)
        self.is_external = False
        self.is_wall = False
        self.is_ceiling = False
        self.is_roof = False
        self.is_soffit = False
        self.is_floor = False
        self.surface_angle = None
        self._is_complete = False
        self.x_angle = None
        self.y_angle = None
        self.z_angle = None
        self.angle = None
        self.is_angled_surface = False
        #self.z_dir = None
        self.cross_vector = None
        self.idf_generation_inputs = idf_generation_inputs

        self.find_angle(self.vertices)
        self.calculate_surface()

    def surface_name(self):
        if self.zone_info['num_zone_per_floor'] != 1:
        #if not self.zone_info['is_plenum']:
            return u"_".join(filter(None, [self.zone_info['zone_location'], u"flr",
                                           unicode(self.zone_info['floor_num']), self.zone_info['zone_type'],
                                           unicode(self.zone_info['zone_num']), self.surface_type, self.surface_angle]))
        else:
            if self.adjacent_surface is None:
                return u"_".join(filter(None, [self.zone_info['zone_location'], u"flr",
                                               unicode(self.zone_info['floor_num']),
                                               self.zone_info['zone_type'], None if self.surface_num is None else
                    unicode(self.surface_num), self.surface_type, self.surface_angle]))
            elif self.zone_info['is_attic']:
                return u"_".join(filter(None, [self.adjacent_surface.zone_info['zone_location'], u"flr",
                                               unicode(self.zone_info['floor_num']),
                                               self.zone_info['zone_type'], None if self.surface_num is None else
                    unicode(self.surface_num), self.surface_type, self.surface_angle]))
            else:
                return u"_".join(filter(None, [self.adjacent_surface.zone_info['zone_location'],
                                               u"flr", unicode(self.zone_info['floor_num']),
                                               self.zone_info['zone_type'],
                                               #unicode(self.adjacent_surface.zone_info['zone_num']), self.surface_type,
                                               unicode(self.surface_num), self.surface_type,
                                               self.surface_angle]))

    def zone_name(self):
        if self.zone_info['num_zone_per_floor'] != 1:
            return u"_".join(filter(None, [self.zone_info['zone_location'], u"flr",
                                           unicode(self.zone_info['floor_num']), self.zone_info['zone_type'],
                                           unicode(self.zone_info['zone_num'])]))
        else:
            return u"_".join(filter(None, [u"flr", unicode(self.zone_info['floor_num']), self.zone_info['zone_type']]))

    def update_adjacent_surface(self):
        if self.adjacent_surface is None:
            self.outside_boundary_condition = u"Outdoors"
            self.sun_exposure = u"SunExposed"
            self.wind_exposure = u"WindExposed"
            self.obc_object = u""
            self.is_external = True

            if self.is_ceiling or self.is_roof:
                self.surface_type = u"roof"
                self.is_roof = True

            if self.is_floor:
                if self.is_soffit:
                    self.surface_type = u"soffit"
                else:
                    self.outside_boundary_condition = u"Ground"
                    self.sun_exposure = u"NoSun"
                    self.wind_exposure = u"NoWind"
        else:
            self.outside_boundary_condition = u"Surface"
            self.obc_object = self.adjacent_surface.surface_name()
            self.is_external = False
            self.sun_exposure = u"NoSun"
            self.wind_exposure = u"NoWind"

    def update_construction_names(self):
        if not self.is_external and not self.adjacent_surface is None:
            if self.is_ceiling:
                if self.adjacent_surface.zone_info['is_attic'] and \
                                self.adjacent_surface.zone_info['absolute_zone_height'] > 0:
                    self.construction_name = u"attic_floor_non_res"
                elif not self.adjacent_surface.zone_info['is_plenum']:
                    self.construction_name = u'INT-FLOOR-UNDERSIDE'
                elif self.adjacent_surface.zone_info['is_plenum']:
                    self.construction_name = u'DropCeiling'
                else:
                    self.construction_name = u'!!!Error_Interior_Ceiling_Construction!!!'
            elif self.is_floor:
                if self.zone_info['is_attic'] and self.zone_info['absolute_zone_height'] > 0:
                    self.construction_name = u"attic_floor_non_res"
                elif not self.zone_info['is_plenum']:
                    self.construction_name = u'INT-FLOOR-TOPSIDE'
                elif self.zone_info['is_plenum']:
                    self.construction_name = u'DropCeiling'
                else:
                    self.construction_name = u'!!!Error_Interior_Floor_Construction!!!'
            else:
                self.construction_name = u'int-walls'
        else:
            if self.is_ceiling:
                #self.construction_name = u'IEAD Non-res Roof'
                if self.zone_info['is_attic'] and self.zone_info['absolute_zone_height'] > 0:
                    self.construction_name = u"attic_roof_non_res"
                else:
                    self.construction_name = self.idf_generation_inputs['roof_type']
            elif self.is_floor:
                if self.zone_info['is_attic'] and self.zone_info['absolute_zone_height'] > 0:
                    self.construction_name = u"attic_floor_non_res"
                else:
                    self.construction_name = u'ext-slab'
            else:
                #self.construction_name = u'Steel Frame Non-res Ext Wall'
                self.construction_name = self.idf_generation_inputs['wall_type']

    def output_surface_list(self):
        #if not self.is_complete_surface():
        #    return None
        self.update_adjacent_surface()
        self.update_construction_names()
        surface = [u"BuildingSurface:Detailed", self.surface_name(), self.surface_type, self.construction_name,
                   self.zone_name(), self.outside_boundary_condition, self.obc_object, self.sun_exposure,
                   self.wind_exposure, u"autocalculate", self.num_of_vertices]

        for vertex in range(len(self.vertices)):
            for coordinate in range(len(self.vertices[vertex])):
                surface.append(unicode(self.vertices[vertex][coordinate]))
        return surface

    def calculate_surface(self):
        if np.allclose(self.z_angle, 0.):
            self.surface_type = u"wall"
            self.is_wall = True
        elif np.allclose(self.z_angle, 90.):
            self.surface_type = u"floor"
            self.is_floor = True
        elif np.allclose(self.z_angle, -90.):
            self.surface_type = u"ceiling"
            self.is_ceiling = True
        elif self.z_angle < 0:
            #self.surface_angle = u""
            self.surface_type = u"ceiling"
            self.is_ceiling = True
            self.is_angled_surface = True
        elif self.z_angle > 0:
            #self.surface_angle = u""
            self.surface_type = u"floor"
            self.is_floor = True
            self.is_angled_surface = True
        else:
            #self.surface_angle = unicode(self.angle)
            self.surface_type = u"wall"
            self.is_wall = True
            self.is_angled_surface = True

    def is_complete_surface(self):
        if self._is_complete:
            return True
            #if self.surface_name is None:
        #    return False
        if self.surface_type is None:
            return False
        if self.construction_name is None:
            return False
            #if self.zone_name is None:
        #    return False
        if self.outside_boundary_condition is None:
            return False
        if self.obc_object is None:
            return False
        if self.sun_exposure is None:
            return False
        if self.wind_exposure is None:
            return False
        self._is_complete = True
        return True

    def find_angle(self, vertices):
        angle = find_angle_name(vertices[0], vertices[2], vertices[1])
        self.x_angle = angle['x_angle']
        self.y_angle = angle['y_angle']
        self.z_angle = angle['z_angle']
        self.surface_angle = u"_".join(filter(None, [unicode(int(self.x_angle)), unicode(int(self.y_angle)),
                                                     unicode(int(self.z_angle))]))
        self.angle = angle['angle']
        #self.z_dir = angle['z_dir']
        self.cross_vector = angle['cross_vector']


class HVAC(object):
    def __init__(self, zone_info, idf_generation_inputs=None):
        self.idf_generation_inputs = idf_generation_inputs
        self.zone_info = zone_info


def cartesian_to_spherical(x, y, z):
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    theta = np.arccos(z / r) * 180. / np.pi
    phi = np.arctan2(y, x) * 180. / np.pi
    return {'r': r, 'theta': theta, "phi": phi}


def spherical_to_cartesian(r, theta, phi):
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return {'x': x, 'y': y, 'z': z}


def find_angle_name(node1, node2, joint_node):
    #node1 = np.array(node1)
    #node2 = np.array(node2)
    #joint_node = np.array(joint_node)
    vector1 = node1 - joint_node
    vector2 = node2 - joint_node

    cross1 = np.cross(vector1, vector2)

    #if cross1[2] > 0:
    #    z_dir = 90
    #elif cross1[2] < 0:
    #    z_dir = -90
    #else:
    #    z_dir = 0

    magnitude = np.sqrt(cross1[0] ** 2 + cross1[1] ** 2 + cross1[2] ** 2)

    x_angle = 90. - np.arccos(cross1[0] / magnitude) * 180. / np.pi
    y_angle = 90. - np.arccos(cross1[1] / magnitude) * 180. / np.pi
    z_angle = 90. - np.arccos(cross1[2] / magnitude) * 180. / np.pi

    #yz_angle = (np.arctan2(cross1[2], cross1[1]) * 180 / np.pi)
    #xz_angle = (np.arctan2(cross1[2], cross1[0]) * 180 / np.pi)
    xy_angle = 180 - (np.arctan2(cross1[1], cross1[0]) * 180 / np.pi)

    #print "xy_angle: ", xy_angle, " xz_angle: ", xz_angle, " yz_angle: ", yz_angle, " x_angle: ", x_angle, \
    #    " y_angle: ", y_angle, " z_angle: ", z_angle

    return {'x_angle': x_angle, 'y_angle': y_angle, 'z_angle': z_angle, 'angle': xy_angle, 'cross_vector': cross1}


#area of polygon poly
def poly_area(poly):
    if len(poly) < 3:  # not a plane - no area
        return 0
    total = [0, 0, 0]
    N = len(poly)
    for i in range(N):
        vi1 = poly[i]
        vi2 = poly[(i + 1) % N]
        prod = np.cross(vi1, vi2)
        total[0] += prod[0]
        total[1] += prod[1]
        total[2] += prod[2]
    result = np.dot(total, unit_normal(poly[0], poly[1], poly[2]))
    return abs(result)


#unit normal vector of plane defined by points a, b, and c
def unit_normal(a, b, c):
    x = np.linalg.det([[1, a[1], a[2]],
                       [1, b[1], b[2]],
                       [1, c[1], c[2]]])
    y = np.linalg.det([[a[0], 1, a[2]],
                       [b[0], 1, b[2]],
                       [c[0], 1, c[2]]])
    z = np.linalg.det([[a[0], a[1], 1],
                       [b[0], b[1], 1],
                       [c[0], c[1], 1]])
    magnitude = (x ** 2 + y ** 2 + z ** 2) ** .5
    return x / magnitude, y / magnitude, z / magnitude


def calculate_polygon_area(x, y, signed=False):
    """Calculate the signed area of non-self-intersecting polygon

    Input
        polygon: Numeric array of points (longitude, latitude). It is assumed
                 to be closed, i.e. first and last points are identical
        signed: Optional flag deciding whether returned area retains its sign:
                If points are ordered counter clockwise, the signed area
                will be positive.
                If points are ordered clockwise, it will be negative
                Default is False which means that the area is always positive.
    Output
        area: Area of polygon (subject to the value of argument signed)
    """

    # Make sure it is numeric
    #P = np.array(polygon)

    # Check input
    #msg = ('Polygon is assumed to consist of coordinate pairs. '
    #       'I got second dimension %i instead of 2' % P.shape[1])
    #assert P.shape[1] == 2, msg

    #msg = ('Polygon is assumed to be closed. '
    #       'However first and last coordinates are different: '
    #       '(%f, %f) and (%f, %f)' % (P[0, 0], P[0, 1], P[-1, 0], P[-1, 1]))
    #assert np.allclose(P[0, :], P[-1, :]), msg

    # Extract x/y and z coordinates
    #x = P[:, 0]
    #y = P[:, 1]

    a = x[:-1] * y[1:]
    b = y[:-1] * x[1:]

    # Area calculation
    A = np.sum(a - b) / 2.

    # Return signed or unsigned area
    if signed:
        return A
    else:
        return abs(A)


def scale_polygon(polygon, scale):
    P = np.array(polygon)
    P = np.vstack((P, np.array(polygon[0])))
    sqrt_scale = np.sqrt(scale)
    x = P[:, 0]
    y = P[:, 1]
    Axy = calculate_polygon_area(x, y, signed=True)
    Axz = 0
    Ayz = 0
    if P.shape[1] == 3:
        z = P[:, 2]
        Axz = calculate_polygon_area(x, z, signed=True)
        Ayz = calculate_polygon_area(y, z, signed=True)

    if Axy == 0 and Ayz == 0 and Axz != 0:
        fenestration_vertices = np.array([sqrt_scale, 1, sqrt_scale]) * np.array(polygon)
    elif Axy == 0 and Ayz != 0 and Axz == 0:
        fenestration_vertices = np.array([1, sqrt_scale, sqrt_scale]) * np.array(polygon)
    elif Axy != 0 and Ayz == 0 and Axz == 0:
        fenestration_vertices = np.array([sqrt_scale, sqrt_scale, 1]) * np.array(polygon)
    else:
        third_root_scale = np.power(scale, 1. / 3.)
        fenestration_vertices = np.array([third_root_scale, third_root_scale, third_root_scale]) * np.array(polygon)

    surface_centroid = calculate_polygon_centroid(polygon)
    fenestration_centroid = calculate_polygon_centroid(fenestration_vertices)
    translation = surface_centroid - fenestration_centroid
    return fenestration_vertices + translation


def calculate_polygon_centroid_test(p_1, p_2, area):
    # Exercise: Compute C as shown in http://paulbourke.net/geometry/polyarea
    a = p_1[:-1] * p_2[1:]
    b = p_2[:-1] * p_1[1:]

    c_1 = p_1[:-1] + p_1[1:]
    c_2 = p_2[:-1] + p_2[1:]

    C_1 = np.sum(c_1 * (a - b)) / (6. * area)
    C_2 = np.sum(c_2 * (a - b)) / (6. * area)

    return np.array([C_1, C_2])


def calculate_polygon_centroid(polygon):
    """Calculate the centroid of non-self-intersecting polygon

    Input
        polygon: Numeric array of points (longitude, latitude). It is assumed
                 to be closed, i.e. first and last points are identical
    Output
        Numeric (1 x 2) array of points representing the centroid
    """
    # Make sure it is numeric
    P = np.array(polygon)
    P = np.vstack((P, np.array(polygon[0])))

    # Extract x and y coordinates
    x = P[:, 0]
    y = P[:, 1]

    Cx = 0.
    Cy = 0.
    Cz = 0.

    # Get area - needed to compute centroid
    Axy = calculate_polygon_area(x, y, signed=True)

    if Axy != 0:
        # Exercise: Compute C as shown in http://paulbourke.net/geometry/polyarea
        a = x[:-1] * y[1:]
        b = y[:-1] * x[1:]

        cx = x[:-1] + x[1:]
        cy = y[:-1] + y[1:]

        Cx = np.sum(cx * (a - b)) / (6. * Axy)
        Cy = np.sum(cy * (a - b)) / (6. * Axy)

    if P.shape[1] == 3:
        # Extract z coordinates
        z = P[:, 2]

        # Get area - needed to compute centroid
        Axz = calculate_polygon_area(x, z, signed=True)
        if Axz != 0:
            # Exercise: Compute C as shown in http://paulbourke.net/geometry/polyarea
            a = x[:-1] * z[1:]
            b = z[:-1] * x[1:]

            cx = x[:-1] + x[1:]
            cz = z[:-1] + z[1:]

            test_Cx = np.sum(cx * (a - b)) / (6. * Axz)

            if Cx != test_Cx and abs(Axz) > abs(Axy):
                Cx = test_Cx

            Cz = np.sum(cz * (a - b)) / (6. * Axz)
            #Cx = np.sum(cx * (a - b)) / (6. * Axz)

        Ayz = calculate_polygon_area(y, z, signed=True)
        if Ayz != 0:
            # Exercise: Compute C as shown in http://paulbourke.net/geometry/polyarea
            a = y[:-1] * z[1:]
            b = z[:-1] * y[1:]

            cy = y[:-1] + y[1:]
            cz = z[:-1] + z[1:]

            test_Cy = np.sum(cy * (a - b)) / (6. * Ayz)
            test_Cz = np.sum(cz * (a - b)) / (6. * Ayz)

            if Cy != test_Cy and abs(Ayz) > abs(Axy):
                Cy = test_Cy

            if Cz != test_Cz and abs(Ayz) > abs(Axz):
                Cz = test_Cz
                #Cz = np.sum(cz * (a - b)) / (6. * Ayz)
                #Cy = np.sum(cy * (a - b)) / (6. * Ayz)

    if P.shape[1] == 3:
        C = np.array([Cx, Cy, Cz])
    else:
        # Create Nx2 array and return
        C = np.array([Cx, Cy])
    return C