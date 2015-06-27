__author__ = 'm5z'

from validation import Validation


def output_variables(unsafe_building_type):
    validate = Validation()
    validate.unsafe_data['building_type'] = unsafe_building_type
    building_type = validate._clean_building_type()
    return _output_variables(building_type)


def _output_variables(safe_building_type):
    outputs = [[u"OutputControl:ReportingTolerances", u"0.556", u"0.556"], [u"Output:SQLite", u"Simple"],
               [u"Output:VariableDictionary", u"IDF", u"Unsorted"], [u"Output:Surfaces:List", u"Details"],
               [u"Output:Surfaces:Drawing", u"DXF"], [u"Output:Constructions", u"Constructions"],
               [u"Output:Meter", u"Electricity:Facility", u"HOURLY"], [u"Output:Meter", u"Fans:Electricity", u"HOURLY"],
               [u"Output:Meter", u"Cooling:Electricity", u"HOURLY"],
               [u"Output:Meter", u"Heating:Electricity", u"HOURLY"],
               [u"Output:Meter", u"InteriorLights:Electricity", u"HOURLY"],
               [u"Output:Meter", u"InteriorEquipment:Electricity", u"HOURLY"],
               [u"Output:Meter", u"Gas:Facility", u"HOURLY"], [u"Output:Meter", u"Heating:Gas", u"HOURLY"],
               [u"Output:Meter", u"InteriorEquipment:Gas", u"HOURLY"],
               [u"Output:Meter", u"Water Heater:WaterSystems:Gas", u"HOURLY"],
               [u"Output:Variable", u"*", u"Outdoor Dry Bulb", u"HOURLY"],
               [u"Output:Variable", u"*", u"Outdoor Humidity Ratio", u"HOURLY"],
               [u"Output:Variable", u"*", u"Outdoor Relative Humidity", u"HOURLY"],
               [u"Output:Variable", u"*", u"AirLoopHVAC Actual Outdoor Air Fraction", u"HOURLY"],
               [u"Output:Variable", u"*", u"Air Loop System Cycle On/Off Status", u"HOURLY"],
               [u"Output:Variable", u"*", u"AirLoopHVAC Outdoor Air Economizer Status", u"HOURLY"],
               [u"Output:Variable", u"*", u"Air Loop Total Heating Energy", u"HOURLY"],
               [u"Output:Variable", u"*", u"Air Loop Total Cooling Energy", u"HOURLY"],
               [u"Output:Variable", u"*", u"Air Loop Fan Electric Consumption", u"HOURLY"],
               [u"Output:Variable", u"*", u"Total Building Electric Demand", u"TimeStep"],
               [u"OutputControl:Table:Style", u"HTML"],
               [u"Output:Table:SummaryReports", u"AnnualBuildingUtilityPerformanceSummary",
                u"InputVerificationandResultsSummary", u"ClimaticDataSummary", u"EnvelopeSummary", u"EquipmentSummary",
                u"ComponentSizingSummary", u"HVACSizingSummary", u"SystemSummary"],
               [u"Output:Table:Monthly", u"Emissions Data Summary", u"4", u"CO2:Facility", u"SumOrAverage",
                u"NOx:Facility", u"SumOrAverage", u"SO2:Facility", u"SumOrAverage", u"PM:Facility", u"SumOrAverage",
                u"Hg:Facility", u"SumOrAverage", u"WaterEnvironmentalFactors:Facility", u"SumOrAverage",
                u"Carbon Equivalent:Facility", u"SumOrAverage"],
               [u"Output:Table:Monthly", u"Components of Peak Electrical Demand", u"3", u"Electricity:Facility",
                u"SumOrAverage", u"Electricity:Facility", u"Maximum", u"InteriorLights:Electricity",
                u"ValueWhenMaximumOrMinimum", u"InteriorEquipment:Electricity", u"ValueWhenMaximumOrMinimum",
                u"Fans:Electricity", u"ValueWhenMaximumOrMinimum", u"Heating:Electricity", u"ValueWhenMaximumOrMinimum",
                u"Cooling:Electricity", u"ValueWhenMaximumOrMinimum", u"ExteriorLights:Electricity",
                u"ValueWhenMaximumOrMinimum", u"Pumps:Electricity", u"ValueWhenMaximumOrMinimum",
                u"HeatRejection:Electricity", u"ValueWhenMaximumOrMinimum", u"ExteriorEquipment:Electricity",
                u"ValueWhenMaximumOrMinimum", u"Humidification:Electricity", u"ValueWhenMaximumOrMinimum",
                u"HeatRecovery:Electricity", u"ValueWhenMaximumOrMinimum", u"WaterSystems:Electricity",
                u"ValueWhenMaximumOrMinimum", u"Refrigeration:Electricity", u"ValueWhenMaximumOrMinimum",
                u"Generators:Electricity", u"ValueWhenMaximumOrMinimum", u"ElectricityProduced:Facility",
                u"ValueWhenMaximumOrMinimum"],
               [u"Output:Table:Monthly", u"Heating Part Load Performance", u"0", u"Heating Coil Gas Consumption Rate",
                u"SumOrAverage", u"Heating Coil Gas Consumption Rate", u"Maximum"],
               [u"Output:Table:Monthly", u"Cooling Part Load Performance", u"0", u"DX Cooling Coil Electric Power",
                u"SumOrAverage", u"DX Cooling Coil Electric Power", u"Maximum"],
               [u"Output:Table:Monthly", u"Fan Part Load Performance", u"0", u"Fan Electric Power", u"SumOrAverage",
                u"Fan Electric Power", u"Maximum"],
               [u"Output:Table:TimeBins", u"*", u"Zone Air Relative Humidity", u"60", u"10", u"4"],
               [u"Output:Table:TimeBins", u"*", u"AirLoopHVAC Actual Outdoor Air Fraction", u"0.00", u"0.20", u"5"],
               [u"Output:Table:TimeBins", u"*", u"Availability Manager Night Cycle Control Status", u"0", u"1", u"4"]]

    if safe_building_type == u"medium_office":
        outputs.append([u"Output:Variable", u"*", u"Boiler Gas Consumption", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Boiler Water Inlet Temp", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Boiler Water Outlet Temp", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Boiler Part-Load Ratio", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Plant Loop System Cycle On/Off Status", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Plant Loop Heating Demand", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Plant Loop InletNode Flowrate", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Plant Loop InletNode Temperature", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Plant Loop OutletNode Temperature", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Plant Loop Unmet Demand", u"HOURLY"])
        outputs.append([u"Output:Variable", u"*", u"Air Loop Heating Coil Hot Water Consumption", u"HOURLY"])
        outputs.append([u"Output:Table:Monthly", u"Boiler Part Load Performance", u"2", u"Boiler Part-Load Ratio",
                        u"SumOrAverage", u"Boiler Part-Load Ratio", u"Maximum"])

    return outputs