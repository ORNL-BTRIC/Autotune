__author__ = 'm5z'

_ASHRAE_DEFAULTS = {
    u'1a': {
        'new2004': {
            u'common': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                        'infiltration_per_ext_sur_area': 0.000302, 'int_lighting_intensity': 10.76,
                        'dhw_efficiency': 0.8, 'glass_u_factor': 6.92716, 'glass_shgc': 0.25,
                        'glass_visible_transmittance': None},
            u'medium_office': {'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'cooling_cop': 3.66668442928701, 'wall_insulation': 0.0365394788793098,
                              'roof_insulation': 0.234129751336427, 'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                        'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78, 'glass_u_factor': 6.92716,
                        'glass_shgc': 0.25, 'glass_visible_transmittance': None},
            u'medium_office': {'wall_insulation': 0.0, 'roof_insulation': 0.104301419176096,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'wall_insulation': 0.0, 'roof_insulation': 0.0969310355164076,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'2a': {
        'new2004': {
            u'common': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                        'infiltration_per_ext_sur_area': 0.000302, 'int_lighting_intensity': 10.76,
                        'dhw_efficiency': 0.8, 'glass_u_factor': 6.92716, 'glass_shgc': 0.25,
                        'glass_visible_transmittance': None},
            u'medium_office': {'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'cooling_cop': 3.66668442928701, 'wall_insulation': 0.0365394788793098,
                              'roof_insulation': 0.234129751336427, 'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                        'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78, 'glass_u_factor': 6.92716,
                        'glass_shgc': 0.25, 'glass_visible_transmittance': None},
            u'medium_office': {'wall_insulation': 0.0418527450379989, 'roof_insulation': 0.118437044442401,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'wall_insulation': 0.0047702530604555, 'roof_insulation': 0.111066660782713,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'2b': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 6.92716,
                        'glass_shgc': 0.25, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0365394788793098, 'roof_insulation': 0.234129751336427,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133,
                        'dhw_efficiency': 0.78, 'glass_u_factor': 6.92716, 'glass_shgc': 0.25,
                        'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.0202782469753007, 'roof_insulation': 0.175286841709063,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.000436781426628043, 'roof_insulation': 0.167916458049374,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'3a': {
        'new2004': {
            u'common': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                        'infiltration_per_ext_sur_area': 0.000302, 'int_lighting_intensity': 10.76,
                        'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646, 'glass_shgc': 0.25,
                        'glass_visible_transmittance': None},
            u'medium_office': {'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'cooling_cop': 3.66668442928701, 'wall_insulation': 0.0365394788793098,
                              'roof_insulation': 0.234129751336427, 'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                        'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78, 'glass_u_factor': 4.08816,
                        'glass_shgc': 0.25, 'glass_visible_transmittance': None},
            u'medium_office': {'wall_insulation': 0.0507038211662853, 'roof_insulation': 0.107540833299624,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'wall_insulation': 0.00914641899609407, 'roof_insulation': 0.100170449639936,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'3b-coast': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.25, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0365394788793098, 'roof_insulation': 0.234129751336427,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133,
                        'dhw_efficiency': 0.78, 'glass_u_factor': 6.92716, 'glass_shgc': 0.44,
                        'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.0235471103181338, 'roof_insulation': 0.0739805029798716,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.0, 'roof_insulation': 0.0666101193201832,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'3b': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.25, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0365394788793098, 'roof_insulation': 0.234129751336427,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 6.92716, 'glass_shgc': 0.25, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.0382569953608825, 'roof_insulation': 0.167469994584897,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.00914641899609407, 'roof_insulation': 0.160099610925208,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'3c': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 6.92716,
                        'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0365394788793098, 'roof_insulation': 0.234129751336427,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 4.08816, 'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.0507038211662853, 'roof_insulation': 0.0857484110140705,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.0, 'roof_insulation': 0.0783780273543822,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'4a': {
        'new2004': {
            u'common': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                        'infiltration_per_ext_sur_area': 0.000302, 'int_lighting_intensity': 10.76,
                        'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646, 'glass_shgc': 0.39,
                        'glass_visible_transmittance': None},
            u'medium_office': {'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'cooling_cop': 3.66668442928701, 'wall_insulation': 0.0365394788793098,
                              'roof_insulation': 0.234129751336427, 'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                        'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78, 'glass_u_factor': 3.35002,
                        'glass_shgc': 0.36, 'glass_visible_transmittance': None},
            u'medium_office': {'wall_insulation': 0.0812847864409827, 'roof_insulation': 0.13647215254079,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'wall_insulation': 0.0513034841760789, 'roof_insulation': 0.129101768881102,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'4b': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0365394788793098, 'roof_insulation': 0.234129751336427,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 4.08816, 'glass_shgc': 0.36, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.0706187424549297, 'roof_insulation': 0.133950294204999,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.0248084865552216, 'roof_insulation': 0.12657991054531,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'4c': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0539159052450989,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0365394788793098, 'roof_insulation': 0.234129751336427,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 4.08816, 'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.0781229156941291, 'roof_insulation': 0.122523123620942,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.0656864828845443, 'roof_insulation': 0.115152739961254,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'5a': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0870564552646045,
                               'roof_insulation': 0.127338688569477, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0495494599433393, 'roof_insulation': 0.236804989096202,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 3.35002, 'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.0895622041685183, 'roof_insulation': 0.153184148962047,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.0656864828845443, 'roof_insulation': 0.145813765302359,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'5b': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0870564552646045,
                               'roof_insulation': 0.127338688569477, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0495494599433393, 'roof_insulation': 0.236804989096202,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 3.35002, 'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.0895622041685183, 'roof_insulation': 0.159569498000212,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.0410299136700322, 'roof_insulation': 0.152199114340523,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'6a': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0870564552646045,
                               'roof_insulation': 0.127338688569477, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0623673293364369, 'roof_insulation': 0.302609558350619,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 2.95256, 'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.117086892128433, 'roof_insulation': 0.182131064601726,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.100934958592615, 'roof_insulation': 0.174760680942037,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'6b': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.0870564552646045,
                               'roof_insulation': 0.127338688569477, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.0623673293364369, 'roof_insulation': 0.302609558350619,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 2.95256, 'glass_shgc': 0.39, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.104179072774682, 'roof_insulation': 0.166476100021083,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.0886264555081727, 'roof_insulation': 0.159105716361395,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'7': {
        'new2004': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.000302,
                        'int_lighting_intensity': 10.76, 'dhw_efficiency': 0.8, 'glass_u_factor': 3.23646,
                        'glass_shgc': 0.49, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'wall_insulation': 0.119161363096001,
                               'roof_insulation': 0.124663450809702, 'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'wall_insulation': 0.075275148690188, 'roof_insulation': 0.299934320590844,
                              'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'heating_efficiency': 0.8, 'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78,
                        'glass_u_factor': 2.95256, 'glass_shgc': 0.49, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'wall_insulation': 0.133110392015848, 'roof_insulation': 0.20342749135606,
                               'ext_lighting_intensity': 17809, 'int_lighting_intensity': 16.89,
                               'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer",
                              'wall_insulation': 0.120860609077674, 'roof_insulation': 0.196057107696372,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
    u'8': {
        'new2004': {
            u'common': {'infiltration_per_ext_sur_area': 0.000302, 'int_lighting_intensity': 10.76,
                        'dhw_efficiency': 0.8, 'glass_u_factor': 2.61188, 'glass_shgc': 0.3,
                        'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'cooling_cop': 3.23372055845678, 'heating_efficiency': 0.78,
                               'wall_insulation': 0.119161363096001, 'roof_insulation': 0.170145232344671,
                               'ext_lighting_intensity': 14804, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'cooling_cop': 3.66668442928701,
                              'heating_efficiency': 0.8, 'wall_insulation': 0.0872609809472425,
                              'roof_insulation': 0.302609558350619, 'ext_lighting_intensity': 2303, }
        },
        'post1980': {
            u'common': {'infiltration_per_ext_sur_area': 0.001133, 'dhw_efficiency': 0.78, 'glass_u_factor': 2.95256,
                        'glass_shgc': 0.615, 'glass_visible_transmittance': None},
            u'medium_office': {'has_economizer': True, 'economizer': u"DifferentialDryBulb",
                               'heating_efficiency': 0.78, 'wall_insulation': 0.17609406631701,
                               'roof_insulation': 0.2687383686527, 'ext_lighting_intensity': 17809,
                               'int_lighting_intensity': 16.89, 'cooling_cop': 2.80075668762656, },
            u'small_office': {'has_economizer': False, 'economizer': u"NoEconomizer", 'heating_efficiency': 0.8,
                              'wall_insulation': 0.163001240103523, 'roof_insulation': 0.261367984993012,
                              'ext_lighting_intensity': 2766, 'int_lighting_intensity': 19.48,
                              'cooling_cop': 3.06719599275285}
        },
        'pre1980': {

        }
    },
}