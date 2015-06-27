__author__ = 'm5z'


def output_hvac_list(floors, idf_generation_inputs):
    hvac_output = []

    hvac_type = idf_generation_inputs['hvac_type']
    heating_coil_type = idf_generation_inputs['heating_coil'].capitalize()
    has_reheat = idf_generation_inputs['has_reheat']
    reheating_coil_type = idf_generation_inputs['reheat_coil'].capitalize()
    heating_efficiency = idf_generation_inputs['heating_efficiency']
    cooling_cop = idf_generation_inputs['cooling_cop']
    fan_efficiency = idf_generation_inputs['fan_efficiency']
    static_pressure = idf_generation_inputs['fan_static_pressure']
    dcv = idf_generation_inputs['has_dcv']
    oa_per_person = idf_generation_inputs['oa_vent_per_person']
    oa_per_area = idf_generation_inputs['oa_vent_per_area']
    has_economizer = idf_generation_inputs['has_economizer']
    economizer = idf_generation_inputs['economizer']
    use_mechanical_vent = idf_generation_inputs['use_mechanical_vent']

    if dcv:
        use_mechanical_vent = True

    if idf_generation_inputs['has_night_cycle']:
        night_cycle = idf_generation_inputs['night_cycle']
    else:
        night_cycle = u"StayOff"

    by_floor = False
    if hvac_type == u"vav":
        hvac_name = u"VAV-MZ"
        by_floor = True
        hvac_output.extend(_vav_performance_curves())
    elif hvac_type == u"psz_onoff":
        hvac_name = u"PSZ-AC"
        hvac_output.extend(_psz_performance_curves())
    elif hvac_type == u"psz_cav":
        hvac_name = u"PSZ-AC"
        hvac_output.extend(_psz_performance_curves())
    else:
        hvac_name = u"PSZ-AC"
        hvac_output.extend(_psz_performance_curves())

    hvac_number = 1
    for floor in floors.keys():
        if not by_floor:
            for zone in floors[floor]:
                if not zone.zone_info['is_plenum']:
                    hvac = u"".join([hvac_name, u":", unicode(hvac_number)])

                    hvac_output.extend(_common_system_objects(floors[floor], hvac, dcv, night_cycle))
                    hvac_output.extend(_output_zone_hvac_list(zone.zone_name(), hvac_type, heating_coil_type,
                                                              fan_efficiency, static_pressure, cooling_cop,
                                                              heating_efficiency, oa_per_person, oa_per_area,
                                                              has_reheat, has_economizer, economizer,
                                                              use_mechanical_vent, hvac=hvac))

                    hvac_number += 1

        else:
            hvac = u"".join([hvac_name, u":", unicode(hvac_number)])

            num_of_plenums = 0
            for zone in floors[floor]:
                if zone.zone_info['is_plenum']:
                    num_of_plenums += 1

            plenum_name = None
            if num_of_plenums == 1:
                for zone in floors[floor]:
                    if zone.zone_info['is_plenum']:
                        plenum_name = zone.zone_name()

            hvac_output.extend(_common_system_objects(floors[floor], hvac, dcv, night_cycle, use_mechanical_vent))
            hvac_output.extend(_output_system_hvac_VAV(floors[floor], hvac, heating_coil_type, fan_efficiency,
                                                       static_pressure, cooling_cop, heating_efficiency, has_economizer,
                                                       economizer, use_mechanical_vent, plenum_name=plenum_name))
            for zone in floors[floor]:
                if not zone.zone_info['is_plenum']:
                    hvac_output.extend(_output_zone_hvac_list(zone.zone_name(), hvac_type, heating_coil_type,
                                                              fan_efficiency, static_pressure, cooling_cop,
                                                              heating_efficiency, oa_per_person, oa_per_area,
                                                              has_reheat, has_economizer, economizer,
                                                              use_mechanical_vent, is_vav=True,
                                                              reheating_coil_type=reheating_coil_type))
            hvac_number += 1

    return hvac_output


def _output_zone_hvac_list(zone_name, hvac_type, heating_coil_type, fan_efficiency, static_pressure, cooling_cop,
                           heating_efficiency, oa_per_person, oa_per_area, has_reheat, has_economizer, economizer,
                           use_mechanical_vent, is_vav=False, hvac=None, reheating_coil_type=None):
    zone_hvac = []

    if is_vav:
        zone_hvac.extend(_zone_vav_list(zone_name, reheating_coil_type, has_reheat))
        #Zone Cooling Design Supply Air Temperature {C}
        cooling_supply = u"12.8000"
        #Zone Heating Design Supply Air Temperature {C}
        heating_supply = u"50.0000"
        # vav box node list
        zone_hvac.append([u"NodeList", zone_name + u" Inlet Nodes",
                          zone_name + u" VAV Box Outlet Node Name"])
    else:
        if hvac_type == u"psz_cav":
            zone_hvac.extend(_output_system_hvac_PSZ_CAV(zone_name, hvac, heating_coil_type, fan_efficiency,
                                                         static_pressure, cooling_cop, heating_efficiency,
                                                         has_economizer, economizer, use_mechanical_vent))
            cooling_supply = u"14.0000"
            heating_supply = u"40.0000"
        else:
            zone_hvac.extend(_output_system_hvac_PSZ_ONOFF(zone_name, hvac, heating_coil_type, fan_efficiency,
                                                           static_pressure, cooling_cop, heating_efficiency,
                                                           has_economizer, economizer, use_mechanical_vent))
            cooling_supply = u"14.0000"
            heating_supply = u"40.0000"

    zone_hvac.append([u"Sizing:Zone", zone_name, cooling_supply, heating_supply, u"0.0085", u"0.0080",
                      u"SZ DSOA " + zone_name, u"", u"", u"DesignDay", u"", u"", u"", u"", u"DesignDay", u"",
                      u"", u"", u"", u"", u""])
    # zone hvac equipment connections
    zone_hvac.append([u"ZoneHVAC:EquipmentConnections", zone_name, zone_name + u" Equipment",
                      zone_name + u" Inlet Nodes", u"", zone_name + u" Air Node",
                      zone_name + u" Return Air Node Name"])
    # zone control thermostat
    zone_hvac.append([u"ZoneControl:Thermostat", zone_name + u" Thermostat", zone_name,
                      u"Dual Zone Control Type Sched", u"ThermostatSetpoint:DualSetpoint",
                      zone_name + u" DualSPSched"])
    # thermostat setpoint: dual setpoint
    zone_hvac.append([u"ThermostatSetpoint:DualSetpoint", zone_name + u" DualSPSched",
                      u"HTGSETP_SCH", u"CLGSETP_SCH"])
    # design specification: outdoor air
    zone_hvac.append([u"DesignSpecification:OutdoorAir", u"SZ DSOA " + zone_name, u"Sum",
                      unicode(oa_per_person), unicode(oa_per_area), u"0", u"0"])
    return zone_hvac


def _return_air_nodes(zones):
    nodes = []
    for zone in zones:
        if not zone.zone_info['is_plenum']:
            nodes.append(zone.zone_name() + u" Return Air Node Name")
    return nodes


def _zone_splitter(zones):
    nodes = []
    for zone in zones:
        if not zone.zone_info['is_plenum']:
            nodes.append(zone.zone_name() + u" VAV Box Inlet Node Name")
    return nodes


def _controller_mechanical_ventilation(zones):
    controller = []
    for zone in zones:
        if not zone.zone_info['is_plenum']:
            controller.extend([zone.zone_name(), u"SZ DSOA " + zone.zone_name(), u"1.0", u"0.8", u""])
    return controller


def _zone_vav_list(zone_name, reheating_coil_type, has_reheat):
    zone_hvac = []
    if has_reheat:
        reheat_terminal = u"Reheat"
        zone_hvac.append([u"AirTerminal:SingleDuct:VAV:Reheat", zone_name + u" VAV Box Component", u"ALWAYS_ON",
                          zone_name + u" VAV Box Damper Node", zone_name + u" VAV Box Inlet Node Name", u"autosize",
                          u"Constant", u"0.3", u"", u"", u"Coil:Heating:" + reheating_coil_type,
                          zone_name + u" VAV Box Reheat Coil", u"autosize", u"0.0",
                          zone_name + u" VAV Box Outlet Node Name", u"0.001", u"NORMAL"])
        # zone reheat coil
        zone_hvac.append([u"Coil:Heating:" + reheating_coil_type, zone_name + u" VAV Box Reheat Coil", u"ALWAYS_ON",
                          u"1", u"autosize", zone_name + u" VAV Box Damper Node",
                          zone_name + u" VAV Box Outlet Node Name"])
    else:
        reheat_terminal = u"NoReheat"
        zone_hvac.append([u"AirTerminal:SingleDuct:VAV:NoReheat", zone_name + u" VAV Box Component",
                          u"HVACOperationSchd", zone_name + u" VAV Box Outlet Node Name",
                          zone_name + u" VAV Box Inlet Node Name", u"autosize", u"Constant", u"0.3", u"", u""])

    # zone hvac air distribution unit
    zone_hvac.append([u"ZoneHVAC:AirDistributionUnit", zone_name + u" VAV Box",
                      zone_name + u" VAV Box Outlet Node Name",
                      u"AirTerminal:SingleDuct:VAV:" + reheat_terminal, zone_name + u" VAV Box Component"])
    # zone hvac equipment list
    zone_hvac.append([u"ZoneHVAC:EquipmentList", zone_name + u" Equipment", u"ZoneHVAC:AirDistributionUnit",
                      zone_name + u" VAV Box", u"1", u"1"])

    return zone_hvac


def _common_system_objects(zones, hvac, dcv, night_cycle, use_mechanical_vent):
    system_hvac = []
    if use_mechanical_vent:
        controller_mech_vent = [u"Controller:MechanicalVentilation", hvac + u" DCVObject",
                                u"HVACOperationSchd", u"Yes" if dcv else u"No",
                                u"VentilationRateProcedure"]
        controller_mech_vent.extend(_controller_mechanical_ventilation(zones))
        system_hvac.append(controller_mech_vent)
    system_hvac.append([u"AirLoopHVAC:ControllerList", hvac + u"_OA_Controllers",
                        u"Controller:OutdoorAir", hvac + u"_OA_Controller"])
    system_hvac.append([u"AirLoopHVAC", hvac + u"", u"",
                        hvac + u" Availability Manager List", u"autosize",
                        hvac + u" Air Loop Branches", u"",
                        hvac + u" Supply Equipment Inlet Node",
                        hvac + u" Zone Equipment Outlet Node",
                        hvac + u" Zone Equipment Inlet Node",
                        hvac + u" Supply Equipment Outlet Node"])
    system_hvac.append([u"AirLoopHVAC:OutdoorAirSystem:EquipmentList", hvac + u"_OA_Equipment",
                        u"OutdoorAir:Mixer", hvac + u"_OAMixing Box"])
    system_hvac.append([u"AirLoopHVAC:OutdoorAirSystem", hvac + u"_OA",
                        hvac + u"_OA_Controllers", hvac + u"_OA_Equipment",
                        hvac + u" Availability Manager List"])
    #system_hvac.append([u"AirLoopHVAC:SupplyPath", hvac + u"",
    #                    hvac + u" Zone Equipment Inlet Node", u"AirLoopHVAC:ZoneSplitter",
    #                    hvac + u" Supply Air Splitter"])
    system_hvac.append([u"BranchList", hvac + u" Air Loop Branches",
                        hvac + u" Air Loop Main Branch"])
    #system_hvac.append([u"NodeList", hvac + u"_OANode List",
    #                    hvac + u"_OAInlet Node"])
    system_hvac.append([u"OutdoorAir:NodeList", hvac + u"_OANode List"])
    system_hvac.append([u"AvailabilityManager:NightCycle", hvac + u" Availability Manager",
                        u"ALWAYS_ON", u"HVACOperationSchd", night_cycle, u"1.0", u"1800"])
    system_hvac.append([u"AvailabilityManagerAssignmentList", hvac + u" Availability Manager List",
                        u"AvailabilityManager:NightCycle", hvac + u" Availability Manager"])
    return system_hvac


def _output_system_hvac_PSZ_CAV(zone_name, hvac, heating_coil_type, fan_efficiency, static_pressure, cooling_cop,
                                heating_efficiency, has_economizer, economizer, use_mechanical_vent):
    zone_hvac = []
    zone_hvac.append([u"Sizing:System", hvac, u"Sensible", u"AUTOSIZE", u"1.0", u"7.0", u"0.008", u"12.8000",
                      u"0.008", u"12.8000", u"40.0", u"NonCoincident", u"No", u"No", u"0.0085", u"0.0080",
                      u"DesignDay", u"", u"DesignDay", u"", u"" if use_mechanical_vent else u"ZoneSum"])
    zone_hvac.append([u"AirTerminal:SingleDuct:Uncontrolled", zone_name + u" Direct Air", u"ALWAYS_ON",
                      zone_name + u" Direct Air Inlet Node Name", u"autosize"])
    zone_hvac.append([u"ZoneHVAC:EquipmentList", zone_name + u" Equipment",
                      u"AirTerminal:SingleDuct:Uncontrolled", zone_name + u" Direct Air", u"1", u"1"])
    zone_hvac.append([u"Fan:ConstantVolume", hvac + u"_Fan", u"HVACOperationSchd", unicode(fan_efficiency),
                      unicode(static_pressure), u"autosize", u"0.825", u"1.0", hvac + u"_HeatC-" + hvac + u"_FanNode",
                      hvac + u" Supply Equipment Outlet Node", u"Fan Energy"])
    zone_hvac.append([u"Coil:Cooling:DX:SingleSpeed", hvac + u"_CoolC DXCoil", u"ALWAYS_ON", u"autosize", u"autosize",
                      unicode(cooling_cop), u"autosize", u"", hvac + u"_OA-" + hvac + u"_CoolCNode",
                      hvac + u"_CoolC-" + hvac + u"_HeatCNode", u"Cool-Cap-fT", u"ConstantCubic", u"Cool-EIR-fT",
                      u"ConstantCubic", u"Cool-PLF-fPLR"])
    zone_hvac.append([u"AirLoopHVAC:UnitaryCoolOnly", hvac + u"_CoolC", u"ALWAYS_ON",
                      hvac + u"_OA-" + hvac + u"_CoolCNode", hvac + u"_CoolC-" + hvac + u"_HeatCNode",
                      hvac + u"_CoolC-" + hvac + u"_HeatCNode", u"Coil:Cooling:DX:SingleSpeed",
                      hvac + u"_CoolC DXCoil"])
    zone_hvac.append(
        [u"Coil:Heating:" + heating_coil_type, hvac + u"_HeatC", u"ALWAYS_ON", unicode(heating_efficiency), u"autosize",
         hvac + u"_CoolC-" + hvac + u"_HeatCNode",
         hvac + u"_HeatC-" + hvac + u"_FanNode",
         hvac + u"_HeatC-" + hvac + u"_FanNode"])
    zone_hvac.append([u"Controller:OutdoorAir", hvac + u"_OA_Controller", hvac + u"_OARelief Node",
                      hvac + u" Supply Equipment Inlet Node", hvac + u"_OA-" + hvac + u"_CoolCNode",
                      hvac + u"_OAInlet Node", u"autosize", u"autosize",
                      economizer if has_economizer else u"NoEconomizer", u"ModulateFlow",
                      u"28.0", u"64000.0", u"", u"", u"-100.0", u"NoLockout", u"FixedMinimum",
                      u"MinOA_MotorizedDamper_Sched", u"", u"",
                      hvac + u" DCVObject" if use_mechanical_vent else u""])
    zone_hvac.append([u"OutdoorAir:Mixer", hvac + u"_OAMixing Box", hvac + u"_OA-" + hvac + u"_CoolCNode",
                      hvac + u"_OAInlet Node", hvac + u"_OARelief Node", hvac + u" Supply Equipment Inlet Node"])
    zone_hvac.append([u"AirLoopHVAC:ZoneSplitter", hvac + u" Supply Air Splitter",
                      hvac + u" Zone Equipment Inlet Node", zone_name + u" Direct Air Inlet Node Name"])
    zone_hvac.append([u"AirLoopHVAC:SupplyPath", hvac, hvac + u" Zone Equipment Inlet Node",
                      u"AirLoopHVAC:ZoneSplitter", hvac + u" Supply Air Splitter"])
    zone_hvac.append([u"AirLoopHVAC:ZoneMixer", hvac + u" Return Air Mixer",
                      hvac + u" Zone Equipment Outlet Node", zone_name + u" Return Air Node Name"])
    zone_hvac.append([u"AirLoopHVAC:ReturnPath", hvac + u" Return Air Path",
                      hvac + u" Zone Equipment Outlet Node", u"AirLoopHVAC:ZoneMixer", hvac + u" Return Air Mixer"])
    zone_hvac.append([u"Branch", hvac + u" Air Loop Main Branch", u"autosize", u"",
                      u"AirLoopHVAC:OutdoorAirSystem", hvac + u"_OA",
                      hvac + u" Supply Equipment Inlet Node", hvac + u"_OA-" + hvac + u"_CoolCNode", u"Passive",
                      u"AirLoopHVAC:UnitaryCoolOnly", hvac + u"_CoolC", hvac + u"_OA-" + hvac + u"_CoolCNode",
                      hvac + u"_CoolC-" + hvac + u"_HeatCNode", u"Passive",
                      u"Coil:Heating:" + heating_coil_type, hvac + u"_HeatC", hvac + u"_CoolC-" + hvac + u"_HeatCNode",
                      hvac + u"_HeatC-" + hvac + u"_FanNode", u"Passive", u"Fan:ConstantVolume",
                      hvac + u"_Fan", hvac + u"_HeatC-" + hvac + u"_FanNode",
                      hvac + u" Supply Equipment Outlet Node", u"Active"])
    zone_hvac.append([u"OutdoorAir:Node", hvac + u"_CoolCOA Ref node"])
    zone_hvac.append([u"SetpointManager:MixedAir", hvac + u"_CoolC SAT Manager", u"Temperature",
                      hvac + u" Supply Equipment Outlet Node", hvac + u"_HeatC-" + hvac + u"_FanNode",
                      hvac + u" Supply Equipment Outlet Node", hvac + u"_CoolC-" + hvac + u"_HeatCNode"])
    zone_hvac.append([u"SetpointManager:MixedAir", hvac + u"_HeatC MixedAir Manager", u"Temperature",
                      hvac + u" Supply Equipment Outlet Node", hvac + u"_HeatC-" + hvac + u"_FanNode",
                      hvac + u" Supply Equipment Outlet Node", hvac + u"_HeatC-" + hvac + u"_FanNode"])
    zone_hvac.append([u"SetpointManager:MixedAir", hvac + u"_OAMixed Air Temp Manager", u"Temperature",
                      hvac + u" Supply Equipment Outlet Node", hvac + u"_HeatC-" + hvac + u"_FanNode",
                      hvac + u" Supply Equipment Outlet Node", hvac + u"_OA-" + hvac + u"_CoolCNode"])
    zone_hvac.append([u"NodeList", zone_name + u" Inlet Nodes", zone_name + u" Direct Air Inlet Node Name"])
    zone_hvac.append([u"NodeList", hvac + u"_OANode List", hvac + u"_OAInlet Node"])
    zone_hvac.append([u"SetpointManager:SingleZone:Reheat", u"SupAirTemp Mngr" + zone_name, u"Temperature", u"10.0",
                      u"50.0", zone_name + u"", zone_name + u" Air Node", zone_name + u" Direct Air Inlet Node Name",
                      hvac + u" Supply Equipment Outlet Node"])
    return zone_hvac


def _output_system_hvac_PSZ_ONOFF(zone_name, hvac, heating_coil_type, fan_efficiency, static_pressure, cooling_cop,
                                  heating_efficiency, has_economizer, economizer, use_mechanical_vent):
    zone_hvac = []
    # is similar but slightly different numbers... can change this...
    zone_hvac.append([u"Sizing:System", hvac, u"Sensible", u"AUTOSIZE", u"1.0", u"7.0", u"0.008", u"12.8000",
                      u"0.008", u"12.8000", u"40.0", u"NonCoincident", u"No", u"No", u"0.0085", u"0.0080",
                      u"DesignDay", u"", u"DesignDay", u"", u"" if use_mechanical_vent else u"ZoneSum"])
    zone_hvac.append([u"AirTerminal:SingleDuct:Uncontrolled", zone_name + u" Direct Air", u"ALWAYS_ON",
                      zone_name + u" Direct Air Inlet Node Name", u"autosize"])
    zone_hvac.append([u"ZoneHVAC:EquipmentList", zone_name + u" Equipment",
                      u"AirTerminal:SingleDuct:Uncontrolled", zone_name + u" Direct Air", u"1", u"1"])
    zone_hvac.append(
        [u"Fan:OnOff", hvac + u"_Fan", u"HVACOperationSchd", unicode(fan_efficiency), unicode(static_pressure),
         u"autosize", u"0.825", u"1.0", hvac + u"_OA-" + hvac + u"_FanNode",
         hvac + u"_FanNode-" + hvac + u"_CoolCNode", u"", u"", u"Fan Energy"])
    zone_hvac.append([u"Coil:Cooling:DX:SingleSpeed", hvac + u"_CoolC DXCoil", u"ALWAYS_ON", u"autosize", u"autosize",
                      unicode(cooling_cop), u"autosize", u"", hvac + u"_FanNode-" + hvac + u"_CoolCNode",
                      hvac + u"_CoolCNode-" + hvac + u"_HeatCNode", u"Cool-Cap-fT", u"ConstantCubic", u"Cool-EIR-fT",
                      u"ConstantCubic", u"Cool-PLF-fPLR"])
    zone_hvac.append([u"Coil:Heating:" + heating_coil_type, hvac + u"_HeatC", u"ALWAYS_ON",
                      unicode(heating_efficiency), u"autosize",
                      hvac + u"_CoolCNode-" + hvac + u"_HeatCNode",
                      hvac + u" Supply Equipment Outlet Node",
                      hvac + u" Supply Equipment Outlet Node"])
    zone_hvac.append([u"AirLoopHVAC:Unitary:Furnace:HeatCool", hvac + u"_HeatCoolC", u"ALWAYS_ON",
                      hvac + u"_OA-" + hvac + u"_FanNode", hvac + u" Supply Equipment Outlet Node",
                      u"ALWAYS_OFF", u"80", u"autosize", u"autosize", u"autosize", zone_name + u"",
                      u"Fan:OnOff", hvac + u"_Fan", u"BlowThrough", u"Coil:Heating:" + heating_coil_type,
                      hvac + u"_HeatC", u"Coil:Cooling:DX:SingleSpeed", hvac + u"_CoolC DXCoil", u"None"])
    # slightly different
    zone_hvac.append([u"Controller:OutdoorAir", hvac + u"_OA_Controller", hvac + u"_OARelief Node",
                      hvac + u" Supply Equipment Inlet Node", hvac + u"_OA-" + hvac + u"_FanNode",
                      hvac + u"_OAInlet Node", u"autosize", u"autosize",
                      economizer if has_economizer else u"NoEconomizer", u"ModulateFlow",
                      u"28.0", u"64000.0", u"", u"", u"-100.0", u"NoLockout", u"FixedMinimum",
                      u"MinOA_MotorizedDamper_Sched", u"", u"",
                      hvac + u" DCVObject" if use_mechanical_vent else u""])
    zone_hvac.append([u"OutdoorAir:Mixer", hvac + u"_OAMixing Box", hvac + u"_OA-" + hvac + u"_FanNode",
                      hvac + u"_OAInlet Node", hvac + u"_OARelief Node", hvac + u" Supply Equipment Inlet Node"])
    zone_hvac.append([u"AirLoopHVAC:ZoneSplitter", hvac + u" Supply Air Splitter",
                      hvac + u" Zone Equipment Inlet Node", zone_name + u" Direct Air Inlet Node Name"])
    zone_hvac.append([u"AirLoopHVAC:SupplyPath", hvac, hvac + u" Zone Equipment Inlet Node",
                      u"AirLoopHVAC:ZoneSplitter", hvac + u" Supply Air Splitter"])
    zone_hvac.append([u"AirLoopHVAC:ZoneMixer", hvac + u" Return Air Mixer",
                      hvac + u" Zone Equipment Outlet Node", zone_name + u" Return Air Node Name"])
    zone_hvac.append([u"AirLoopHVAC:ReturnPath", hvac + u" Return Air Path",
                      hvac + u" Zone Equipment Outlet Node", u"AirLoopHVAC:ZoneMixer", hvac + u" Return Air Mixer"])
    zone_hvac.append([u"Branch", hvac + u" Air Loop Main Branch", u"autosize", u"",
                      u"AirLoopHVAC:OutdoorAirSystem", hvac + u"_OA",
                      hvac + u" Supply Equipment Inlet Node", hvac + u"_OA-" + hvac + u"_FanNode", u"Passive",
                      u"AirLoopHVAC:Unitary:Furnace:HeatCool", hvac + u"_HeatCoolC",
                      hvac + u"_OA-" + hvac + u"_FanNode", hvac + u" Supply Equipment Outlet Node", u"Passive"])
    zone_hvac.append([u"NodeList", zone_name + u" Inlet Nodes", zone_name + u" Direct Air Inlet Node Name"])
    zone_hvac.append([u"NodeList", hvac + u"_OANode List", hvac + u"_OAInlet Node"])
    zone_hvac.append([u"OutdoorAir:Node", hvac + u"_FanOA Ref node"])
    zone_hvac.append([u"SetpointManager:SingleZone:Reheat", u"SupAirTemp Mngr" + zone_name, u"Temperature", u"10.0",
                      u"50.0", zone_name + u"", zone_name + u" Air Node", zone_name + u" Direct Air Inlet Node Name",
                      hvac + u" Supply Equipment Outlet Node"])
    zone_hvac.append([u"SetpointManager:MixedAir", hvac + u"_CoolC SAT Manager", u"Temperature",
                      hvac + u" Supply Equipment Outlet Node",
                      hvac + u"_OA-" + hvac + u"_FanNode",
                      hvac + u"_FanNode-" + hvac + u"_CoolCNode",
                      hvac + u"_CoolCNode-" + hvac + u"_HeatCNode"])
    zone_hvac.append([u"SetpointManager:MixedAir", hvac + u"_OAMixed Air Temp Manager", u"Temperature",
                      hvac + u" Supply Equipment Outlet Node",
                      hvac + u"_OA-" + hvac + u"_FanNode",
                      hvac + u"_FanNode-" + hvac + u"_CoolCNode",
                      hvac + u"_OA-" + hvac + u"_FanNode"])
    return zone_hvac


def _output_system_hvac_VAV(zones, hvac, heating_coil_type, fan_efficiency, static_pressure, cooling_cop,
                            heating_efficiency, has_economizer, economizer, use_mechanical_vent, plenum_name=None):
    system_hvac = []

    high_speed_cooling_cop = cooling_cop
    low_speed_cooling_cop = cooling_cop * 1.0148883374689821621905643734212

    system_hvac.append([u"Sizing:System", hvac, u"Sensible", u"autosize", u"0.3", u"7.0", u"0.008", u"12.8000",
                        u"0.008", u"12.8000", u"16.7000", u"NonCoincident", u"No", u"No", u"0.0085", u"0.0080",
                        u"DesignDay", u"0.0", u"DesignDay", u"0.0", u"" if use_mechanical_vent else u"ZoneSum"])
    system_hvac.append([u"Fan:VariableVolume", hvac + u"_Fan", u"HVACOperationSchd",
                        unicode(fan_efficiency), unicode(static_pressure), u"autosize", u"FixedFlowRate", u"",
                        u"0.0000",
                        u"0.91", u"1.0", u"0.0407598940", u"0.08804497", u"-0.072926120", u"0.9437398230", u"0",
                        hvac + u"_HeatC-" + hvac + u"_FanNode",
                        hvac + u" Supply Equipment Outlet Node", u"Fan Energy"])
    system_hvac.append([u"Coil:Cooling:DX:TwoSpeed", hvac + u"_CoolC DXCoil", u"ALWAYS_ON",
                        u"autosize", u"autosize", unicode(high_speed_cooling_cop), u"autosize",
                        hvac + u"_OA-" + hvac + u"_CoolCNode",
                        hvac + u"_CoolC-" + hvac + u"_HeatCNode",
                        u"Measured_CoolCStandard10Ton_CapFT", u"Measured_CoolCStandard10Ton_CapFF",
                        u"Measured_CoolCStandard10Ton_EIRFT", u"Measured_CoolCStandard10Ton_EIRFFF",
                        u"No_PLR_Degredation", u"autosize", u"autosize", unicode(low_speed_cooling_cop),
                        u"autosize", u"Measured_LowSpeedCoolCapLSFT", u"Measured_LowSpeedCoolEIRLSFT"])
    system_hvac.append([u"Coil:Heating:" + heating_coil_type, hvac + u"_HeatC", u"ALWAYS_ON",
                        unicode(heating_efficiency), u"autosize",
                        hvac + u"_CoolC-" + hvac + u"_HeatCNode",
                        hvac + u"_HeatC-" + hvac + u"_FanNode",
                        hvac + u"_HeatC-" + hvac + u"_FanNode"])
    system_hvac.append([u"AirLoopHVAC:UnitaryCoolOnly", hvac + u"_CoolC",
                        u"ALWAYS_ON", hvac + u"_OA-" + hvac + u"_CoolCNode",
                        hvac + u"_CoolC-" + hvac + u"_HeatCNode",
                        hvac + u"_CoolC-" + hvac + u"_HeatCNode",
                        u"Coil:Cooling:DX:TwoSpeed", hvac + u"_CoolC DXCoil"])
    system_hvac.append([u"Controller:OutdoorAir", hvac + u"_OA_Controller",
                        hvac + u"_OARelief Node",
                        hvac + u" Supply Equipment Inlet Node",
                        hvac + u"_OA-" + hvac + u"_CoolCNode",
                        hvac + u"_OAInlet Node", u"autosize", u"autosize",
                        economizer if has_economizer else u"NoEconomizer", u"ModulateFlow", u"28.0", u"64000.0", u"",
                        u"", u"-100.0", u"NoLockout", u"FixedMinimum", u"MinOA_MotorizedDamper_Sched", u"", u"",
                        hvac + u" DCVObject" if use_mechanical_vent else u""])
    system_hvac.append([u"OutdoorAir:Mixer", hvac + u"_OAMixing Box",
                        hvac + u"_OA-" + hvac + u"_CoolCNode",
                        hvac + u"_OAInlet Node", hvac + u"_OARelief Node",
                        hvac + u" Supply Equipment Inlet Node"])
    splitters = [u"AirLoopHVAC:ZoneSplitter", hvac + u" Supply Air Splitter", hvac + u" Zone Equipment Inlet Node"]
    splitters.extend(_zone_splitter(zones))
    system_hvac.append(splitters)

    if not plenum_name is None:
        system_hvac.append([u"AirLoopHVAC:ZoneMixer", hvac + u" " + plenum_name + u" Return Air Mixer",
                            hvac + u" Zone Equipment Outlet Node", plenum_name + u"_OutletNode"])
        return_plenum = [u"AirLoopHVAC:ReturnPlenum", hvac + u" " + plenum_name + u" Return Plenum",
                         plenum_name, plenum_name + u"_Node", plenum_name + u"_OutletNode"]
        return_plenum.extend(_return_air_nodes(zones))
        system_hvac.append(return_plenum)
        system_hvac.append([u"AirLoopHVAC:ReturnPath", hvac + u" Return Air Path",
                            hvac + u" Zone Equipment Outlet Node", u"AirLoopHVAC:ReturnPlenum",
                            hvac + u" " + plenum_name + u" Return Plenum", u"AirLoopHVAC:ZoneMixer",
                            hvac + u" " + plenum_name + u" Return Air Mixer"])
    else:
        system_hvac.append([u"AirLoopHVAC:ReturnPath", hvac + u" Return Air Path",
                            hvac + u" Zone Equipment Outlet Node", u"AirLoopHVAC:ZoneMixer",
                            hvac + u" Return Air Mixer"])
        return_air = [u"AirLoopHVAC:ZoneMixer", hvac + u" Return Air Mixer",
                      hvac + u" Zone Equipment Outlet Node"]
        return_air.extend(_return_air_nodes(zones))
        system_hvac.append(return_air)

    system_hvac.append([u"NodeList", hvac + u"_OANode List",
                        hvac + u"_OAInlet Node"])
    system_hvac.append([u"AirLoopHVAC:SupplyPath", hvac + u"",
                        hvac + u" Zone Equipment Inlet Node", u"AirLoopHVAC:ZoneSplitter",
                        hvac + u" Supply Air Splitter"])
    system_hvac.append([u"Branch", hvac + u" Air Loop Main Branch", u"autosize", u"",
                        u"AirLoopHVAC:OutdoorAirSystem", hvac + u"_OA",
                        hvac + u" Supply Equipment Inlet Node",
                        hvac + u"_OA-" + hvac + u"_CoolCNode", u"Passive",
                        u"AirLoopHVAC:UnitaryCoolOnly", hvac + u"_CoolC",
                        hvac + u"_OA-" + hvac + u"_CoolCNode",
                        hvac + u"_CoolC-" + hvac + u"_HeatCNode", u"Passive",
                        u"Coil:Heating:" + heating_coil_type, hvac + u"_HeatC",
                        hvac + u"_CoolC-" + hvac + u"_HeatCNode",
                        hvac + u"_HeatC-" + hvac + u"_FanNode", u"Passive",
                        u"Fan:VariableVolume", hvac + u"_Fan",
                        hvac + u"_HeatC-" + hvac + u"_FanNode",
                        hvac + u" Supply Equipment Outlet Node", u"Active"])
    system_hvac.append([u"OutdoorAir:Node", hvac + u"_CoolC Cond OA node"])
    system_hvac.append([u"OutdoorAir:Node", hvac + u"_CoolCOA Ref node"])
    system_hvac.append([u"SetpointManager:Scheduled", hvac + u" SAT setpoint",
                        u"Temperature", u"Seasonal-Reset-Supply-Air-Temp-Sch",
                        hvac + u" Supply Equipment Outlet Node"])
    system_hvac.append([u"SetpointManager:MixedAir", hvac + u"_CoolC SAT Manager", u"Temperature",
                        hvac + u" Supply Equipment Outlet Node",
                        hvac + u"_HeatC-" + hvac + u"_FanNode",
                        hvac + u" Supply Equipment Outlet Node",
                        hvac + u"_CoolC-" + hvac + u"_HeatCNode"])
    system_hvac.append([u"SetpointManager:MixedAir", hvac + u"_HeatC MixedAir Manager", u"Temperature",
                        hvac + u" Supply Equipment Outlet Node",
                        hvac + u"_HeatC-" + hvac + u"_FanNode",
                        hvac + u" Supply Equipment Outlet Node",
                        hvac + u"_HeatC-" + hvac + u"_FanNode"])
    system_hvac.append([u"SetpointManager:MixedAir", hvac + u"_OAMixed Air Temp Manager", u"Temperature",
                        hvac + u" Supply Equipment Outlet Node",
                        hvac + u"_HeatC-" + hvac + u"_FanNode",
                        hvac + u" Supply Equipment Outlet Node",
                        hvac + u"_OA-" + hvac + u"_CoolCNode"])
    return system_hvac


def _vav_performance_curves():
    perf_curve = [
        [u"Curve:Quadratic", u"Measured_CoolCStandard10Ton_CapFF", u"0.7685", u"0.2315", u"0", u"0.776", u"1.197"],
        [u"Curve:Quadratic", u"Measured_CoolCStandard10Ton_EIRFFF", u"1.192", u"-0.1917", u"0", u"0.776", u"1.197"],
        [u"Curve:Quadratic", u"No_PLR_Degredation", u"1.0", u"0", u"0", u"0.0", u"1.0"],
        [u"Curve:Biquadratic", u"Measured_LowSpeedCoolCapLSFT", u"0.4136", u"0.03105", u"0", u"0.006952",
         u"-0.00021280", u"0", u"11.1", u"29.4", u"10.0", u"50.3"],
        [u"Curve:Biquadratic", u"Measured_CoolCStandard10Ton_CapFT", u"0.52357", u"0.03478", u"0", u"-0.001915",
         u"-0.00010838", u"0", u"11.1", u"29.4", u"10.0", u"50.3"],
        [u"Curve:Biquadratic", u"Measured_LowSpeedCoolEIRLSFT", u"1.1389", u"-0.04518", u"0.0014298", u"0.006044",
         u"0.0006745", u"-0.0012325", u"11.1", u"29.4", u"10.0", u"50.3"],
        [u"Curve:Biquadratic", u"Measured_CoolCStandard10Ton_EIRFT", u"0.9847", u"-0.04285", u"0.0013562",
         u"0.009934", u"0.0006398", u"-0.0011690", u"11.1", u"29.4", u"10.0", u"50.3"]]
    return perf_curve


def _psz_performance_curves():
    perf_curve = [
        [u"Curve:Quadratic", u"Cool-PLF-fPLR", u"0.90949556", u"0.09864773", u"-0.00819488", u"0", u"1", u"0.7",
         u"1"], [u"Curve:Cubic", u"ConstantCubic", u"1", u"0", u"0", u"0", u"-100", u"100"],
        [u"Curve:Biquadratic", u"Cool-Cap-fT", u"0.9712123", u"-0.015275502", u"0.0014434524", u"-0.00039321",
         u"-0.0000068364", u"-0.0002905956", u"-100", u"100", u"-100", u"100"],
        [u"Curve:Biquadratic", u"Cool-EIR-fT", u"0.28687133", u"0.023902164", u"-0.000810648", u"0.013458546",
         u"0.0003389364", u"-0.0004870044", u"-100", u"100", u"-100", u"100"]]
    return perf_curve