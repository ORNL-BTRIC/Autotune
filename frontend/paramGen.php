<?php
	/*
		Creates a parameter file. Calls a python script that uses the parameter file and creates an idf file.
		Required:	city
					state
					climateZone
					
		- Run python script and recieve the contents of the idf file from the result of the exec command. Use the contents to create a new job in Autotune
	*/

	
	function generateModel($city, $state, $climateZone, $additionalOptions) { //additonalOptions is an associative array with specified options
																			// ex. 'floor_height' => 5.675
		
	
		$defaultContents =	"{\"timestep\": 1, \"run_number\": 1, \"climate_zone\": \"$climateZone\", \"state\": \"$state\", \"city\": \"$city\", \"number_of_floors\": 3, \"floor_height\": 3.9624, \"plenums\": true, \"orientation\": 0.0, \"building_type\": \"medium_office\", \"geometry_configuration\": \"Rectangle\", \"zone_layout\": \"Five_Zone\", \"roof_style\": \"flat\", \"wall_type\": \"Steel_Frame_Non_Res\", \"roof_type\": \"iead_non_res\", \"south_wwr\": 0.477, \"east_wwr\": 0.477, \"north_wwr\": 0.477, \"west_wwr\": 0.477, \"south_win_type\": \"reference\", \"east_win_type\": \"reference\", \"north_win_type\": \"reference\", \"west_win_type\": \"reference\", \"hvac_type\": \"vav\", \"heating_coil\": \"Gas\", \"has_reheat\": true, \"reheat_coil\": \"Electric\", \"heating_efficiency\": 0.8, \"cooling_cop\": 3.23372055845678, \"fan_efficiency\": 0.5915, \"fan_static_pressure\": 1109.648, \"elec_plug_intensity\": 10.76, \"int_lighting_intensity\": 10.76, \"ext_lighting_intensity\": 14804, \"people_density\": 18.58, \"infiltration_per_ext_sur_area\": 0.000302, \"oa_vent_per_person\": 0.0125, \"oa_vent_per_area\": 0.0, \"length1\": 49.911, \"length2\": 0.0, \"width1\": 33.2738, \"width2\": 0.0, \"end1\": 0.0, \"end2\": 0.0, \"offset1\": 0.0, \"offset2\": 0.0, \"offset3\": 0.0, \"has_setback\": true, \"has_night_cycle\": true, \"night_cycle\": \"CycleOnAny\", \"has_dcv\": false, \"cooling_setback\": 26.7, \"heating_setback\": 15.6, \"cooling_setpoint\": 24.0, \"heating_setpoint\": 21.0, \"has_weekend_occupancy\": true, \"weekend_occupancy_type\": \"Saturday\", \"weekday_start_time\": \"06:00\", \"weekday_end_time\": \"22:00\", \"weekend_start_time\": \"06:00\", \"weekend_end_time\": \"18:00\", \"use_mechanical_vent\": false}";
		
		$contents = modify($defaultContents, $additionalOptions); 
		$contents = str_replace('"', "'", $contents); // replace double quotes with single quotes
		
		$generator = "/yourserverpath/autotune/web/backend/idfgenerator.py"; //on the server
		//$generator = "C:/xampp/htdocs/Git/backend/idfgenerator.py"; //testing locally
		
		$command = "$generator \"$contents\"";
		//call python script
		$modelContents = array();

		exec($command, $modelContents);
		$strContents = implode("\n", $modelContents); //make array into a string
		return $strContents;
	}
	
	
	function modify($jsonString, $arrayModifier) { //the keys in the arrayModifier must match the elements in the json string
													//modify requires a json string --> use of double quotes
		if(count($arrayModifier) > 0) {
			$obj = json_decode($jsonString);
			foreach($arrayModifier as $key=>$value) {
				$obj->$key = $value;
			}		
			$newString = json_encode($obj);
			return $newString;
		}
		else return $jsonString;
	}
?>
