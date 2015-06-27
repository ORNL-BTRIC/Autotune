__author__ = 'm5z'

window_constructions = {
    u'reference': {
        'construction': [u"Construction", u"Reference", u"NonRes Fixed Assembly Window"]},
    u'double_bronze': {
        'construction': [u"Construction", u"Double_Bronze", u"BRONZE 6MM", u"AIR 6MM", u"CLEAR 6MM"],
        'glass_u_factor': 3.058, 'glass_shgc': 0.503, 'glass_visible_transmittance': 0.473},
    u'double_clear_lowe': {
        'construction': [u"Construction", u"Double_Clear_LowE", u"LoE CLEAR 6MM", u"AIR 6MM", u"CLEAR 6MM"],
        'glass_u_factor': 2.371, 'glass_shgc': 0.569, 'glass_visible_transmittance': 0.745},
    u'double_clear': {
        'construction': [u"Construction", u"Double_Clear", u"CLEAR 6MM", u"AIR 6MM", u"CLEAR 6MM"],
        'glass_u_factor': 3.058, 'glass_shgc': 0.700, 'glass_visible_transmittance': 0.781},
    u'single_bronze': {
        'construction': [u"Construction", u"Single_Bronze", u"BRONZE 6MM"],
        'glass_u_factor': 5.778, 'glass_shgc': 0.620, 'glass_visible_transmittance': 0.534},
    u'single_clear_lowe': {
        'construction': [u"Construction", u"Single_Clear_LowE", u"PYR B CLEAR 6MM"],
        'glass_u_factor': 3.779, 'glass_shgc': 0.720, 'glass_visible_transmittance': 0.811},
    u'single_clear': {
        'construction': [u"Construction", u"Single_Clear", u"CLEAR 6MM"],
        'glass_u_factor': 5.778, 'glass_shgc': 0.819, 'glass_visible_transmittance': 0.881},
    u'triple_clear': {
        'construction': [u"Construction", u"Triple_Clear", u"CLEAR 3MM", u"AIR 6MM", u"CLEAR 3MM", u"AIR 6MM",
                         u"CLEAR 3MM"],
        'glass_u_factor': 2.143, 'glass_shgc': 0.682, 'glass_visible_transmittance': 0.738},
    u"triple_clear_lowe": {
        'construction': [u"Construction", u"Triple_Clear_LowE", u"LoE CLEAR 3MM", u"AIR 6MM", u"CLEAR 3MM", u"AIR 6MM",
                         u"LoE CLEAR 3MM Rev"],
        'glass_u_factor': 1.525, 'glass_shgc': 0.472, 'glass_visible_transmittance': 0.661}, }

window_materials = {
    u"CLEAR 6MM": [u"WindowMaterial:Glazing", u"CLEAR 6MM", u"SpectralAverage", u"", u"0.006", u"0.775", u"0.071",
                   u"0.071", u"0.881", u"0.08", u"0.08", u"0", u"0.84", u"0.84", u"0.9"],
    u"BRONZE 6MM": [u"WindowMaterial:Glazing", u"BRONZE 6MM", u"SpectralAverage", u"", u"0.006", u"0.482", u"0.054",
                    u"0.054", u"0.534", u"0.057", u"0.057", u"0", u"0.84", u"0.84", u"0.9"],
    u"AIR 6MM": [u"WindowMaterial:Gas", u"AIR 6MM", u"Air", u"0.0063"],
    u"LoE CLEAR 6MM": [u"WindowMaterial:Glazing", u"LoE CLEAR 6MM", u"SpectralAverage", u"", u"0.006", u"0.6", u"0.17",
                       u"0.22", u"0.84", u"0.055", u"0.078", u"0", u"0.84", u"0.1", u"0.9"],
    u"PYR B CLEAR 6MM": [u"WindowMaterial:Glazing", u"PYR B CLEAR 6MM", u"SpectralAverage", u"", u"0.006", u"0.68",
                         u"0.09", u"0.1", u"0.81", u"0.11", u"0.12", u"0", u"0.84", u"0.2", u"0.9"],
    u"LoE CLEAR 3MM Rev": [u"WindowMaterial:Glazing", u"LoE CLEAR 3MM Rev", u"SpectralAverage", u"", u"0.003", u"0.63",
                           u"0.22", u"0.19", u"0.85", u"0.079", u"0.056", u"0", u"0.1", u"0.84", u"0.9"],
    u"LoE CLEAR 3MM": [u"WindowMaterial:Glazing", u"LoE CLEAR 3MM", u"SpectralAverage", u"", u"0.003", u"0.63", u"0.19",
                       u"0.22", u"0.85", u"0.056", u"0.079", u"0", u"0.84", u"0.1", u"0.9"],
    u"CLEAR 3MM": [u"WindowMaterial:Glazing", u"CLEAR 3MM", u"SpectralAverage", u"", u"0.003", u"0.837", u"0.075",
                   u"0.075", u"0.898", u"0.081", u"0.081", u"0", u"0.84", u"0.84", u"0.9"]}


def all_constructions(inputs):
    constructions = []
    constructions.extend(_common())

    unique_windows = {inputs['south_win_type'], inputs['east_win_type'],
                      inputs['north_win_type'], inputs['west_win_type']}

    if u'reference' in unique_windows:
        window_materials[u'NonRes Fixed Assembly Window'] = \
            [u"WindowMaterial:SimpleGlazingSystem", u"NonRes Fixed Assembly Window",
             inputs['glass_u_factor'], inputs['glass_shgc'],
             u"" if inputs['glass_visible_transmittance'] is None else inputs['glass_visible_transmittance']]

    all_window_materials = []
    for window_type in unique_windows:
        constructions.append(window_constructions[window_type]['construction'])
        all_window_materials.extend(window_constructions[window_type]['construction'][2:])
    unique_window_materials = set(all_window_materials)
    [constructions.append(window_materials[window_material]) for window_material in unique_window_materials]

    #unique_walls = {inputs['wall_type']}
    #[constructions.extend(_walls(wall_type)) for wall_type in unique_walls]

    #unique_roofs = {inputs['roof_type']}
    #[constructions.extend(_roofs(roof_type)) for roof_type in unique_roofs]

    constructions.extend(_walls(inputs['wall_type'], inputs['wall_insulation']))
    constructions.extend(_roofs(inputs['roof_type'], inputs['roof_insulation']))

    return constructions


def _common():
    common = [[u"Material", u"Std Wood 6inch", u"MediumSmooth", u"0.15", u"0.12", u"540.0000", u"1210", u"0.9000000",
               u"0.7000000", u"0.7000000"],
              [u"Material", u"Wood Siding", u"MediumSmooth", u"0.0100", u"0.1100", u"544.6200", u"1210.0000", u"0.9000",
               u"0.7800", u"0.7800"], [u"Material:NoMass", u"MAT-SHEATH", u"Rough", u"0.36256", u"0.9", u"0.7", u"0.7"],
              [u"Material", u"1/2IN Gypsum", u"Smooth", u"0.0127", u"0.1600", u"784.9000", u"830.0000", u"0.9000",
               u"0.9200", u"0.9200"],
              [u"Material", u"1IN Stucco", u"Smooth", u"0.0253", u"0.6918", u"1858.0000", u"837.0000", u"0.9000",
               u"0.9200", u"0.9200"],
              #[u"Material", u"8IN Concrete HW", u"MediumRough", u"0.2033", u"1.7296", u"2243", u"837", u"0.9", u"0.65",
              # u"0.65"],
              [u"Material", u"8IN Concrete HW", u"Rough", u"0.2032", u"1.3110", u"2240.0000", u"836.8000", u"0.9000",
               u"0.7000", u"0.7000"],
              [u"Material", u"Metal Siding", u"Smooth", u"0.0015", u"44.9600", u"7688.8600", u"410.0000", u"0.9000",
               u"0.2000", u"0.2000"],
              [u"Material", u"HW CONCRETE", u"Rough", u"0.1016", u"1.3110", u"2240.0000", u"836.8000", u"0.9000",
               u"0.7000", u"0.7000"],
              [u"Material", u"Roof Membrane", u"VeryRough", u"0.0095", u"0.1600", u"1121.2900", u"1460.0000", u"0.9000",
               u"0.7000", u"0.7000"],
              [u"Material", u"Metal Decking", u"MediumSmooth", u"0.0015", u"45.0060", u"7680.0000", u"418.4000",
               u"0.9000", u"0.7000", u"0.3000"],
              [u"Material", u"Metal Roofing", u"MediumSmooth", u"0.0015", u"45.0060", u"7680.0000", u"418.4000",
               u"0.9000", u"0.7000", u"0.3000"],
              [u"Material", u"MAT-CC05 4 HW CONCRETE", u"Rough", u"0.1016", u"1.3110", u"2240.0000", u"836.8000",
               u"0.9000", u"0.7000", u"0.7000"],
              [u"Material", u"Std AC02", u"MediumSmooth", u"1.2700000E-02", u"5.7000000E-02", u"288.0000", u"1339.000",
               u"0.9000000", u"0.7000000", u"0.2000000"],
              [u"Material:NoMass", u"CP02 CARPET PAD", u"VeryRough", u"0.2165", u"0.9000", u"0.7000", u"0.8000"],
              [u"Construction", u"ext-slab", u"HW CONCRETE", u"CP02 CARPET PAD"],
              [u"Construction", u"int-walls", u"1/2IN Gypsum", u"1/2IN Gypsum"],
              [u"Construction", u"DropCeiling", u"Std AC02"],
              [u"Construction", u"InteriorFurnishings", u"Std Wood 6inch"],
              [u"Construction", u"INT-FLOOR-TOPSIDE", u"MAT-CC05 4 HW CONCRETE", u"CP02 CARPET PAD"],
              [u"Construction", u"INT-FLOOR-UNDERSIDE", u"CP02 CARPET PAD", u"MAT-CC05 4 HW CONCRETE"],
              [u"Material:NoMass", u"MAT-AIR-WALL", u"Rough", u"0.2079491", u"0.9", u"0.7"],
              [u"Construction", u"AIR-WALL", u"MAT-AIR-WALL"]]
    return common


def _roofs(roof_type, roof_insulation):
    roof = []
    if roof_type == u"attic_roof_non_res":
        roof.append(
            [u"Material", u"AtticFloor NonRes Insulation", u"MediumRough", roof_insulation, # u"0.236804989096202",
             u"0.049", u"265.0000", u"836.8000", u"0.9000", u"0.7000", u"0.7000"])
        roof.append([u"Construction", u"attic_floor_non_res", u"1/2IN Gypsum", u"AtticFloor NonRes Insulation",
                     u"1/2IN Gypsum"])
        roof.append([u"Construction", u"attic_roof_non_res", u"Roof Membrane", u"Metal Decking"])
        roof.append(
            [u"ComponentCost:LineItem", u"Attic_Floor_Non_Res", u"", u"Construction", u"Attic_Floor_Non_Res",
             u"", u"", u"35.009", u"", u"", u"", u"", u"", u""])
    elif roof_type == u"iead_non_res":
        roof.append(
            [u"Material", u"IEAD NonRes Roof Insulation", u"MediumRough", roof_insulation, # u"0.127338688569477",
             u"0.049", u"265.0000", u"836.8000", u"0.9000", u"0.7000", u"0.7000"])
        roof.append(
            [u"Construction", u"IEAD_Non_Res", u"Roof Membrane", u"IEAD NonRes Roof Insulation", u"Metal Decking"])
        roof.append(
            [u"ComponentCost:LineItem", u"IEAD_Non_Res", u"", u"Construction", u"IEAD_Non_Res", u"", u"",
             u"52.870", u"", u"", u"", u"", u"", u""])
    return roof


def _walls(wall_type, wall_insulation):
    wall = []
    if wall_type == u"concrete_non_res":
        wall.append(
            [u"Material", u"Mass NonRes Wall Insulation", u"MediumRough", wall_insulation, # u"0.0495494599433393",
             u"0.049", u"265.0000", u"836.8000", u"0.9000", u"0.7000", u"0.7000"])
        wall.append([u"Construction", u"Concrete_Non_Res", u"1IN Stucco", u"8IN Concrete HW",
                     u"Mass NonRes Wall Insulation", u"1/2IN Gypsum"])
        wall.append(
            [u"ComponentCost:LineItem", u"Concrete_Non_Res", u"", u"Construction", u"Concrete_Non_Res", u"",
             u"", u"67.955", u"", u"", u"", u"", u"", u""])
    elif wall_type == u"metal_building_non_res":
        wall.append(
            [u"Material", u"Metal Building Wall Insulation", u"MediumRough", wall_insulation, # u"0.128688",
             u"0.045", u"265", u"836.8", u"0.9", u"0.7", u"0.7"])
        wall.append(
            [u"Construction", u"Metal_Building_Non_Res", u"Metal Siding", u"Metal Building Wall Insulation",
             u"1/2IN Gypsum"])
        wall.append([u"ComponentCost:LineItem", u"Metal_Building_Non_Res", u"", u"Construction",
                     u"Metal_Building_Non_Res", u"", u"", u"107.702", u"", u"", u"", u"", u"", u""])
    elif wall_type == u"steel_frame_non_res":
        wall.append(
            [u"Material", u"Steel Frame NonRes Wall Insulation", u"MediumRough", wall_insulation,
             # u"0.0870564552646045",
             u"0.049", u"265.0000", u"836.8000", u"0.9000", u"0.7000", u"0.7000"])
        wall.append(
            [u"Construction", u"Steel_Frame_Non_Res", u"Wood Siding", u"Steel Frame NonRes Wall Insulation",
             u"1/2IN Gypsum"])
        wall.append(
            [u"ComponentCost:LineItem", u"Steel_Frame_Non_Res", u"", u"Construction", u"Steel_Frame_Non_Res",
             u"", u"", u"94.657", u"", u"", u"", u"", u"", u""])
    elif wall_type == u"wood_framed":
        wall.append(
            [u"Material", u"Wood Framed Wall Insulation", u"MediumRough", wall_insulation, # u"0.140713",
             u"0.045", u"265", u"836.8", u"0.9", u"0.7", u"0.7"])
        wall.append([u"Construction", u"Wood_Framed", u"Wood Siding", u"Wall Insulation [13]", u"1/2IN Gypsum"])
        wall.append(
            [u"ComponentCost:LineItem", u"Wood_Framed", u"", u"Construction", u"Wood_Framed", u"", u"",
             u"80.638", u"", u"", u"", u"", u"", u""])
    return wall