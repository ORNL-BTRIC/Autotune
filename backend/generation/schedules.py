__author__ = 'm5z'


def all_schedules(idf_generation_inputs):
    building_type = idf_generation_inputs['building_type']

    schedules = [[u"ScheduleTypeLimits", u"Any Number"],
                 [u"ScheduleTypeLimits", u"Fraction", u"0.0", u"1.0", u"CONTINUOUS"],
                 [u"ScheduleTypeLimits", u"Temperature", u"-60", u"200", u"CONTINUOUS"],
                 [u"ScheduleTypeLimits", u"On/Off", u"0", u"1", u"DISCRETE"],
                 [u"ScheduleTypeLimits", u"Control Type", u"0", u"4", u"DISCRETE"],
                 [u"ScheduleTypeLimits", u"Humidity", u"10", u"90", u"CONTINUOUS"],
                 [u"ScheduleTypeLimits", u"Number"],
                 [u"Schedule:Compact", u"ALWAYS_ON", u"On/Off", u"Through: 12/31", u"For: AllDays", u"Until: 24:00",
                  u"1"],
                 [u"Schedule:Compact", u"ALWAYS_OFF", u"On/Off", u"Through: 12/31", u"For: AllDays", u"Until: 24:00",
                  u"0"],
                 [u"Schedule:Compact", u"ACTIVITY_SCH", u"Any Number", u"Through: 12/31", u"For: AllDays",
                  u"Until: 24:00", u"120."],
                 [u"Schedule:Compact", u"AIR_VELO_SCH", u"Any Number", u"Through: 12/31", u"For: AllDays",
                  u"Until: 24:00", u"0.2"],
                 [u"Schedule:Compact", u"BLDG_OCC_SCH", u"Fraction", u"Through: 12/31", u"For: SummerDesignDay",
                  u"Until: 06:00", u"0.0", u"Until: 22:00", u"1.0", u"Until: 24:00", u"0.05", u"For: Weekdays",
                  u"Until: 06:00", u"0.0", u"Until: 07:00", u"0.1", u"Until: 08:00", u"0.2", u"Until: 12:00",
                  u"0.95", u"Until: 13:00", u"0.5", u"Until: 17:00", u"0.95", u"Until: 18:00", u"0.7", u"Until: 20:00",
                  u"0.4", u"Until: 22:00", u"0.1", u"Until: 24:00", u"0.05", u"For: Saturday", u"Until: 06:00", u"0.0",
                  u"Until: 08:00", u"0.1", u"Until: 14:00", u"0.5", u"Until: 17:00", u"0.1", u"Until: 24:00", u"0.0",
                  u"For: AllOtherDays", u"Until: 24:00", u"0.0"],
                 [u"Schedule:Compact", u"BLDG_LIGHT_SCH", u"Fraction", u"Through: 12/31", u"For: Weekdays",
                  u"Until: 05:00",
                  u"0.05", u"Until: 07:00", u"0.1", u"Until: 08:00", u"0.3", u"Until: 17:00", u"0.9",
                  u"Until: 18:00", u"0.7",
                  u"Until: 20:00", u"0.5", u"Until: 22:00", u"0.3", u"Until: 23:00", u"0.1", u"Until: 24:00",
                  u"0.05",
                  u"For: Saturday", u"Until: 06:00", u"0.05", u"Until: 08:00", u"0.1", u"Until: 14:00",
                  u"0.5", u"Until: 17:00",
                  u"0.15", u"Until: 24:00", u"0.05", u"For: SummerDesignDay", u"Until: 24:00", u"1.0",
                  u"For: WinterDesignDay",
                  u"Until: 24:00", u"0.0", u"For: AllOtherDays", u"Until: 24:00", u"0.05"],
                 [u"Schedule:Compact", u"BLDG_EQUIP_SCH", u"Fraction", u"Through: 12/31", u"For: Weekdays",
                  u"Until: 08:00",
                  u"0.40", u"Until: 12:00", u"0.90", u"Until: 13:00", u"0.80", u"Until: 17:00", u"0.90",
                  u"Until: 18:00",
                  u"0.80", u"Until: 20:00", u"0.60", u"Until: 22:00", u"0.50", u"Until: 24:00", u"0.40",
                  u"For: Saturday",
                  u"Until: 06:00", u"0.30", u"Until: 08:00", u"0.4", u"Until: 14:00", u"0.5", u"Until: 17:00", u"0.35",
                  u"Until: 24:00", u"0.30", u"For: SummerDesignDay", u"Until: 24:00", u"1.0", u"For: WinterDesignDay",
                  u"Until: 24:00", u"0.0", u"For: AllOtherDays", u"Until: 24:00", u"0.30"],
                 [u"Schedule:Compact", u"CLOTHING_SCH", u"Any Number", u"Through: 04/30", u"For: AllDays",
                  u"Until: 24:00", u"1.0", u"Through: 09/30", u"For: AllDays", u"Until: 24:00", u"0.5",
                  u"Through: 12/31", u"For: AllDays", u"Until: 24:00", u"1.0"],
                 [u"Schedule:Compact", u"WORK_EFF_SCH", u"Fraction", u"Through: 12/31", u"For: AllDays",
                  u"Until: 24:00", u"0.0"],
                 [u"Schedule:Compact", u"Dual Zone Control Type Sched", u"Control Type", u"Through: 12/31",
                  u"For: AllDays", u"Until: 24:00", u"4"],
                 [u"Schedule:Compact", u"BLDG_SWH_SCH", u"Fraction", u"Through: 12/31",
                  u"For: Weekdays SummerDesignDay",
                  u"Until: 05:00", u"0.05", u"Until: 06:00", u"0.08", u"Until: 07:00", u"0.07", u"Until: 08:00",
                  u"0.19",
                  u"Until: 09:00", u"0.35", u"Until: 10:00", u"0.38", u"Until: 11:00", u"0.39", u"Until: 12:00",
                  u"0.47",
                  u"Until: 13:00", u"0.57", u"Until: 14:00", u"0.54", u"Until: 15:00", u"0.34", u"Until: 16:00",
                  u"0.33",
                  u"Until: 17:00", u"0.44", u"Until: 18:00", u"0.26", u"Until: 19:00", u"0.21", u"Until: 20:00",
                  u"0.15",
                  u"Until: 21:00", u"0.17", u"Until: 22:00", u"0.08", u"Until: 24:00", u"0.05",
                  u"For: Saturday WinterDesignDay",
                  u"Until: 05:00", u"0.05", u"Until: 06:00", u"0.08", u"Until: 07:00", u"0.07", u"Until: 08:00",
                  u"0.11",
                  u"Until: 09:00", u"0.15", u"Until: 10:00", u"0.21", u"Until: 11:00", u"0.19", u"Until: 12:00",
                  u"0.23",
                  u"Until: 13:00", u"0.20", u"Until: 14:00", u"0.19", u"Until: 15:00", u"0.15", u"Until: 16:00",
                  u"0.13",
                  u"Until: 17:00", u"0.14", u"Until: 21:00", u"0.07", u"Until: 22:00", u"0.09", u"Until: 24:00",
                  u"0.05",
                  u"For: Sunday Holidays AllOtherDays", u"Until: 05:00", u"0.04", u"Until: 06:00", u"0.07",
                  u"Until: 11:00", u"0.04", u"Until: 13:00", u"0.06", u"Until: 14:00", u"0.09", u"Until: 15:00",
                  u"0.06",
                  u"Until: 21:00", u"0.04", u"Until: 22:00", u"0.07", u"Until: 24:00", u"0.04"],
                 [u"Schedule:Compact", u"Water Equipment Latent fract sched", u"Fraction", u"Through: 12/31",
                  u"For: AllDays", u"Until: 24:00", u"0.05"],
                 [u"Schedule:Compact", u"Water Equipment Sensible fract sched", u"Fraction", u"Through: 12/31",
                  u"For: AllDays", u"Until: 24:00", u"0.2"],
                 [u"Schedule:Compact", u"Water Equipment Hot Supply Temp Sched", u"Temperature", u"Through: 12/31",
                  u"For: AllDays", u"Until: 24:00", u"43.3"],
                 [u"Schedule:Compact", u"Water Equipment Temp Sched", u"Temperature", u"Through: 12/31",
                  u"For: AllDays", u"Until: 24:00", u"43.3"],
                 [u"Schedule:Compact", u"SWHSys1 Water Heater Ambient Temperature Schedule Name", u"Temperature",
                  u"Through: 12/31", u"For: AllDays", u"Until: 24:00", u"22.0"],
                 [u"Schedule:Compact", u"SWHSys1 Water Heater Setpoint Temperature Schedule Name", u"Temperature",
                  u"Through: 12/31", u"For: AllDays", u"Until: 24:00", u"60.0"],
                 [u"Schedule:Compact", u"SWHSys1-Loop-Temp-Schedule", u"Temperature", u"Through: 12/31",
                  u"For: AllDays", u"Until: 24:00", u"60.0"],
                 [u"Schedule:Compact", u"Seasonal-Reset-Supply-Air-Temp-Sch", u"Temperature", u"Through: 12/31",
                  u"For: AllDays", u"Until: 24:00", u"12.8"]]

    if building_type == u"medium_office":
        schedules.append(
            [u"Schedule:Compact", u"BLDG_ELEVATORS", u"Fraction", u"Through: 12/31", u"For: Weekdays SummerDesignDay",
             u"Until: 07:00", u"0.0", u"Until: 08:00", u"0.35", u"Until: 09:00", u"0.69", u"Until: 10:00", u"0.43",
             u"Until: 11:00", u"0.37", u"Until: 12:00", u"0.43", u"Until: 13:00", u"0.58", u"Until: 14:00", u"0.48",
             u"Until: 15:00", u"0.37", u"Until: 16:00", u"0.37", u"Until: 17:00", u"0.46", u"Until: 18:00", u"0.62",
             u"Until: 19:00", u"0.12", u"Until: 20:00", u"0.04", u"Until: 21:00", u"0.04", u"Until: 24:00", u"0.00",
             u"For: Saturday WinterDesignDay", u"Until: 07:00", u"0.0", u"Until: 08:00", u"0.16", u"Until: 09:00",
             u"0.14", u"Until: 10:00", u"0.21", u"Until: 11:00", u"0.18", u"Until: 12:00", u"0.25", u"Until: 13:00",
             u"0.21", u"Until: 14:00", u"0.13", u"Until: 15:00", u"0.08", u"Until: 16:00", u"0.04", u"Until: 17:00",
             u"0.05", u"Until: 18:00", u"0.06", u"Until: 24:00", u"0.00", u"For: Sunday Holidays AllOtherDays",
             u"Until: 24:00", u"0.0"])

    schedules.append(_schedule_helper(idf_generation_inputs, schedule_name=u"CLGSETP_SCH", schedule_type=u"Temperature",
                                      occupied_value=idf_generation_inputs['cooling_setpoint'],
                                      unoccupied_value=idf_generation_inputs['cooling_setback'] if
                                      idf_generation_inputs['has_setback'] else
                                      idf_generation_inputs['cooling_setpoint'], winter_design_day_separate=True,
                                      summer_design_day_separate=False))
    schedules.append(_schedule_helper(idf_generation_inputs, schedule_name=u"HTGSETP_SCH", schedule_type=u"Temperature",
                                      occupied_value=idf_generation_inputs['heating_setpoint'],
                                      unoccupied_value=idf_generation_inputs['heating_setback'] if
                                      idf_generation_inputs['has_setback'] else
                                      idf_generation_inputs['heating_setpoint'], winter_design_day_separate=True,
                                      summer_design_day_separate=True))
    schedules.append(_schedule_helper(idf_generation_inputs, schedule_name=u"HVACOperationSchd",
                                      schedule_type=u"On/Off", occupied_value=1.0, unoccupied_value=0.0,
                                      winter_design_day_separate=False, summer_design_day_separate=False))
    schedules.append(_schedule_helper(idf_generation_inputs, schedule_name=u"INFIL_QUARTER_ON_SCH",
                                      schedule_type=u"Fraction", occupied_value=0.25, unoccupied_value=1.0,
                                      winter_design_day_separate=False, summer_design_day_separate=False))
    schedules.append(_schedule_helper(idf_generation_inputs, schedule_name=u"MinOA_MotorizedDamper_Sched",
                                      schedule_type=u"Fraction", occupied_value=1.0, unoccupied_value=0.0,
                                      winter_design_day_separate=False, summer_design_day_separate=False))

    return schedules


def _schedule_helper(idf_generation_inputs, schedule_name, schedule_type, occupied_value, unoccupied_value,
                     winter_design_day_separate, summer_design_day_separate):
    has_weekend = idf_generation_inputs['has_weekend_occupancy']
    weekday_start_time = idf_generation_inputs['weekday_start_time']
    weekday_end_time = idf_generation_inputs['weekday_end_time']
    weekend_start_time = idf_generation_inputs['weekend_start_time']
    weekend_end_time = idf_generation_inputs['weekend_end_time']
    weekend_occupancy_days = idf_generation_inputs['weekend_occupancy_type'].capitalize()
    schedule = [u"Schedule:Compact", schedule_name, schedule_type, u"Through: 12/31",
                u"For: Weekdays" + (u" SummerDesignDay" if not summer_design_day_separate else u"") +
                (u" WinterDesignDay" if not winter_design_day_separate and not has_weekend else u""),
                u"Until: " + weekday_start_time, unicode(unoccupied_value),
                u"Until: " + weekday_end_time, unicode(occupied_value),
                u"Until: 24:00", unicode(unoccupied_value)]
    if summer_design_day_separate:
        schedule.extend([u"For: SummerDesignDay", u"Until: 24:00", unicode(unoccupied_value)])
    if has_weekend:
        schedule.extend([u"For: " + weekend_occupancy_days +
                         (u" WinterDesignDay" if not winter_design_day_separate else u""),
                         u"Until: " + weekend_start_time, unicode(unoccupied_value),
                         u"Until: " + weekend_end_time, unicode(occupied_value),
                         u"Until: 24:00", unicode(unoccupied_value)])
        if winter_design_day_separate:
            schedule.extend([u"For: WinterDesignDay", u"Until: 24:00", unicode(occupied_value),
                             u"For: AllOtherDays", u"Until: 24:00", unicode(unoccupied_value)])
        else:
            schedule.extend([u"For: AllOtherDays", u"Until: 24:00", unicode(unoccupied_value)])
    else:
        if winter_design_day_separate:
            schedule.extend([u"For: WinterDesignDay", u"Until: 24:00", unicode(occupied_value)])
        schedule.extend([u"For: AllOtherDays", u"Until: 24:00", unicode(unoccupied_value)])
    return schedule