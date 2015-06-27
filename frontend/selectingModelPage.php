<!DOCTYPE html>

<html>
	<head>
		<title> Selecting Base Model Page</title>
		
		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, minimum-scale=1" />
		
		<link type="text/css" rel="stylesheet" href="stylePractice2.css" /> 
		
		<link href="css/custom-theme/jquery-ui-1.10.2.custom.css" rel="stylesheet">  
		<link type="text/css" rel="stylesheet" href="mobile.css" />
		<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
		<link rel="stylesheet" type="text/css" href="js/jquery.jWizard.css" /> 
		<script type="text/javascript" src="js/jquery.jWizard.js"></script>  
		<script src="jquery/JQCode.js"></script>
		
		<script
			src="http://maps.googleapis.com/maps/api/js?key=ENTER_YOUR_KEY_HERE">
		</script>
		
		<!--<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/themes/base/jquery-ui.css" rel="stylesheet" type="text/css" />-->
		<!--<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery-ui.min.js"></script>-->
		<!--<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js"></script-->

		<script type="text/javascript"> <!--there-->
		$(document).ready(function() {
			$("#jWizard").jWizard({
				counter: {
					enable: true,
					type: "percentage",	// Default: "count"
					progressbar: true,	// Default: false
					
					startCount: true,		// Default: true
					startHide: true,		// Default: false
					finishCount: false,	// Default: true
					finishHide: false,	// Default: false
					appendText: "Done",	// Default: "Complete"
					orientText: "right"	// Default: "left" ("center" is also valid)
				}
			});
		});
		
		function validateMonthlyInput(array) {
			var errors = 0;
			for(var count = 0; count < 12; count++) {
				errors = validate(array[count], array[count].val(), "number", 0, "", errors, true);
			}
			return errors;
		}
		
		function validate(inputfield, value, type, min, max, errorcount, required) {
			var errors = errorcount;
			if(required == true && value == "") { 
				$(inputfield).before('<span class="important reminder">*   </span>');
				errors = errors + 1;
				return errors;
			}
			else if(required == false && value == "") {
				return errors;
			}
			else if(type == "number") { 
				if(isNaN(parseInt(value))) {
					$(inputfield).before('<span class="important reminder">*   </span>');
					errors = errors + 1;
					return errors;
				}
				else if((min == 0) && (value.lastIndexOf("-") != -1)) {
					$(inputfield).before('<span class="important reminder">*   </span>');
					errors++;
					return errors;
				}
				else if((min != "") && (min > value)) {
					$(inputfield).before('<span class="important reminder">*   </span>');
					errors++;
					return errors;
				}
				else if((max != "") &&  (max < value)) {
					$(inputfield).before('<span class="important reminder">*   </span>');
					errors++;
					return errors;
				}
				else { 
					return errors; 
				}
			}
			else { 
				return errors; 
			}
		}
		
		function checkForBlanks(array) {
			for(var count = 0; count < 12; count++) {
				if(array[count].val() == "") { return true; }
			}
			
			return false;
		}
		
		</script>
		<style>
			input {
				text-align:right;
			}
		</style>
	</head>
	
	<body>
		
		<div id="logo">
			<a href="home.html"><img src="pictures/Logo.png"/></a>
			
		</div>
		<div class="inside">
			<div id="jWizardWrapper">
				<form id="jWizard" enctype="multipart/form-data" action="tune.php" method="POST">	
				
					<?php 
					$advancedMode = isset($_REQUEST['advanced'])&& $_REQUEST['advanced'];
					if($advancedMode): ?>	
						<input type="hidden" name="advanced" value="true">
					<?php else: ?>
						<input type="hidden" name="advanced" value="false">
					<?php endif; ?>
					
					<fieldset><legend>Selecting the Base Model</legend>
						<!--<form action="modelSelection.php" method="post">-->
							<section id="homeSelect">
								<p class="instruct">
									Please select the model which most closely represents your home.
								</p>
								
								
								<div class="sizeSelect">
									<div class="imageWrap">
										<div class="image home"><img src="pictures/transparent.png" alt="home"></div>
										<p>Residential</p>
									</div>
									
									<div class="imageWrap">
										<div class="image business"><img class="current" src="pictures/transparent.png" alt="business"></div>
										<p>Commercial</p>
									</div>
									
								</div> <!-- end of image selection  -->
								
							</section>
					</fieldset>
					<fieldset><legend>Selecting the Base Model</legend>
						<table id="step2">
							<tr>
								<td><label>Please select the building type:</label></td>
								<td><select name="idf[building_type]">
									<!--<option value="small_office" class="home business">Small Office</option>-->
									<option value="medium_office" class="home business">Medium Office</option>
									<!--<option value="apartment" class="home">Apartment</option>
									<option value="fullServiceRestaurant" class="business">Full Service Restaurant</option>
									<option value="hospital" class="business">Hospital</option>
									<option value="largeHotel" class="business">Large Hotel</option>
									<option value="largeOffice" class="business">Large Office</option>
									<option value="outPatient" class="business">Out Patient</option>
									<option value="primarySchool" class="business">Primary School</option>
									<option value="quickServiceRestaurant" class="business">Quick Service Restaurant</option>
									<option value="secondarySchool" class="business">Secondary School</option>
									<option value="smallHotel" class="business">Small Hotel</option>
									<option value="standAloneRetail" class="home business">Stand-alone Retail</option>
									<option value="stripMall" class="business">Strip Mall</option>
									<option value="superMarket" class="business">Super Market</option>
									<option value="warehouse" class="business">Warehouse</option>-->
								</select></td>
							</tr>
							
							<tr>
								<td><label>Please Input Number of Floors:</label></td> <td>
								<input type="number" name="idf[number_of_floors]" size="3" value="1"></td>
							</tr>
							
							<tr>
								<td><label>Please input the building's square footage:</label></td> <td>
								<input type="number" name="size" size="5">sqft</td>
							</tr>
							
							<tr>
								<td><label>Please select the building's condition:</label></td>
								<td><select name="idf[building_age]">
									<!--<option value="1970" selected>Old</option>-->
									<option value="1990">Recent</option>
									<option value="2005">New</option>
								</select></td>
							</tr>
							
							
					<?php 
					$advancedMode = isset($_REQUEST['advanced'])&& $_REQUEST['advanced'];
					if($advancedMode): ?>	
							<tr>
								<td><label>Please input the length and width of the building: <i>(optional)</i></label></td>
								<td>
								
								<input type="text" placeholder="Width" name="idf[width1]">ft<br>
								
								<input type="text" placeholder="Length" name="idf[length1]">ft</td>
							</tr>
					<?php endif; ?>		
							
						</table>
					</fieldset>
					
					<?php if($advancedMode): ?>	
					<!--
						<fieldset><legend>Selecting Schedule</legend>
				
						<div id="dialog-option" title="Edit Selection">
							<h4 id="selection"></h4>
							<p>Change room to</p>
							<select name="EditRooms">
								<option value="bedroom" selected>Bedroom</option>
								<option value="kitchen">Kitchen</option>
								<option value="bathroom">Bathroom</option>
								<option value="diningRoom">Dining Room</option>
								<option value="livingRoom">Living Room</option>
							</select>
							
							
						</div> <!-- end of dialog form -->
					<!--	
						<div id="dialog-form" title="Room Selection">
							<h5 id="timeRange"></h5>
							<select name="Rooms">
								<option value="bedroom" selected>Bedroom</option>
								<option value="kitchen">Kitchen</option>
								<option value="bathroom">Bathroom</option>
								<option value="diningRoom">Dining Room</option>
								<option value="livingRoom">Living Room</option>
							</select>
							
						</div> <!-- end of dialog form -->
						
						
						<!-- Ask for number of residents -->
					<!--	<label>What is the maximum number of people that are in the building at one time?</label>

						<input type="text" size="4" name="numRes" value="0">
						
						<div id="inputInsert">
							<p class="instruct"> 
								Please provide the first name of each person. (This is only used to help with the scheduling process)
							</p>
						</div>
						
						<br/><p id="createSchedules" class="button left">Click to Create Schedule</p>
						<br>
						<br>
						<br>				
						
						<!-- Time selection -->
					<!--
						<div id="tabs">
							<ul>
								<!-- jQuery puts tab names here -->
					<!--		</ul>
							<div id="tab">
								
								
								<h3>Format:</h3>
								
								<input type="radio" name="numCols" value="2" checked>Weekday/Weekend<br>
								
								<input type="radio" name="numCols" value="7" >Specify each day<br>
								<div class="scheduleContainer">
									<table>
										<thead>
											<tr>
												<!-- JQuery puts headers here -->
					<!--						</tr>
										</thead>
										<tbody>
											<tr><th>12AM</th></tr>
											<tr><th>12:15</th></tr>
											<tr><th>12:30</th></tr>
											<tr><th>12:45</th></tr>
											<tr><th>1AM</th></tr>
											<tr><th>1:15</th></tr>
											<tr><th>1:30</th></tr>
											<tr><th>1:45</th></tr>
											<tr><th>2AM</th></tr>
											<tr><th>2:15</th></tr>
											<tr><th>2:30</th></tr>
											<tr><th>2:45</th></tr>
											<tr><th>3AM</th></tr>
											<tr><th>3:15</th></tr>
											<tr><th>3:30</th></tr>
											<tr><th>3:45</th></tr>
											<tr><th>4AM</th></tr>
											<tr><th>4:15</th></tr>
											<tr><th>4:30</th></tr>
											<tr><th>4:45</th></tr>
											<tr><th>5AM</th></tr>
											<tr><th>5:15</th></tr>
											<tr><th>5:30</th></tr>
											<tr><th>5:45</th></tr>
											<tr><th>6AM</th></tr>
											<tr><th>6:15</th></tr>
											<tr><th>6:30</th></tr>
											<tr><th>6:45</th></tr>
											<tr><th>7AM</th></tr>   
											<tr><th>7:15</th></tr>  
											<tr><th>7:30</th></tr>      	
											<tr><th>7:45</th></tr>      	
											<tr><th>8AM</th></tr>      
											<tr><th>8:15</th></tr>      	
											<tr><th>8:30</th></tr>      	
											<tr><th>8:45</th></tr>     
											<tr><th>9AM</th></tr>      
											<tr><th>9:15</th></tr>     
											<tr><th>9:30</th></tr>     
											<tr><th>9:45</th></tr>      
											<tr><th>10AM</th></tr>      
											<tr><th>10:15</th></tr>      	
											<tr><th>10:30</th></tr>   
											<tr><th>10:45</th></tr>     
											<tr><th>11AM</th></tr>      
											<tr><th>11:15</th></tr>      		
											<tr><th>11:30</th></tr>      			
											<tr><th>11:45</th></tr>     
											
											<tr><th>12PM</th></tr>
											<tr><th>12:15</th></tr>
											<tr><th>12:30</th></tr>
											<tr><th>12:45</th></tr>
											<tr><th>1PM</th></tr>
											<tr><th>1:15</th></tr>
											<tr><th>1:30</th></tr>
											<tr><th>1:45</th></tr>
											<tr><th>2PM</th></tr>
											<tr><th>2:15</th></tr>
											<tr><th>2:30</th></tr>
											<tr><th>2:45</th></tr>
											<tr><th>3PM</th></tr>
											<tr><th>3:15</th></tr>
											<tr><th>3:30</th></tr>
											<tr><th>3:45</th></tr>
											<tr><th>4PM</th></tr>
											<tr><th>4:15</th></tr>
											<tr><th>4:30</th></tr>
											<tr><th>4:45</th></tr>
											<tr><th>5PM</th></tr>
											<tr><th>5:15</th></tr>
											<tr><th>5:30</th></tr>
											<tr><th>5:45</th></tr>
											<tr><th>6PM</th></tr>
											<tr><th>6:15</th></tr>
											<tr><th>6:30</th></tr>
											<tr><th>6:45</th></tr>
											<tr><th>7PM</th></tr>   
											<tr><th>7:15</th></tr>  
											<tr><th>7:30</th></tr>      	
											<tr><th>7:45</th></tr>      	
											<tr><th>8PM</th></tr>      
											<tr><th>8:15</th></tr>      	
											<tr><th>8:30</th></tr>      	
											<tr><th>8:45</th></tr>     
											<tr><th>9PM</th></tr>      
											<tr><th>9:15</th></tr>     
											<tr><th>9:30</th></tr>     
											<tr><th>9:45</th></tr>      
											<tr><th>10PM</th></tr>      
											<tr><th>10:15</th></tr>      	
											<tr><th>10:30</th></tr>   
											<tr><th>10:45</th></tr>     
											<tr><th>11PM</th></tr>      
											<tr><th>11:15</th></tr>      		
											<tr><th>11:30</th></tr>      			
											<tr><th>11:45</th></tr> 					
											
										</tbody>
									</table>
								</div> <!-- end of schedule container -->
						<!--	</div>
							<!-- more tab sections are created by jQuery -->
						<!--</div>
						
						<input type="hidden" name="schedule">
						
						</fieldset> -->
						<fieldset><legend>IDF Generation</legend>
						<table id="step3">
							<tr><td>
								<label>Timestep</label></td><td>
								<input type="number" name="idf[timestep]" value="1"></td></tr>
							<tr><td>
								<label>Run Number</label></td><td>
								<input type="number" name="idf[run_number]" value="1"></td></tr>
							<tr><td>
								<label>Floor Height</label></td><td>
								<input type="number" name="idf[floor_height]" value="3.9624">meters</td></tr>
							<tr><td>
								<label>Plenums</label></td><td>
								<select name="idf[plenums]">
									<option value="true" selected>True</option>
									<option value="false">False</option>
								</td></tr>
							<tr><td>
								<label>Orientation</label></td><td>
								<input type="number" name="idf[orientation]" value="0.0">
								</td></tr>
							<tr><td>
								<label>Geometry Configuration</label></td><td>
								<select name="idf[geometry_configuration]">
									<option value="rectangle" selected>Rectangle</option>
									<!--<option value="Courtyard">Courtyard</option>
									<option value="L_Shape">L Shape</option>
									<option value="H_Shape">H Shape</option>
									<option value="T_Shape">T Shape</option>
									<option value="U_Shape">U Shape</option>-->
								</td></tr>
							<tr><td>
								<label>Zone Layout</label></td><td>
								<select name="idf[zone_layout]">
									<option value="Five_Zone" selected>Five Zone</option>
									</td></tr>
							<tr><td>
								<label>Roof Style</label></td><td>
								<select name="idf[roof_style]">
									<option value="flat" selected>Flat</option>
									<option value="gable">Gable</option>
									<option value="hip">Hip</option>
									</td></tr>
							<tr><td>
								<label>Wall Type</label></td><td>
								<select name="idf[wall_type]">
									<option value="Steel_Frame_Non_Res" selected>Steel Frame Non Res</option>
									<option value="Metal_Building_Non_Res">Metal Building Non Res</option>
									<option value="Wood_Framed">Wood Framed</option>
									<option value="Concrete_Non_Res">Concrete Non Res</option>
									</td></tr>
							<tr><td>
								<label>Roof Type</label></td><td>
								<select name="idf[roof_type]">
									<option value="iead_non_res" selected>IEAD Non Res</option>
									<option value="Attic_Roof_Non_Res">Attic Roof Non Res</option>
									</td></tr>
							<tr><td>
								<label>South WWR</label></td><td>
								<input type="number" name="idf[south_wwr]" value="0.477"></td></tr>
							<tr><td>
								<label>East WWR</label></td><td>
								<input type="number" name="idf[east_wwr]" value="0.477"></td></tr>
							<tr><td>
								<label>North WWR</label></td><td>
								<input type="number" name="idf[north_wwr]" value="0.477"></td></tr>
							<tr><td>
								<label>West WWR</label></td><td>
								<input type="number" name="idf[west_wwr]" value="0.477"></td></tr>
							<tr><td>
								<label>South Window Type</label></td><td>
								<select name="idf[south_win_type]">
									<option value="reference" selected>Reference</option>
									<option value="Single_Clear">Single Clear</option>
									<option value="Single_Bronze">Single Bronze</option>
									<option value="Single_Clear_LowE">Single Clear Low Energy</option>
									<option value="Double_Clear">Double Clear</option>
									<option value="Double_Bronze">Double Bronze</option>
									<option value="Double_Clear_LowE">Double Clear Low Energy</option>
									<option value="Triple_Clear">Triple Clear</option>
									<option value="Triple_Clear">Triple Clear</option>									
									<option value="Triple_Clear_LowE">Triple Clear Low Energy</option>									
									</td></tr>
							<tr><td>
								<label>East Window Type</label></td><td>
								<select name="idf[east_win_type]">
									<option value="reference" selected>Reference</option>
									<option value="Single_Clear">Single Clear</option>
									<option value="Single_Bronze">Single Bronze</option>
									<option value="Single_Clear_LowE">Single Clear Low Energy</option>
									<option value="Double_Clear">Double Clear</option>
									<option value="Double_Bronze">Double Bronze</option>
									<option value="Double_Clear_LowE">Double Clear Low Energy</option>
									<option value="Triple_Clear">Triple Clear</option>
									<option value="Triple_Clear">Triple Clear</option>									
									<option value="Triple_Clear_LowE">Triple Clear Low Energy</option>									
									</td></tr>
							<tr><td>
								<label>North Window Type</label></td><td>
								<select name="idf[north_win_type]">
									<option value="reference" selected>Reference</option>
									<option value="Single_Clear">Single Clear</option>
									<option value="Single_Bronze">Single Bronze</option>
									<option value="Single_Clear_LowE">Single Clear Low Energy</option>
									<option value="Double_Clear">Double Clear</option>
									<option value="Double_Bronze">Double Bronze</option>
									<option value="Double_Clear_LowE">Double Clear Low Energy</option>
									<option value="Triple_Clear">Triple Clear</option>
									<option value="Triple_Clear">Triple Clear</option>									
									<option value="Triple_Clear_LowE">Triple Clear Low Energy</option>									
									</td></tr>
							<tr><td>
								<label>West Window Type</label></td><td>
								<select name="idf[west_win_type]">
									<option value="reference" selected>Reference</option>
									<option value="Single_Clear">Single Clear</option>
									<option value="Single_Bronze">Single Bronze</option>
									<option value="Single_Clear_LowE">Single Clear Low Energy</option>
									<option value="Double_Clear">Double Clear</option>
									<option value="Double_Bronze">Double Bronze</option>
									<option value="Double_Clear_LowE">Double Clear Low Energy</option>
									<option value="Triple_Clear">Triple Clear</option>
									<option value="Triple_Clear">Triple Clear</option>									
									<option value="Triple_Clear_LowE">Triple Clear Low Energy</option>									
									</td></tr>
							<tr><td>
								<label>HVAC Type</label></td><td>
								<select name="idf[hvac_type]">
									<option value="vav" selected>VAV</option>
									<option value="psz_onoff">PSZ on off</option>
									<option value="psz_cav">PSZ CAV</option>
									</td></tr>
							<tr><td>
								<label>Heating Coil</label></td><td>
								<select name="idf[heating_coil]">
									<option value="Gas" selected>Gas</option>
									<option value="Electric">Electric</option>
									</td></tr>
							<tr><td>
								<label>Has Reheat</label></td><td>
								<select name="idf[has_reheat]">
									<option value="true" selected>True</option>
									<option value="false">False</option>
									</td></tr>
							<tr><td>
								<label>Reheat Coil</label></td><td>
								<select name="idf[reheat_coil]">
									<option value="Electric" selected>Electric</option>
									<option value="Gas">Gas</option>
									</td></tr>
							<tr><td>
								<label>Heating Efficiency</label></td><td>
								<input type="number" name="idf[heating_efficiency]" value="0.8"></td></tr>
							<tr><td>
								<label>Cooling Cop</label></td><td>
								<input type="number" name="idf[cooling_cop]" value="3.23372055845678"></td></tr>
							<tr><td>
								<label>Fan Efficiency</label></td><td>
								<input type="number" name="idf[fan_efficiency]" value="0.5915"></td></tr>
							<tr><td>
								<label>Fan Static Pressure</label></td><td>
								<input type="number" name="idf[fan_static_pressure]" value="1109.648"></td></tr>
							<tr><td>
								<label>Elecric Plug Intensity</label></td><td>
								<input type="number" name="idf[elec_plug_intensity]" value="10.76"></td></tr>
							<tr><td>
								<label>Internal Lighting Intensity</label></td><td>
								<input type="number" name="idf[int_lighting_intensity]" value="10.76"></td></tr>
							<tr><td>
								<label>External Lighting Intensity</label></td><td>
								<input type="number" name="idf[ext_lighting_intensity]" value="14804"></td></tr>
							<tr><td>
								<label>People Density</label></td><td>
								<input type="number" name="idf[people_density]" value="18.58"></td></tr>
							<tr><td>
								<label>Infiltration Per External Surface Area</label></td><td>
								<input type="number" name="idf[infiltration_per_ext_sur_area]" value="0.000302"></td></tr>
							<tr><td>
								<label>OA Vent Per Person</label></td><td>
								<input type="number" name="idf[oa_vent_per_person]" value="0.0125"></td></tr>
							<tr><td>
								<label>OA Vent Per Area</label></td><td>
								<input type="number" name="idf[oa_vent_per_area]" value="0.0"></td></tr>
							<tr><td>
								<label>Length2</label></td><td>
								<input type="number" name="idf[length2]" value="0.0">meters</td></tr>
							<tr><td>
								<label>Width2</label></td><td>
								<input type="number" name="idf[width2]" value="0.0">meters</td></tr>
							<tr><td>
								<label>End1</label></td><td>
								<input type="number" name="idf[end1]" value="0.0"></td></tr>
							<tr><td>
								<label>End2</label></td><td>
								<input type="number" name="idf[end2]" value="0.0"></td></tr>
							<tr><td>
								<label>Offset1</label></td><td>
								<input type="number" name="idf[offset1]" value="0.0"></td></tr>
							<tr><td>
								<label>Offset2</label></td><td>
								<input type="number" name="idf[offset2]" value="0.0"></td></tr>
							<tr><td>
								<label>Offset3</label></td><td>
								<input type="number" name="idf[offset3]" value="0.0"></td></tr>
							<tr><td>
								<label>Has Setback</label></td><td>
								<select name="idf[has_setback]">
									<option value="true" selected>True</option>
									<option value="false">False</option>
									</td></tr>
							<tr><td>
								<label>Has Night Cycle</label></td><td>
								<select name="idf[has_night_cycle]">
									<option value="true" selected>True</option>
									<option value="false">False</option>
									</td></tr>
							<tr><td>
								<label>Night Cycle</label></td><td>
								<select name="idf[night_cycle]">
									<option value="CycleOnAny" selected>Cycle On Any</option>
									<option value="CycleOnAnyZoneFansOnly">Cycle On Any Zone Fans Only</option>
									<option value="StayOff">Stay Off</option>
									</td></tr>
							<tr><td>
								<label>Has DVC</label></td><td>
								<select name="idf[has_dcv]">
									<option value="false" selected>False</option>
									<option value="true">True</option>
									</td></tr>
							<tr><td>
								<label>Cooling Setback</label></td><td>
								<input type="number" name="idf[cooling_setback]" value="26.7"></td></tr>
							<tr><td>
								<label>Heating Setback</label></td><td>
								<input type="number" name="idf[heating_setback]" value="15.6"></td></tr>
							<tr><td>
								<label>Cooling Setpoint</label></td><td>
								<input type="number" name="idf[cooling_setpoint]" value="24.0"></td></tr>
							<tr><td>
								<label>Heating Setpoint</label></td><td>
								<input type="number" name="idf[heating_setpoint]" value="21.0"></td></tr>
							<tr><td>
								<label>Has Weekend Occupancy</label></td><td>
								<select name="idf[has_weekend_occupancy]">
									<option value="true" selected>True</option>
									<option value="false">False</option>
									</td></tr>
							<tr><td>
								<label>Weekend Occupancy Type</label></td><td>
								<select name="idf[weekend_occupancy_type]">
									<option value="Saturday" selected>Saturday</option>
									<option value="Sunday">Sunday</option>
									<option value="Weekend">Weekend</option>
									</td></tr>
							<tr><td>
								<label>Weekday Start Time</label></td><td>
								<input type="time" name="idf[weekday_start_time]" value="06:00"></td></tr>
							<tr><td>
								<label>Weekday End Time</label></td><td>
								<input type="time" name="idf[weekday_end_time]" value="22:00"></td></tr>
							<tr><td>
								<label>Weekend Start Time</label></td><td>
								<input type="time" name="idf[weekend_start_time]" value="06:00"></td></tr>
							<tr><td>
								<label>Weekend End Time</label></td><td>
								<input type="time" name="idf[weekend_end_time]" value="18:00"></td></tr>
							<tr><td>
								<label>Use Mechanical Vent</label></td><td>
								<select name="idf[use_mechanical_vent]">
									<option value="false" selected>False</option>
									<option value="true">True</option>
									</td></tr>
						</table>
						</fieldset>
					<?php endif; ?>
					
						
					<fieldset id="map"><legend>Select location</legend>
					
						<p id = "step4">Current Selection: <span id="locationOutput">none</span></p>
						
								<input type="hidden" name="climateZone">
						
								<input type="hidden" name="weatherFile">
						<div id="googleMap" ></div>
						
						
								<input type="hidden" name="location" value="none">
					</fieldset>
					<fieldset><legend>Input Data</legend>
					<div id="accordion">
						 <h3>Electricity</h3>
						  <div>
								<label id="electricity"> Have a file containing energy usage: </label>
								<input type="file" name="energyFile"><br>
								<p>Sample File: <a href="SampleMonthlyUserInput.csv" type="option">Monthly Sample</a>, <a href="SampleHourlyUserInput.csv" class="option">Hourly Sample</a></p>
								<p> OR </p>
								<label> Energy usage from previous months: </label><br>
								<div id="energyInputs"></div>
						  </div>
						  
						  <h3>Gas</h3>
						  <div>
								<label id="gas">Have a file: </label>
								<input type="file" name="gasFile"><br>
								<p> OR </p>
								<label> Gas usage from previous months: </label><br>
								<div id="gasInputs"></div>
						  </div>
						  
						  <h3>Temperature</h3>
						  <div>
								<label id="temp">Have a file containing home temperature readings: </label>
								<input type="file" name="tempFile"><br>
						  </div>
						 
					</div>
					</fieldset>
					<fieldset><legend>Tune</legend>
						<p>You have completed all the steps of the wizard!</p>
						<em>Click Tune below to Submit your Information</em><br /><br />
						<label>Email Address <i>(optional): </i></label><input type="text" name="email">
					</fieldset>
								
				</form>
			</div>
		</div> <!-- end of inside -->
	</body>

</html>
