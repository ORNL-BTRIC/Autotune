__author__ = 'm5z'


def create_rectangle_zone(total_floor_num, floor_height=3.9624, five_zone_plenum=False, plenums=False, length1=49.9110,
                          width1=33.2738, core_offset=4.5732, plenum_height=1.2192, use_multiplier=True,
                          roof_type=u"flat"):
    building = []

    is_flat_roof = False
    is_hip_roof = False

    if roof_type == u"flat":
        is_flat_roof = True
    elif roof_type == u"hip":
        is_hip_roof = True

    if use_multiplier and total_floor_num > 3:
        floor_nums = [1, int(round((total_floor_num - 2.) * 0.5) + 1.), total_floor_num]
    else:
        floor_nums = range(1, total_floor_num + 1)

    for floor_num in floor_nums:
        if plenums:
            # add zone vertices
            floor = floor_height * (floor_num - 1)
            ceiling = floor_height * floor_num - plenum_height
            building.extend(_rectangle_zone_vertices(floor, ceiling, length1, width1, core_offset))
            # add plenum vertices
            floor = floor_height * floor_num - plenum_height
            ceiling = floor_height * floor_num
            if five_zone_plenum:
                building.extend(_rectangle_zone_vertices(floor, ceiling, length1, width1, core_offset))
            else:
                building.extend(_rectangle_plenum_vertices(floor, ceiling, length1, width1, core_offset))
        else:
            floor = floor_height * (floor_num - 1)
            ceiling = floor_height * floor_num
            building.extend(_rectangle_zone_vertices(floor, ceiling, length1, width1, core_offset))

    if not is_flat_roof:
        floor = total_floor_num * floor_height
        ceiling = floor + 3.28
        building.extend(_rectangle_gable_roof_vertices(floor, ceiling, length1, width1, core_offset,
                                                       is_hip_roof=is_hip_roof))
    return building


def _rectangle_zone_vertices(floor, ceiling, length1, width1, core_offset):
    """

                     ________________________________
                    |\                              /|
                    | \                            / |
                    |  \__________________________/  |
                    |   |                        |   |
                    |   |                        |   |
                    |   |                        |   |
                    |   |                        |   |
                    |   |________________________|   |
                    |  /                          \  |
                    | /                            \ |
                    |/______________________________\|

                              4 - int wall
                        _____________________
                       /                     \
      5 - int wall    /       1 - floor       \  3 - int wall
                     /        6 - ceiling      \
                    /___________________________\
                              2 - ext wall

    [zone][surface][vertex order][vertices]

    :param floor:
    :param ceiling:
    :param length1:
    :param width1:
    :param core_offset:
    :return: nested list of vertices for zone one of rectangle
    """

    core_length = length1 - core_offset
    core_width = width1 - core_offset

    return [
        [[[0, 0, floor], [core_offset, core_offset, floor], [core_length, core_offset, floor], [length1, 0, floor]],
         [[0, 0, ceiling], [0, 0, floor], [length1, 0, floor], [length1, 0, ceiling]],
         [[length1, 0, ceiling], [length1, 0, floor], [core_length, core_offset, floor],
          [core_length, core_offset, ceiling]],
         [[core_length, core_offset, ceiling], [core_length, core_offset, floor], [core_offset, core_offset, floor],
          [core_offset, core_offset, ceiling]],
         [[core_offset, core_offset, ceiling], [core_offset, core_offset, floor], [0, 0, floor], [0, 0, ceiling]],
         [[length1, 0, ceiling], [core_length, core_offset, ceiling], [core_offset, core_offset, ceiling],
          [0, 0, ceiling]]],

        [[[length1, 0, floor], [core_length, core_offset, floor], [core_length, core_width, floor],
          [length1, width1, floor]],
         [[length1, 0, ceiling], [length1, 0, floor], [length1, width1, floor], [length1, width1, ceiling]],
         [[length1, width1, ceiling], [length1, width1, floor], [core_length, core_width, floor],
          [core_length, core_width, ceiling]],
         [[core_length, core_width, ceiling], [core_length, core_width, floor], [core_length, core_offset, floor],
          [core_length, core_offset, ceiling]],
         [[core_length, core_offset, ceiling], [core_length, core_offset, floor], [length1, 0, floor],
          [length1, 0, ceiling]],
         [[length1, width1, ceiling], [core_length, core_width, ceiling], [core_length, core_offset, ceiling],
          [length1, 0, ceiling]]],

        [[[length1, width1, floor], [core_length, core_width, floor], [core_offset, core_width, floor],
          [0, width1, floor]],
         [[core_offset, core_width, ceiling], [core_offset, core_width, floor], [core_length, core_width, floor],
          [core_length, core_width, ceiling]],
         [[core_length, core_width, ceiling], [core_length, core_width, floor], [length1, width1, floor],
          [length1, width1, ceiling]],
         [[length1, width1, ceiling], [length1, width1, floor], [0, width1, floor], [0, width1, ceiling]],
         [[0, width1, ceiling], [0, width1, floor], [core_offset, core_width, floor],
          [core_offset, core_width, ceiling]],
         [[0, width1, ceiling], [core_offset, core_width, ceiling], [core_length, core_width, ceiling],
          [length1, width1, ceiling]]],

        [[[0, width1, floor], [core_offset, core_width, floor], [core_offset, core_offset, floor], [0, 0, floor]],
         [[0, 0, ceiling], [0, 0, floor], [core_offset, core_offset, floor], [core_offset, core_offset, ceiling]],
         [[core_offset, core_offset, ceiling], [core_offset, core_offset, floor], [core_offset, core_width, floor],
          [core_offset, core_width, ceiling]],
         [[core_offset, core_width, ceiling], [core_offset, core_width, floor], [0, width1, floor],
          [0, width1, ceiling]],
         [[0, width1, ceiling], [0, width1, floor], [0, 0, floor], [0, 0, ceiling]],
         [[0, 0, ceiling], [core_offset, core_offset, ceiling], [core_offset, core_width, ceiling],
          [0, width1, ceiling]]],

        [[[core_offset, core_offset, floor], [core_offset, core_width, floor], [core_length, core_width, floor],
          [core_length, core_offset, floor]],
         [[core_offset, core_offset, ceiling], [core_offset, core_offset, floor], [core_length, core_offset, floor],
          [core_length, core_offset, ceiling]],
         [[core_length, core_offset, ceiling], [core_length, core_offset, floor], [core_length, core_width, floor],
          [core_length, core_width, ceiling]],
         [[core_length, core_width, ceiling], [core_length, core_width, floor], [core_offset, core_width, floor],
          [core_offset, core_width, ceiling]],
         [[core_offset, core_width, ceiling], [core_offset, core_width, floor], [core_offset, core_offset, floor],
          [core_offset, core_offset, ceiling]],
         [[core_length, core_offset, ceiling], [core_length, core_width, ceiling], [core_offset, core_width, ceiling],
          [core_offset, core_offset, ceiling]]]
    ]


def _rectangle_plenum_vertices(floor, ceiling, length1, width1, core_offset):
    """

                     ________________________________
                    |\                              /|
                    | \                            / |
                    |  \__________________________/  |
                    |   |                        |   |
                    |   |                        |   |
                    |   |                        |   |
                    |   |                        |   |
                    |   |________________________|   |
                    |  /                          \  |
                    | /                            \ |
                    |/______________________________\|

                              4 - int wall
                        _____________________
                       /                     \
      5 - int wall    /       1 - floor       \  3 - int wall
                     /        6 - ceiling      \
                    /___________________________\
                              2 - ext wall

    [zone][surface][vertex order][vertices]

    :param floor:
    :param ceiling:
    :param length1:
    :param width1:
    :param core_offset:
    :return: nested list of vertices for zone one of rectangle
    """

    core_length = length1 - core_offset
    core_width = width1 - core_offset

    return [
        [[[0, 0, floor], [core_offset, core_offset, floor], [core_length, core_offset, floor], [length1, 0, floor]],
         [[length1, 0, floor], [core_length, core_offset, floor], [core_length, core_width, floor],
          [length1, width1, floor]],
         [[length1, width1, floor], [core_length, core_width, floor], [core_offset, core_width, floor],
          [0, width1, floor]],
         [[0, width1, floor], [core_offset, core_width, floor], [core_offset, core_offset, floor], [0, 0, floor]],
         [[core_offset, core_offset, floor], [core_offset, core_width, floor], [core_length, core_width, floor],
          [core_length, core_offset, floor]],

         [[0, 0, ceiling], [0, 0, floor], [length1, 0, floor], [length1, 0, ceiling]],
         [[length1, 0, ceiling], [length1, 0, floor], [length1, width1, floor], [length1, width1, ceiling]],
         [[length1, width1, ceiling], [length1, width1, floor], [0, width1, floor], [0, width1, ceiling]],
         [[0, width1, ceiling], [0, width1, floor], [0, 0, floor], [0, 0, ceiling]],

         [[length1, 0, ceiling], [core_length, core_offset, ceiling], [core_offset, core_offset, ceiling],
          [0, 0, ceiling]],
         [[length1, width1, ceiling], [core_length, core_width, ceiling], [core_length, core_offset, ceiling],
          [length1, 0, ceiling]],
         [[0, width1, ceiling], [core_offset, core_width, ceiling], [core_length, core_width, ceiling],
          [length1, width1, ceiling]],
         [[0, 0, ceiling], [core_offset, core_offset, ceiling], [core_offset, core_width, ceiling],
          [0, width1, ceiling]],
         [[core_length, core_offset, ceiling], [core_length, core_width, ceiling], [core_offset, core_width, ceiling],
          [core_offset, core_offset, ceiling]]]
    ]


def _rectangle_gable_roof_vertices(floor, ceiling, length1, width1, core_offset, soffit=0.6, is_hip_roof=False):
    core_length = length1 - core_offset
    core_width = width1 - core_offset
    soffit = -abs(soffit)
    soffit_length = length1 - soffit
    soffit_width = width1 - soffit
    if is_hip_roof:
        gable_origin_side = length1 / 3.0
        gable_length1_side = length1 * 2.0 / 3.0
    else:
        gable_origin_side = 0.0
        gable_length1_side = length1
    gable_width = width1 * 0.5

    return [
        [[[0, 0, floor], [core_offset, core_offset, floor], [core_length, core_offset, floor], [length1, 0, floor]],
         [[length1, 0, floor], [core_length, core_offset, floor], [core_length, core_width, floor],
          [length1, width1, floor]],
         [[length1, width1, floor], [core_length, core_width, floor], [core_offset, core_width, floor],
          [0, width1, floor]],
         [[0, width1, floor], [core_offset, core_width, floor], [core_offset, core_offset, floor], [0, 0, floor]],
         [[core_offset, core_offset, floor], [core_offset, core_width, floor], [core_length, core_width, floor],
          [core_length, core_offset, floor]],

         [[0, 0, floor], [length1, 0, floor], [soffit_length, soffit, floor], [soffit, soffit, floor]],
         [[soffit_length, soffit_width, floor], [soffit_length, soffit, floor], [length1, 0, floor],
          [length1, width1, floor]],
         [[soffit, soffit_width, floor], [soffit_length, soffit_width, floor], [length1, width1, floor],
          [0, width1, floor]],
         [[soffit, soffit_width, floor], [0, width1, floor], [0, 0, floor], [soffit, soffit, floor]],

         [[soffit, soffit, floor], [soffit_length, soffit, floor], [gable_length1_side, gable_width, ceiling],
          [gable_origin_side, gable_width, ceiling]],
         [[soffit_length, soffit, floor], [soffit_length, soffit_width, floor],
          [gable_length1_side, gable_width, ceiling]],
         [[soffit_length, soffit_width, floor], [soffit, soffit_width, floor],
          [gable_origin_side, gable_width, ceiling],
          [gable_length1_side, gable_width, ceiling]],
         [[soffit, soffit_width, floor], [soffit, soffit, floor], [gable_origin_side, gable_width, ceiling]]]
    ]