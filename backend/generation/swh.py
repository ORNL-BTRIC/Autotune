__author__ = 'm5z'


def _zone_load(zone_name, branch_num):
    load = []

    zone_water_flow_rate = 1.04e-005

    load.append([u"Branch", _demand_load_branches(branch_num), u"", u"", u"WaterUse:Connections",
                 zone_name + u" Water Equipment", zone_name + u" Water Equipment Water Inlet Node",
                 zone_name + u" Water Equipment Water Outlet Node", u"Active"])
    load.append([u"WaterUse:Equipment", zone_name + u" Water Equipment", u"", unicode(zone_water_flow_rate),
                 u"BLDG_SWH_SCH", u"Water Equipment Temp Sched", u"Water Equipment Hot Supply Temp Sched",
                 u"", zone_name, u"Water Equipment Sensible fract sched", u"Water Equipment Latent fract sched"])
    load.append([u"WaterUse:Connections", zone_name + u" Water Equipment",
                 zone_name + u" Water Equipment Water Inlet Node",
                 zone_name + u" Water Equipment Water Outlet Node", u"", u"", u"", u"", u"", u"", u"",
                 zone_name + u" Water Equipment"])
    return load


def _demand_load_branches(branch_num):
    return u"SWHSys1 Demand Load Branch " + unicode(branch_num)


def _zone_swh(floors):
    branches = []

    demand_branches = [_demand_load_branches(branch_num) for branch_num in floors.keys()]

    branch_list = [u"BranchList", u"SWHSys1 Demand Branches", u"SWHSys1 Demand Inlet Branch"]
    branch_list.extend(demand_branches)
    branch_list.extend([u"SWHSys1 Demand Bypass Branch", u"SWHSys1 Demand Outlet Branch"])

    connector_splitter = [u"Connector:Splitter", u"SWHSys1 Demand Splitter", u"SWHSys1 Demand Inlet Branch"]
    connector_splitter.extend(demand_branches)
    connector_splitter.extend([u"SWHSys1 Demand Bypass Branch"])

    connector_mixer = [u"Connector:Mixer", u"SWHSys1 Demand Mixer", u"SWHSys1 Demand Outlet Branch"]
    connector_mixer.extend(demand_branches)
    connector_mixer.extend([u"SWHSys1 Demand Bypass Branch"])

    branches.append(branch_list)
    branches.append(connector_splitter)
    branches.append(connector_mixer)

    floor_has_interior_zone = False
    for floor in floors.keys():
        branch_num = floor
        for zone in floors[floor]:
            if not zone.zone_info['is_plenum'] and zone.zone_info['is_interior_zone']:
                branches.extend(_zone_load(zone.zone_name(), branch_num))
                floor_has_interior_zone = True
        if not floor_has_interior_zone:
            for zone in floors[floor]:
                if not zone.zone_info['is_plenum']:
                    branches.extend(_zone_load(zone.zone_name(), branch_num))
                    break

    return branches


def swh_system(floors, idf_generation_inputs):
    swh = [[u"Sizing:Plant", u"SWHSys1", u"Heating", u"60", u"5.0"],
           [u"Branch", u"SWHSys1 Demand Bypass Branch", u"", u"", u"Pipe:Adiabatic", u"SWHSys1 Demand Bypass Pipe",
            u"SWHSys1 Demand Bypass Pipe Inlet Node", u"SWHSys1 Demand Bypass Pipe Outlet Node", u"Bypass"],
           [u"Branch", u"SWHSys1 Demand Inlet Branch", u"", u"", u"Pipe:Adiabatic", u"SWHSys1 Demand Inlet Pipe",
            u"SWHSys1 Demand Inlet Node", u"SWHSys1 Demand Inlet Pipe-SWHSys1 Demand Mixer", u"Passive"],
           [u"Branch", u"SWHSys1 Demand Outlet Branch", u"", u"", u"Pipe:Adiabatic", u"SWHSys1 Demand Outlet Pipe",
            u"SWHSys1 Demand Mixer-SWHSys1 Demand Outlet Pipe", u"SWHSys1 Demand Outlet Node", u"Passive"],
           [u"Branch", u"SWHSys1 Supply Equipment Branch", u"", u"", u"WaterHeater:Mixed", u"SWHSys1 Water Heater",
            u"SWHSys1 Pump-SWHSys1 Water HeaterNode", u"SWHSys1 Supply Equipment Outlet Node", u"Active"],
           [u"Branch", u"SWHSys1 Supply Equipment Bypass Branch", u"", u"", u"Pipe:Adiabatic",
            u"SWHSys1 Supply Equipment Bypass Pipe", u"SWHSys1 Supply Equip Bypass Inlet Node",
            u"SWHSys1 Supply Equip Bypass Outlet Node", u"Bypass"],
           [u"Branch", u"SWHSys1 Supply Inlet Branch", u"", u"", u"Pump:ConstantSpeed", u"SWHSys1 Pump",
            u"SWHSys1 Supply Inlet Node", u"SWHSys1 Pump-SWHSys1 Water HeaterNode via Connector", u"Active"],
           [u"Branch", u"SWHSys1 Supply Outlet Branch", u"", u"", u"Pipe:Adiabatic", u"SWHSys1 Supply Outlet Pipe",
            u"SWHSys1 Supply Mixer-SWHSys1 Supply Outlet Pipe", u"SWHSys1 Supply Outlet Node", u"Passive"],
           [u"BranchList", u"SWHSys1 Supply Branches", u"SWHSys1 Supply Inlet Branch",
            u"SWHSys1 Supply Equipment Branch",
            u"SWHSys1 Supply Equipment Bypass Branch", u"SWHSys1 Supply Outlet Branch"],
           [u"Connector:Splitter", u"SWHSys1 Supply Splitter", u"SWHSys1 Supply Inlet Branch",
            u"SWHSys1 Supply Equipment Branch", u"SWHSys1 Supply Equipment Bypass Branch"],
           [u"Connector:Mixer", u"SWHSys1 Supply Mixer", u"SWHSys1 Supply Outlet Branch",
            u"SWHSys1 Supply Equipment Branch", u"SWHSys1 Supply Equipment Bypass Branch"],
           [u"ConnectorList", u"SWHSys1 Demand Connectors", u"Connector:Splitter", u"SWHSys1 Demand Splitter",
            u"Connector:Mixer", u"SWHSys1 Demand Mixer"],
           [u"ConnectorList", u"SWHSys1 Supply Connectors", u"Connector:Splitter", u"SWHSys1 Supply Splitter",
            u"Connector:Mixer", u"SWHSys1 Supply Mixer"],
           [u"Pipe:Adiabatic", u"SWHSys1 Demand Bypass Pipe", u"SWHSys1 Demand Bypass Pipe Inlet Node",
            u"SWHSys1 Demand Bypass Pipe Outlet Node"],
           [u"Pipe:Adiabatic", u"SWHSys1 Demand Inlet Pipe", u"SWHSys1 Demand Inlet Node",
            u"SWHSys1 Demand Inlet Pipe-SWHSys1 Demand Mixer"],
           [u"Pipe:Adiabatic", u"SWHSys1 Demand Outlet Pipe", u"SWHSys1 Demand Mixer-SWHSys1 Demand Outlet Pipe",
            u"SWHSys1 Demand Outlet Node"],
           [u"Pipe:Adiabatic", u"SWHSys1 Supply Equipment Bypass Pipe", u"SWHSys1 Supply Equip Bypass Inlet Node",
            u"SWHSys1 Supply Equip Bypass Outlet Node"],
           [u"Pipe:Adiabatic", u"SWHSys1 Supply Outlet Pipe", u"SWHSys1 Supply Mixer-SWHSys1 Supply Outlet Pipe",
            u"SWHSys1 Supply Outlet Node"],
           [u"Pump:ConstantSpeed", u"SWHSys1 Pump", u"SWHSys1 Supply Inlet Node",
            u"SWHSys1 Pump-SWHSys1 Water HeaterNode via Connector", u"autosize", u"179352", u"autosize", u"0.85",
            u"0.0", u"Intermittent"],
           [u"WaterHeater:Mixed", u"SWHSys1 Water Heater", u"0.3785",
            u"SWHSys1 Water Heater Setpoint Temperature Schedule Name", u"2.0", u"82.2222", u"Cycle", u"845000",
            u"", u"", u"", u"NATURALGAS", unicode(idf_generation_inputs['dhw_efficiency']), u"", u"20", u"NATURALGAS",
            u"0.8", u"", u"NATURALGAS", u"", u"SCHEDULE", u"SWHSys1 Water Heater Ambient Temperature Schedule Name",
            u"", u"", u"6.0", u"", u"6.0", u"", u"", u"", u"", u"SWHSys1 Pump-SWHSys1 Water HeaterNode",
            u"SWHSys1 Supply Equipment Outlet Node", u"1.0", u"", u"", u"1.0", u"autosize", u"autosize", u"1.5"],
           [u"PlantLoop", u"SWHSys1", u"Water", u"", u"SWHSys1 Loop Operation Scheme List",
            u"SWHSys1 Supply Outlet Node", u"60.0", u"10.0", u"autosize", u"0.0", u"autosize",
            u"SWHSys1 Supply Inlet Node", u"SWHSys1 Supply Outlet Node", u"SWHSys1 Supply Branches",
            u"SWHSys1 Supply Connectors", u"SWHSys1 Demand Inlet Node", u"SWHSys1 Demand Outlet Node",
            u"SWHSys1 Demand Branches", u"SWHSys1 Demand Connectors", u"Optimal"],
           [u"PlantEquipmentList", u"SWHSys1 Equipment List", u"WaterHeater:Mixed", u"SWHSys1 Water Heater"],
           [u"PlantEquipmentOperation:HeatingLoad", u"SWHSys1 Operation Scheme", u"0.0", u"1000000000000000",
            u"SWHSys1 Equipment List"],
           [u"PlantEquipmentOperationSchemes", u"SWHSys1 Loop Operation Scheme List",
            u"PlantEquipmentOperation:HeatingLoad", u"SWHSys1 Operation Scheme", u"ALWAYS_ON"],
           [u"SetpointManager:Scheduled", u"SWHSys1 Loop Setpoint Manager", u"Temperature",
            u"SWHSys1-Loop-Temp-Schedule",
            u"SWHSys1 Supply Outlet Node"]]

    swh.extend(_zone_swh(floors))

    return swh