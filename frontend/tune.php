


<!DOCTYPE html>
<html>
	<head>
		<title>Receipt</title>
		
		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, minimum-scale=1" />
		
		<link type="text/css" rel="stylesheet" href="stylePractice2.css" />
		<link type="text/css" rel="stylesheet" href="mobile.css" />
		<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
		<script>
				$(document).ready(function() {
					var userData = $("input[name=userData]").val();
					var baseModel = $("input[name=baseModel]").val();
					var schedule = $("input[name=schedule]").val();
					var parameters = $("input[name=parameters]").val();
					var weather = $("input[name=weather]").val();
					var email = $("input[name=email]").val()
					$.post("http://yourdomain.com/autotune/service/service.php",
						{
						  userData:userData,
						  baseModel:baseModel,
						  schedule:schedule,
						  parameters:parameters,
						  weather:weather,
						  email:email
						}, 
						function(data) {
							xmlDoc = $.parseXML(data),
							$xml = $(xmlDoc),
							$tracking = $xml.find("tracking");
							$position = $xml.find("position");
							$(".tracking").append("Tracking Number: " + $tracking.text());
							$(".position").append("Position: " + $position.text());
							
						});
				});
			</script>

		
	</head>
	
	<body>
	
		<div id="logo">
			<a href="home.html"><img src="pictures/Logo.png"/></a>
		</div>
		<div class="inside">
			<div id="pageTitle"><h1>Receipt</h1></div>
			<div class="left box">
				<p class="emphasized">
					<span class="tracking"></span><br>
					<span class="position"></span>
			<?php
				function getPost($input, $defaultValue) {
					if(isset($_POST[$input])){
						return $_POST[$input];
					}
					else {
						return $defaultValue;
					}
				}
				function getFile($input, $defaultValue) {
					if(isset($_FILES[$input]) && $_FILES[$input]['size'] > 0) {
						$contents = file_get_contents($_FILES[$input]['tmp_name']);
						return $contents;
					}
					else {
						return $defaultValue;
					}
				}
				function getArrayElement($array, $element, $defaultValue) {
					if(isset($array[$element])) {
						return $array[$element];
					}
					else {
						return $defaultValue;
					}
				}
				$idfInputs = getPost('idf', array());								//idf inputs, used for idf generator
				$model = getArrayElement($idfInputs, 'building_type', null);		//model -> super market, apartment, etc.
				$numFloors = getArrayElement($idfInputs, 'number_of_floors', null);	//number of the the building has
				$sqrFootage = getPost('size', null);								//the amount of square footage the building contains
				$condition = getArrayElement($idfInputs, 'building_age', null);		//condition of the building -> new, recent, old
				$width = getArrayElement($idfInputs, 'width1', null);				//the width of the building
				$length = getArrayElement($idfInputs, 'length1', null);				//the length of the building
				$numResidents = getPost('numRes', null);							//the max number of residents that occupy the building
				$schedule = getPost('schedule', null);			//schedule of the building's usage
				$climate = getPost('climateZone', null);		//the climate zone which the building is located
				$weatherFile = getPost('weatherFile', null);	//the name of the weather file autotune should use
				$location = getPost('location', null);			//the "city, state" which the building is located
				$eFile = getFile('energyFile', false);			//user's file containing the energy usage
				$energyUsages = getPost('energyUsage', null);	//the amount of energy used in a particular month
				$gFile = getFile('gasFile', false);				//user's file containing gas usage
				$gasUsages = getPost('gasUsage', null);			//user monthly input for natural gas usage
				$tFile = getFile('tempFile', false);			//user's file containing temperature readings
				$email = getPost('email', "");					//user's email
				

				
				//If length and width are not set, calculate them
				if(!$width && !$length) {
					$width = sqrt($sqrFootage/$numFloors);
					$length = $width;
				}
				//If length or width is set, calculate the other
				else if($length && !$width) {
					$width = ($sqrFootage/$numFloors)/$length;
				}
				else if($width && !$length) {
					$length = ($sqrFootage/$numFloors)/$width;
				}
				
				//Set the width and length to units of meters
				$width = toMeters($width); // ft -> m
				$length = toMeters($length);
				$idfInputs['width1'] = $width;
				$idfInputs['length1'] = $length;
				
				//If timestep was given, validate it
				if(isset($idfInputs['timestep'])) {
					if(isDivisorOf($idfInputs['timestep'], 60)) {
						//valid
					}
					else {
						//invalid
						$idfInputs['timestep'] = 1;
					}
				}
				
				//Get city and state from the location, format: "city, state"
				$commaPos = strpos($location, ",");
				$city = substr($location, 0, $commaPos);
				$state = substr($location, $commaPos+2); 
				
				//Generate base model
				checkTypes($idfInputs);
				include 'paramGen.php';
				$baseModel = generateModel($city, $state, $climate, $idfInputs);
				
				//Create energy spreadsheet if user entered values
				$uDataArray = array();
				
				$energyFilledOut = completedInput($energyUsages);
				$gasFilledOut = completedInput($gasUsages);
				
				/*
				case 1: files only are provided
					combine files if they are compatible
				case 2: input only is provided
					combine both inputs
				case 3: files and input are provided
					combine if compatible, otherwise keep file
					
				compatible - both contain the same number of rows
				*/
				$dateTimeNeeded = true;
				if($eFile && isCompatible($eFile, $uDataArray)) addFile($eFile, $uDataArray, $dateTimeNeeded);
				if($gFile && isCompatible($gFile, $uDataArray)) addFile($gFile, $uDataArray, $dateTimeNeeded);
				if($tFile && isCompatible($tFile, $uDataArray)) addFile($tFile, $uDataArray, $dateTimeNeeded);
				if($dateTimeNeeded && ($energyFilledOut || $gasFilledOut)) addMonthlyCol(12, $uDataArray);
				$monthlyCompatible = (numRows($uDataArray) == 13 || numRows($uDataArray) == 0); // 12 months + 1 header, or no files have been added
				if($energyFilledOut && $monthlyCompatible && !$eFile) addEnergyUsage($energyUsages, $uDataArray);
				//if($gasFilledOut && $monthlyCompatible && !$gFile) addGasUsage($gasUsages, $uDataArray);
				$userData = createSpreadsheet($uDataArray);

				//Get parameter file contents
				include 'paramMatch.php';
				$paramFileName = getParamFileName($model);
				$paramContents = file_get_contents($paramFileName);
				
				
//------------------------------------------------------------------------------------------------------------				
				function addFile($fileContents, &$dataArray, &$addDateTime) {
					$validHeaders = array();
					$csvArray = csvToArray($fileContents);
					if (validDateTime($csvArray)) {
						if ($addDateTime) { //If we need to add date time, leave it in the array -- we don't need it anymore after this point
							$addDateTime = false;
						}	
						else { // Else remove the date/time column
							$dateTimes = getDateTime($dataArray);
							reorderArray($dateTimes, $csvArray); //reoder the array before combining so that the data will match previous data
							removeDateTime($csvArray);
						}
						combineArrays($dataArray, $csvArray);
						return true;
					}
					else {
						return false;
					}
				}
				
				function isCompatible($fileContents, $dataArray) {
					if (numRows($dataArray) == 0) return true;
					if (numRowsCSV($fileContents) == numRows($dataArray)) {
						$csvArray = csvToArray($fileContents);
						return compatibleDateTimes($dataArray, $csvArray);
					}
					else {return false;}
				}
				
				function csvToArray($csvContents) {//adds csv contents to array
					$rows = str_getcsv($csvContents, "\n"); //parse the rows
					for($i=0; $i<count($rows); $i++) {
						$rows[$i] = str_getcsv($rows[$i]); //parse the columns
					}
					
					return $rows;
				}
				
				function numRowsCSV($csvContents) {
					$rows = str_getcsv($csvContents, "\n"); //parse the rows
					return count($rows);
				}
				
				function numRows($array) { //determines the number of used rows in a multidimensional array that might have many rows initialized but is using fewer rows
					for($i=0; $i<count($array); $i++) {
						if(count($array[$i]) == 0) return $i;
					}
					return count($array);
				}
				
				function reorderArray($dateTimes, &$array) { //Reoders the array according to the given date/time values. The array should already contain date/time entries.
				/* Example
				  $dateTimes   $array			$result
					1/31 	  2/28  dog			1/31  cat
					2/28	  3/31  bird	==> 2/28  dog
					3/31	  1/31  cat			3/31  bird
				
				*/
					$col = array_search("Date/Time", $array);
					for($i=1; $i<=count($dateTimes); $i++) {//after each iteration, the "i"th row should have the correct row (Bubble Sort)
						$swapped = false;
						for($j=$i; $j<count($array) && !$swapped; $j++) {
							if($dateTimes[$i-1] == $array[$j][$col]) {
								//swap
								$temp = $array[$j];
								$array[$j] = $array[$i];
								$array[$i] = $temp;
								$swapped = true;
							}
						}
					}
				}
				
				function combineArrays(&$baseArray, $otherArray) { //combines two multidimensional arrays
					for($i=0; $i<count($otherArray); $i++) { // ? -> change this to foreach, use the $key to find which row to insert the data into
						for($j=0; $j<count($otherArray[$i]); $j++) {
							$next = getNext($baseArray, $i);
							$baseArray[$i][$next] = $otherArray[$i][$j];
						}
					}
				}
				
				function compatibleDateTimes($baseArray, $otherArray) {
					$baseDates = getDateTime($baseArray); 
					$otherDates = getDateTime($baseArray);
					$found = true;
					for($i=1; $i<count($baseDates) && $found; $i++) { //for each item in base array, search for its counterpart; stop searching if one entry cannot be found
						$found = false;
						for($j=0; $j<count($otherDates) && !$found; $j++) { //keep searching if the element has not been found
							if($baseDates[$i] == $otherDates[$j]) {$found = true;}
						}
					}
					
					return $found;
				}
				
				function validDateTime($array) { 					// returns true or false whether the Date/Time column follows equal and regular timesteps 
					$col = array_search("Date/Time", $array[0]); 	//determine which column "date/time" is in
					if($col === false) { 							// "Date/Time" does not exist in the array
						return false;
					}
					$valid = true;
					
					if(count($array) > 3) { // 1 header + 2 rows
						//determine if there is monthly interval
						$month = (int)substr($array[1][$col], 0, strpos($array[1][$col], "/"));
						for($i=2; $i<count($array) && $valid; $i++) {
							//get month
							$nextMonth = (int)substr($array[$i][$col], 0, strpos($array[$i][$col], "/"));
							if(($month%12+1) != $nextMonth) $valid = false;
							$month = $nextMonth;
						}
						
						
						if($valid) return $valid; //return true if date/time contains monthly intervals
						else $valid = true; //else try the next validation technique
						
						//get the first date/time					
						$time = parseDateTime($array[1][$col]); 		
						if(!$time) {//could not parse the date/time --> probably incorrect date/time format
							return false;
						}
					
						$nextTime = parseDateTime($array[2][$col]);
						$interval = $time->diff($nextTime);
						$time = $nextTime;
						for($i=3; $i<count($array); $i++) {
							$nextTime = parseDateTime($array[$i][$col]);
							$nextInterval = $time->diff($nextTime);
							if((array)$interval != (array)$nextInterval) {	
								
								print_r($time);
								print_r($nextTime);
								print_r($nextInterval);
								return false;
							}
							$time = $nextTime;
						}
						
					}
					return $valid;
					
				}
		
				function getDateTime($array) { //returns array holding all the date/time entries
					$col = array_search("Date/Time", $array[0]);
					if($col === false) return false; // "Date/Time" could not be found
					
					$dateEntries = array();
					for($i=1; $i<count($array); $i++) {
						$dateEntries[$i-1] = $array[$i][$col];
					}
					return $dateEntries;
				}
		
				function removePadding($str) { //returns string without whitespaces at beginning/end of string and where there are double whitespaces
					$strippedStr = $str;
					while(substr($strippedStr, 0, 1) == " ") {//remove whitespaces at beginning
						$strippedStr = substr($strippedStr, 1);
					}
					while(substr($strippedStr, -1) == " ") {//remove whitespaces at end
						$strippedStr = substr($srippedStr, 0, -1);
					}
					while(strpos($strippedStr, "  ") !== false) {//replace double whitespaces with a single whitespace
						$strippedStr = str_replace("  ", " ", $strippedStr);
					}
					return $strippedStr;
				}
				
				function parseDateTime($str) { // parses the date/time entry into a datetime object
					//set timezone without DST
					//DST can create problems when calculating dateTime intervals
					date_default_timezone_set('Africa/Dakar');
					
					$entry = removePadding($str);
					$date = DateTime::createFromFormat('m/d H:i:s', $entry);
					return $date;
				}
				
				function removeDateTime(&$array) { //removes the date/time col in the array 
													// cols on right of date/time col are moved to the left
					$col = array_search("Date/Time", $array[0]);
					
					if($col !== false) {
						for($i=0; $i<count($array); $i++) {
							removeCol($col, $array[$i]);
						}
						return true; //success
					}
					else return false; //could not find Date/Time
				}
				
				function removeCol($currCol, &$array) { //replaces the current col with the next col until all cols are moved (recursive)
					if($currCol == (count($array)-1)) {
						//delete if last col
						$array[$currCol] = null;
					}
					else {
						$nextCol = $currCol + 1;
						$array[$currCol] = $array[$nextCol];
						removeCol($nextCol, $array);
					}
				}
				
				function completedInput($input) {
					$filledOut = true;
					foreach($input as $key=>$value) {
						if(!$input[$key]) $filledOut = false;
					}
					return $filledOut;
				}
				
				function getNext($array, $index) { //for multidimensional arrays
								//gets the key(number) of the next element, if null an array is initialized
					if(!isset($array[$index])) {
						$array[$index] = array();
					}
					return count($array[$index]);
				}
				
				function createSpreadsheet($dataArray) { //$dataArray needs to be a two-dimensional array
					$content = "";
					for($i=0; $i<count($dataArray); $i++) {
						for($j=0; $j<count($dataArray[$i]) && $dataArray[$i][$j] != null; $j++) {
							$content .= $dataArray[$i][$j] . ",";
						}
						$content = substr($content, 0, -1); //take off the last comma
						$content .= "\n"; //end of row
					}
					return $content;
				}
				
				function addEnergyUsage($energyUsageArray, &$dataArray) {
					
					$next = getNext($dataArray, 0);
					$dataArray[0][$next] = "Whole Building:Total Building Electric Demand [W](TimeStep)";
					
					for($i=1; $i<=count($energyUsageArray); $i++) {
						// $energy = kwhToJoules($energyUsageArray[$i-1]);
						$energy = $energyUsageArray[$i-1];
						$next = getNext($dataArray, $i);
						$dataArray[$i][$next] = $energy;
						
					}				
				}
				
				function addGasUsage($gasUsageArray, &$dataArray) {
					$next = getNext($dataArray, 0);
					$dataArray[0][$next] = "Whole Building:Total Building Gas Demand [J](TimeStep)";
					
					for($i=1; $i<=count($gasUsageArray); $i++) {
						$energy = ccfToJoules($gasUsageArray[$i-1]);
						
						$next = getNext($dataArray, $i);
						$dataArray[$i][$next] = $energy;
						
					}
				}
				
				function addMonthlyCol($numMonths, &$dataArray) { //adds a monthly column beginning with January
					$next = getNext($dataArray, 0);
					$dataArray[0][$next] = "Date/Time";
					$year = date("Y");
					for($i=0; $i<$numMonths; $i++) {
						if(($i > 12) && ($i%12 == 0)) { //after 12 months, go to next year
							$year++;
						}
						$mm = $i%12 + 1;
						$month = date("m/t", strtotime("$year-$mm")); 
						$next = getNext($dataArray, $i+1);
						$dataArray[$i+1][$next] = "$month  23:59:59";
					}
				}
				
				function checkTypes(&$array) { //changes certain string values into their true values -- ex. '23.4' -> 23.4
					foreach($array as $key=>$value) {
						if(is_numeric($value)) {
							$array[$key] = (float)$value;
						}
						else if($value == "false" || $value == "True") {
							$array[$key] = false;
						}
						else if($value == "true" || $value == "True") {
							$array[$key] = true;
						}
					}
				}
				
				function countDigits($num) {	
					//if null, then the value is zero -> 1 digit
					if($num == null) {
						return 1;
					}
					
					$strNum = (string)$num;
					//if there is a decimal, look only at the digits before the decimal place
					$decimal = strpos($strNum, ".");
					if($decimal) {
						$strNum = substr($strNum, 0, $decimal);
					}
					return strlen($strNum);
				}
				
				function kwhToJoules($kwh) {
					$joules = 3600000 * $kwh;
					return $joules;
				}
				
				function ccfToJoules($ccf) {
					$joules = 105506000 * $ccf;
					return $joules;
				}
				
				function toMeters($feet) {
					$meters = $feet*0.3048;
					return $meters;
				}
				
				function toFeet($meters) {
					$feet = $meters/0.3048;
					return $feet;
				}
				
				function isDivisorOf($divisor, $num) {
					$otherDivisor = $num/$divisor;
					//if otherDivisor is an integer, then both are divisors
					return is_int($otherDivisor);
				}
//----------------------------------------------------------------------------------------------------------
				?>
				
				<form id="create" action="http://yourdomain.com/autotune/service/service.php" method="post">
					<input type="hidden" name="userData" value="<?php echo $userData; ?>" />
					<input type="hidden" name="baseModel" value="<?php echo $baseModel; ?>" />
					<input type="hidden" name="schedule" value="<?php echo $schedule; ?>" />
					<input type="hidden" name="parameters" value="<?php echo $paramContents; ?>" />
					<input type="hidden" name="weather" value="<?php echo $weatherFile; ?>" />
					<input type="hidden" name="email" value="<?php echo $email; ?>" />
				</form>
				
				</p>
			</div>
			
			<p class="important">
				*Please keep your tracking number so you can access your building models in the future
			</p>
			
			
			<a class="button" href="home.html">Home</a>
	</body>
</html>

