__author__ = 'Mark Adams <adamsmb@ornl.gov>'

import numpy as np
import math
#from numpy import linalg as LA


surface_generation_order = ['Floor', 'Wall', 'Wall', 'Wall', 'Wall', 'Ceiling']


def generate_geometry(inputs):
    #generate_rectangle_walls(inputs)
    for floornum in inputs['numoffloors']:
        for zonenum in inputs['zonelayout']:
            for surface_order in len(surface_generation_order):
                generate_building_surface(floornum, zonenum, surface_order)


def generate_rectangle_building(floornum, zonenum, surface_order):
    building = []
    vertices = []

    if surface_order == 'Floor':
        vertices.append

    return building


def generate_building_surface(floornum, zonenum, surface_order, length1=50, width1=50, coreoffset=5):
    surfaces = []

    vertices = rectangle_zone_vertices(1, 10)

    for zone in range(len(vertices)):
        if zone == 4:
            zone_location = u"core"
        else:
            zone_location = u"perimeter"
        surfaces.extend(generate_building(vertices=vertices, zone=zone, zone_location=zone_location, total_floors=3,
                                          floor_number=1, is_plenum=False))

    for surface in surfaces:
        adjancent_surface = surface[11:].reverse()
        for adjancency in surfaces:
            surface_check = adjancency[11:]
            if surface_check == adjancent_surface:
                outside_boundary = adjancency[1]
                has_internal_boundary = True


    #check outside boundary condition and object here. Also will edit sun and wind properties here
    #probably change construction name here too
    #maybe check if 1 or more walls face exterior then perimeter else 0 walls face exterior then core for
    #zone_location
    #check for adjacency here

    generate_building_surface_detailed(vertices[0][1], 1, 1, "Ceiling", False)

    southwall = vertices[0][1]

    return surfaces


def generate_building(vertices, zone, zone_location, total_floors, floor_number, is_plenum=False):
    building = []

    if floor_number == 1:
        floor_level = u"bot"
    elif floor_number == total_floors:
        floor_level = u"top"
    else:
        floor_level = u"mid"

    if is_plenum:
        zone_type = u"plenum"
    else:
        zone_type = u"zone"

    #zone_name =
    for surface in range(len(vertices[zone])):

        angle = find_angle_name(vertices[zone][surface][0], vertices[zone][surface][2], vertices[zone][surface][1])

        if angle[1] < 0:
            surface_facing_location = u""
            surface_type = u"ceiling"
        elif angle[1] > 0:
            surface_facing_location = u""
            surface_type = u"floor"
        else:
            surface_facing_location = unicode(angle[0])
            surface_type = u"wall"

        surfaces = []

        surfaces.append(u"BuildingSurface:Detailed")
        surfaces.append(
            u"_".join(filter(None, ['''zone_location''' u"location", floor_level, zone_type, unicode(zone + 1),
                                    surface_type, surface_facing_location])))
        surfaces.append(surface_type)
        surfaces.append(u"construction name")
        surfaces.append(u"_".join(filter(None, [zone_location, floor_level, zone_type, unicode(zone + 1)])))
        surfaces.append(u"outside boundary condition / Outdoors")
        surfaces.append(u"outside boundary condition object / Blank")
        surfaces.append(u"NoSun / SunExposed")
        surfaces.append(u"NoWind / WindExposed")
        surfaces.append(u"autocalculate")
        surfaces.append(unicode(len(vertices[zone][surface])))

        for vertex in range(len(vertices[zone][surface])):
            for coordinate in range(len(vertices[zone][surface][vertex])):
                surfaces.append(unicode(vertices[zone][surface][vertex][coordinate]))

        building.append(surfaces)

    #check outside boundary condition and object here. Also will edit sun and wind properties here
    #probably change construction name here too
    #maybe check if 1 or more walls face exterior then perimeter else 0 walls face exterior then core for
    #zone_location

    #maybe run all vertices through a class that generates angle, outside boundary, floor_level, etc???
    return building


def find_angle_name(node1, node2, joint_node):
    node1 = np.array(node1)
    node2 = np.array(node2)
    joint_node = np.array(joint_node)
    vector1 = node1 - joint_node
    vector2 = node2 - joint_node

    cross1 = np.cross(vector1, vector2)

    if cross1[2] > 0:
        zdir = 90
    elif cross1[2] < 0:
        zdir = -90
    else:
        zdir = 0

    angle = 180 - (np.arctan2(cross1[1], cross1[0]) * 180 / np.pi)

    #Unused...
    #cross2 = np.cross(vector2, vector1)
    #normvector1 = np.linalg.norm(vector1)
    #normvector2 = np.linalg.norm(vector2)
    #normvector1 = np.sqrt(vector1.dot(vector1))
    #normvector2 = np.sqrt(vector2.dot(vector2))
    #normcross1 = np.cross(vector1 / normvector1, vector2 / normvector2)
    #normcross2 = np.cross(vector2 / normvector2, vector1 / normvector1)
    #angles1 = vector_angle(cross1)
    #angles2 = vector_angle(cross2)
    return [angle, zdir]


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
    return abs(result / 2)


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


def norm(vector):
    """
    Returns the norm (length) of the vector.
    :param vector:
    :return: norm (length) of the vector
    """
    return np.sqrt(np.dot(vector, vector))


def unit_vector(vector):
    """
    Returns the unit vector of the vector.
    :param vector:
    :return: unit vector of the vector
    """
    return vector / norm(vector)


def angle_between(v1, v2, indegrees=False):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))

    if math.isnan(angle):
        if v1_u == v2_u:
            return 0.0
        else:
            return np.pi
    if indegrees:
        return np.rad2deg(angle)
    else:
        return angle


def vector_angle(vector):
    x = angle_between(vector, np.array([1, 0, 0]), True)
    y = angle_between(vector, np.array([0, 1, 0]), True)
    z = angle_between(vector, np.array([0, 0, 1]), True)

    return [x, y, z]


def generate_building_surface_detailed(vertices, zonenum, floornum, surface_type, isplenum=False):
    building = []

    building.append("BuildingSurface:Detailed")
    building.append(
        "core_" if zonenum == 5 else "perimeter_" + "bot_" if floornum == 1 else "top_" + "plenum_" if isplenum else "zone_" + zonenum + "_" + surface_type)
    building.append(surface_type)
    #building.append(surfaceconstruction)
    building.append(
        "core_" if zonenum == 5 else "perimeter_" + "bot_" if floornum == 1 else "mid_" + "plenum_" if isplenum else "zone_" + zonenum)
    #building.append(outsideboundarycondition)
    #building.append("core_" if zonenum == 5 else "perimeter_" + "mid_" if floornum == 1 else
    #                "top_" + "plenum_" if isplenum else "zone_" + zonenum + "_" + outside_surface_type)
    building.append("NoSun")
    building.append("NoWind")
    building.append("4")
    for vertex in vertices:
        for coordinate in vertex:
            building.append(coordinate)

    return building


"""
BuildingSurface:Detailed,
    Core_*%ZoneFloorLevel%*_*%ZoneType%*_5_Ceiling,   !- Name
    Ceiling,                 !- Surface Type
    *%*%ZoneType%*CeilingConstruction%*,             !- Construction Name
    Core_*%ZoneFloorLevel%*_*%ZoneType%*_5,                !- Zone Name
    Surface,                 !- Outside Boundary Condition
    Core_*%ZoneCeilingBoundaryObjectFloorLevel%*_*%ZoneCeilingBoundaryObject%*_5_Floor,      !- Outside Boundary Condition Object
    NoSun,                   !- Sun Exposure
    NoWind,                  !- Wind Exposure
    AutoCalculate,           !- View Factor to Ground
    4,                       !- Number of Vertices
    *%CoreBuildingLength%*,  !- Vertex 1 X-coordinate {m}
    *%CoreOffset%*,          !- Vertex 1 Y-coordinate {m}
    *%*%ZoneFloorLevel%*_*%ZoneTypeHeight%*_UpperHeight%*,  !- Vertex 1 Z-coordinate {m}
    *%CoreBuildingLength%*,  !- Vertex 2 X-coordinate {m}
    *%CoreBuildingWidth%*,   !- Vertex 2 Y-coordinate {m}
    *%*%ZoneFloorLevel%*_*%ZoneTypeHeight%*_UpperHeight%*,  !- Vertex 2 Z-coordinate {m}
    *%CoreOffset%*,          !- Vertex 3 X-coordinate {m}
    *%CoreBuildingWidth%*,   !- Vertex 3 Y-coordinate {m}
    *%*%ZoneFloorLevel%*_*%ZoneTypeHeight%*_UpperHeight%*,  !- Vertex 3 Z-coordinate {m}
    *%CoreOffset%*,          !- Vertex 4 X-coordinate {m}
    *%CoreOffset%*,          !- Vertex 4 Y-coordinate {m}
    *%*%ZoneFloorLevel%*_*%ZoneTypeHeight%*_UpperHeight%*;  !- Vertex 4 Z-coordinate {m}
"""