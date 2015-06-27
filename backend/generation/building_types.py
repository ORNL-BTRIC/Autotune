__author__ = 'm5z'


def common(idf_generation_inputs, floors):
    building_common = []
    ext_light_intensity = idf_generation_inputs['ext_lighting_intensity']
    building_type = idf_generation_inputs['building_type']

    if building_type == u"medium_office":
        heating_sizing = u"1.33"
        cooling_sizing = u"1.33"

        floor_has_interior_zone = False
        zone_name = None
        if 1 in floors:
            for zone in floors[1]:
                if not zone.zone_info['is_plenum'] and zone.zone_info['is_interior_zone']:
                    zone_name = zone.zone_name()
                    floor_has_interior_zone = True
                    break
            if not floor_has_interior_zone:
                for zone in floors[1]:
                    if not zone.zone_info['is_plenum']:
                        zone_name = zone.zone_name()
                        break
        else:
            for floor in floors:
                for zone in floors[floor]:
                    if not zone.zone_info['is_plenum'] and zone.zone_info['is_interior_zone']:
                        zone_name = zone.zone_name()
                        floor_has_interior_zone = True
                        break
                if not floor_has_interior_zone:
                    for zone in floors[floor]:
                        if not zone.zone_info['is_plenum']:
                            zone_name = zone.zone_name()
                            break
                if not zone_name is None:
                    break
        building_common.append([u"ElectricEquipment", zone_name + u"_Elevators_Equip", zone_name,
                                u"BLDG_ELEVATORS", u"EquipmentLevel", u"32109.8901098901", u"", u"", u"0.0000",
                                u"0.5000", u"0.0000", u"Elevators"])
    elif building_type == u"small_office":
        heating_sizing = u"1.2"
        cooling_sizing = u"1.2"
    else:
        heating_sizing = u"1.33"
        cooling_sizing = u"1.33"

    building_common.append([u"Version", u"7.0"])
    building_common.append([u"SimulationControl", u"YES", u"YES", u"YES", u"NO", u"YES"])
    building_common.append(
        [u"Building", u"Ref_Bldg_" + building_type + u'_' + unicode(idf_generation_inputs['building_age']) +
                      u"_v1.3_5.0_modified",
         unicode(idf_generation_inputs['orientation']), # u"0.0000",
         u"City", u"0.0400", u"0.2000", u"FullInteriorAndExterior", u"25", u"6"])
    building_common.append([u"ShadowCalculation", u"7", u"15000"])
    building_common.append([u"SurfaceConvectionAlgorithm:Inside", u"TARP"])
    building_common.append([u"SurfaceConvectionAlgorithm:Outside", u"DOE-2"])
    building_common.append([u"HeatBalanceAlgorithm", u"ConductionTransferFunction", u"200.0000"])
    building_common.append([u"ZoneAirHeatBalanceAlgorithm", u"AnalyticalSolution"])
    building_common.append([u"Timestep", unicode(idf_generation_inputs['timestep'])])
    building_common.append([u"ConvergenceLimits", u"2", u"25"])
    building_common.append(
        [u"RunPeriod", u"", u"1", u"1", u"12", u"31", u"Sunday", u"No", u"No", u"No", u"Yes", u"Yes", u"1.0000"])
    building_common.append([u"RunPeriodControl:SpecialDays", u"New Years Day", u"January 1", u"1", u"Holiday"])
    building_common.append([u"RunPeriodControl:SpecialDays", u"Veterans Day", u"November 11", u"1", u"Holiday"])
    building_common.append([u"RunPeriodControl:SpecialDays", u"Christmas", u"December 25", u"1", u"Holiday"])
    building_common.append([u"RunPeriodControl:SpecialDays", u"Independence Day", u"July 4", u"1", u"Holiday"])
    building_common.append([u"RunPeriodControl:SpecialDays", u"MLK Day", u"3rd Monday in January", u"1", u"Holiday"])
    building_common.append(
        [u"RunPeriodControl:SpecialDays", u"Presidents Day", u"3rd Monday in February", u"1", u"Holiday"])
    building_common.append([u"RunPeriodControl:SpecialDays", u"Memorial Day", u"Last Monday in May", u"1", u"Holiday"])
    building_common.append(
        [u"RunPeriodControl:SpecialDays", u"Labor Day", u"1st Monday in September", u"1", u"Holiday"])
    building_common.append(
        [u"RunPeriodControl:SpecialDays", u"Columbus Day", u"2nd Monday in October", u"1", u"Holiday"])
    building_common.append(
        [u"RunPeriodControl:SpecialDays", u"Thanksgiving", u"4th Thursday in November", u"1", u"Holiday"])
    building_common.append([u"RunPeriodControl:DaylightSavingTime", u"2nd Sunday in March", u"1st Sunday in November"])
    building_common.append([u"GlobalGeometryRules", u"UpperLeftCorner", u"Counterclockwise", u"Relative", u"Relative"])
    building_common.append([u"Exterior:Lights", u"Exterior Facade Lighting", u"ALWAYS_ON", unicode(ext_light_intensity),
                            u"AstronomicalClock", u"Exterior Facade Lighting"])
    building_common.append([u"Sizing:Parameters", heating_sizing, cooling_sizing, u"6"])
    '''
    building_common.append(
        [u"Output:Table:SummaryReports", u"AllSummaryAndMonthly", u"AnnualBuildingUtilityPerformanceSummary",
         u"InputVerificationandResultsSummary", u"ClimaticDataSummary", u"EnvelopeSummary", u"EquipmentSummary",
         u"ComponentSizingSummary", u"HVACSizingSummary", u"SystemSummary"])
    building_common.append([u"Output:Table:TimeBins", u"*", u"Zone Air Relative Humidity", u"60", u"10", u"4"])
    building_common.append(
        [u"Output:Table:TimeBins", u"*", u"AirLoopHVAC Actual Outdoor Air Fraction", u"0.00", u"0.20", u"5"])
    building_common.append(
        [u"Output:Table:TimeBins", u"*", u"Availability Manager Night Cycle Control Status", u"0", u"1", u"4"])
    building_common.append(
        [u"Output:Table:Monthly", u"Emissions Data Summary", u"4", u"CO2:Facility", u"SumOrAverage", u"NOx:Facility",
         u"SumOrAverage", u"SO2:Facility", u"SumOrAverage", u"PM:Facility", u"SumOrAverage", u"Hg:Facility",
         u"SumOrAverage", u"WaterEnvironmentalFactors:Facility", u"SumOrAverage", u"Carbon Equivalent:Facility",
         u"SumOrAverage"])
    building_common.append(
        [u"Output:Table:Monthly", u"Components of Peak Electrical Demand", u"3", u"Electricity:Facility",
         u"SumOrAverage", u"Electricity:Facility", u"Maximum", u"InteriorLights:Electricity",
         u"ValueWhenMaximumOrMinimum", u"InteriorEquipment:Electricity", u"ValueWhenMaximumOrMinimum",
         u"Fans:Electricity", u"ValueWhenMaximumOrMinimum", u"Heating:Electricity", u"ValueWhenMaximumOrMinimum",
         u"Cooling:Electricity", u"ValueWhenMaximumOrMinimum", u"ExteriorLights:Electricity",
         u"ValueWhenMaximumOrMinimum", u"Pumps:Electricity", u"ValueWhenMaximumOrMinimum", u"HeatRejection:Electricity",
         u"ValueWhenMaximumOrMinimum", u"ExteriorEquipment:Electricity", u"ValueWhenMaximumOrMinimum",
         u"Humidification:Electricity", u"ValueWhenMaximumOrMinimum", u"HeatRecovery:Electricity",
         u"ValueWhenMaximumOrMinimum", u"WaterSystems:Electricity", u"ValueWhenMaximumOrMinimum",
         u"Refrigeration:Electricity", u"ValueWhenMaximumOrMinimum", u"Generators:Electricity",
         u"ValueWhenMaximumOrMinimum", u"ElectricityProduced:Facility", u"ValueWhenMaximumOrMinimum"])
    building_common.append(
        [u"Output:Table:Monthly", u"Heating Part Load Performance", u"0", u"Heating Coil Gas Consumption Rate",
         u"SumOrAverage", u"Heating Coil Gas Consumption Rate", u"Maximum"])
    building_common.append(
        [u"Output:Table:Monthly", u"Cooling Part Load Performance", u"0", u"DX Cooling Coil Electric Power",
         u"SumOrAverage", u"DX Cooling Coil Electric Power", u"Maximum"])
    building_common.append(
        [u"Output:Table:Monthly", u"Fan Part Load Performance", u"0", u"Fan Electric Power", u"SumOrAverage",
         u"Fan Electric Power", u"Maximum"])
    building_common.append([u"OutputControl:Table:Style", u"Comma"])
    building_common.append([u"OutputControl:ReportingTolerances", u"0.556", u"0.556"])
    building_common.append([u"Output:EnvironmentalImpactFactors", u"Monthly"])
    building_common.append(
        [u"EnvironmentalImpactFactors", u"0.663", u"4.18", u"0.585", u"80.7272", u"6.2727", u"0.2727"])
    '''
    building_common.append([u"Output:Diagnostics", u"DisplayExtraWarnings"])
    return building_common