<?php
header("Access-Control-Allow-Origin: *"); //CORS
 
// service.php
// provides all services needed for interaction with the database
// --definitions are at end of file
// default output is in XML

/*POST
	baseModel, parameters, schedule, userdata

//REQUEST (GET or POST)
	weather, email, tracking, terminate, full, retune, modelId, json
	
**Any given boolean values should be expressed as 1 or 0**	
	
Services
--------------Tune new order--------------------
	Input 
		Required -> userData, baseModel, schedule, parameters, weather
		Optional -> email
	Output
		tracking, position
		
--------------Change terminate-----------------
	Input
		Required -> tracking, terminate
	Output
		tracking, position, terminate, runtime, model ids, model fits
		
--------------Get order details------------		
	Input
		Required -> tracking
		Optional -> full (default=false),
	Output
		full=false
			tracking, position, runtime, terminate, model ids, model fits
		full=true (includes all elements with full=false)
			weather, baseModel, parameters, schedule, userData, model files
			
--------------Get single model------------			
	Input
		Required -> tracking, modelId
	Output
		tracking, runtime, model id, model file, model fit
	
--------------Retune a model--------------------
	Input
		Required -> tracking, retune
	Output
		new tracking, position

		
If an error occurs, output is returned with an error code along with the error description. Here are the error codes with their description:

1000-1999: Input error
	1000 Did not include all requirements for creating an order.
	1005 Invalid tracking number
	1010 Invalid model id
2000-2999: Database error
	
	
	
Format of XML:
=== Error output ===
	<autotune>
		<error>
			<code>1234</code>
			<description>Some description of the error.</description>
		</error>
	</autotune>
	
=== Full output ===
	<autotune>
		<tracking>8765</tracking>
		<position>-1</position>
		<weather>USA_AL_Birmingham_whatever.epw</weather>
		<email>joe@gmail.com</email>
		<baseModel>string-goes-here</baseModel>
		<parameters>string-goes-here</parameters>
		<schedule>string-goes-here</schedule>
		<userData>string-goes-here</userData>
		<terminate>0</terminate>
		<runtime>86403</runtime>
		<models>
			<model>
				<id>1</id>
				<fitness>0.743</fitness>
				<file>string-goes-here</file>
			</model>
			<model>
				<id>2</id>
				<fitness>1.234</fitness>
				<file>string-goes-here</file>
			</model>
		</models>
	</autotune>
	
	
If json is true, data will be outputted in JSON format:
==== Error Output ====
{"autotune":
	{"error":
		{"code":1234,
		 "description":"Error details"
		}
	}
}
	
	
==== Full Output ====
{"autotune":
  {"tracking":"8765",
   "position":-1,
   "weather":"USA_AL_Birmingham_whatever.epw",
   "email":"joe@gmail.com",
   "basemodel":"string-goes-here",
   "parameters":"string-goes-here",
   "schedule":"string-goes-here",
   "userData":"string-goes-here",
   "terminate":0,
   "runtime":45678,
   "models":[
     {"id":1, "fitness":0.765, "file":"string-goes-here"}
     {"id":2, "fitness":1.234, "file":"string-goes-here"}]
   }
}
*/

$jsonOutput = (isset($_REQUEST['json']) ? $_REQUEST['json'] : false); 
$soap = true;

require 'dbAccess.php';
$db = new AutotuneDb();
if(!isset($_REQUEST['tracking']) && isset($_POST['userData'], $_POST['baseModel'], $_POST['schedule'], $_POST['parameters'], $_REQUEST['weather'])) { // tune an order
	$soap = false;
	
	$uData = $_POST['userData'];
	$bModel = $_POST['baseModel'];
	$schedule = $_POST['schedule'];
	$parameters = $_POST['parameters'];
	$weather = $_REQUEST['weather'];
	
	// set optional inputs
	$email = (isset($_REQUEST['email']) ? $_REQUEST['email'] : ""); 

	tune($uData, $bModel, $schedule, $parameters, $weather, $email);
	
	
	
}
else if(isset($_REQUEST['tracking'])) { // do something with given tracking
	$soap = false;
	$tracking = $_REQUEST['tracking'];
	
	// give full details
	if(isset($_REQUEST['full']) && $_REQUEST['full']) {
		getFullOutput($tracking);		
	}
	
	 // set terminate
	else if(isset($_REQUEST['terminate'])) {
		$terminate = $_REQUEST['terminate'];
		setTerminate($tracking, $terminate);
	}
	
	// get single model
	else if(isset($_REQUEST['modelId'])) {
		$modelId = $_REQUEST['modelId'];
		getModel($tracking, $modelId);
	}
	
	// retune a model
	else if(isset($_REQUEST['retune']) && $_REQUEST['retune']) {
		retune($tracking);
	}
	
	// return default details 
	else if(!isset($_REQUEST['full']) || !$_REQUEST['full']) {
		getOutput($tracking);
	}
	
}
else if(count($_REQUEST) > 0){ //tracking is not set and all parameters were not given
	//return error because required parameters were not given
	echo outputError("1000");
}



function tune($uData, $bModel, $schedule, $parameters, $weather, $email) {
	
	$scheduleInput["schedule"] = $schedule;
	$parametersInput["parameters"] = $parameters;

	$db = new AutotuneDb();
	$id = $db->getNewTracking($bModel, $uData);
	$db->insertInputFile($id, $scheduleInput);
	$db->insertInputFile($id, $parametersInput);
	$db->setWeather($id, $weather);
	$db->setEmail($id, $email);
	return outputNewTracking($id, $db->getQueuePosition($id));
}


function getFullOutput($tracking) {
	$db = new AutotuneDb();
	if(!$db->validTracking($tracking)) {
		// return error for invalid tracking
		return outputError("1005");;
	}
	else return fullOutput($tracking);
}

function getOutput($tracking) {
	$db = new AutotuneDb();
	if(!$db->validTracking($tracking)) {
		// return error for invalid tracking
		return outputError("1005");;
	}
	return defaultOutput($tracking);
}

function terminate($tracking) {
	return setTerminate($tracking, true);
}

function resume($tracking) {
	return setTerminate($tracking, false);
}

function setTerminate($tracking, $terminate) {
	$db = new AutotuneDb();
	if(!$db->validTracking($tracking)) {
		// return error for invalid tracking
		return outputError("1005");;
	}
	$db->setTerminate($tracking, $terminate);
	
	// resuming an order
	if(!$terminate) {
	
		// if the order has finished, put it back into the queue
		$pos = $db->getQueuePosition($tracking);
		if($pos < 0) {
			$db->updateQueuePosition($tracking);
		}		
	}
	return defaultOutput($tracking);
}

function getModel($tracking, $modelId) {	
	$db = new AutotuneDb();
	if(!$db->validTracking($tracking)) {
		// return error for invalid tracking
		return outputError("1005");;
	}
	// check if model id is valid
	if($db->validModelId($modelId)) {
		return singleModelOutput($tracking, $modelId);
	}
	else {
		// return error for invalid model id
		return outputError("1010");
	}
}

function retune($tracking) {
	$db = new AutotuneDb();
	if(!$db->validTracking($tracking)) {
		// return error for invalid tracking
		return outputError("1005");;
	}
	$newTracking = $db->duplicate($tracking);
	$pos = $db->getQueuePosition($newTracking);
	return outputNewTracking($newTracking, $pos);
}

function singleModelOutput($tracking, $modelId) {
	$db = new AutotuneDb();
	$details = array("tracking"=>$tracking,
					"runtime"=>$db->getRuntime($tracking));
	
	$model = array("id"=>$modelId,
					"fitness"=>$db->getFit($modelId),
					"file"=>($db->getFile($modelId)));
	$modelSet = array($model);
	return outputDetails($details, $modelSet);
}

function fullOutput($tracking) {
	$db = new AutotuneDb();
	
	$pos = $db->getQueuePosition($tracking);
	$weather = $db->getWeather($tracking);
	if($weather == null) $weather = "";
	$email = $db->getEmail($tracking);
	$inputFiles = $db->getInputFiles($tracking);
	$runtime = $db->getRuntime($tracking);
	$terminate = $db->getTerminate($tracking);
	$details = array("tracking"=>$tracking,
					"position"=>$pos,
					"weather"=>$weather,
					"email"=>$email,
					"baseModel"=>($inputFiles['baseModel']),
					"parameters"=>($inputFiles['parameters']),
					"schedule"=>($inputFiles['schedule']),
					"userData"=>($inputFiles['userData']),
					"terminate"=>$terminate,
					"runtime"=>$runtime);
	$modelIds = $db->getModelIds($tracking);
	$modelFile = array();
	$models = array();
	foreach ($modelIds as $x=>$value) {
		$models[$x] = array("id"=>$value,
							"fitness"=>$db->getFit($value),
							"file"=>($db->getFile($value)));
	}
	return outputDetails($details, $models);

}

function defaultOutput($tracking) {
	$db = new AutotuneDb();
	$pos = $db->getQueuePosition($tracking);
	$details = array("tracking"=>$tracking,
					"position"=>$pos,
					"terminate"=>$db->getTerminate($tracking),
					"runtime"=>$db->getRuntime($tracking));
	$modelIds = $db->getModelIds($tracking);
	$models = array();
	foreach ($modelIds as $x=>$value) {
		$models[$x] = array("id"=>$value,
							"fitness"=>$db->getFit($value));
	}
	return outputDetails($details, $models);
}	
	
function outputError($code) {
	$errors = array("1000"=>"Did not include all requirements for creating an order.",
					"1005"=>"Invalid tracking number",
					"1010"=>"Invalid model id",
					"2000"=>"",
					"2005"=>"");
	$autotune = array("autotune"=>
					array("error"=>
						array("code"=>$code,
							  "description"=>$errors[$code])));
	$json = json_encode($autotune);
	
	global $jsonOutput;
	global $soap;
	if($soap) return $json;
	else if($jsonOutput) {
		echo $json;
	}
	else {				
		$xml = new SimpleXMLElement('<autotune></autotune>');
		$error = $xml->addChild('error');
		$error->addChild('code', $code);
		$error->addChild('description', $errors[$code]);
		
		echo $xml->asXML();
		
	}
	
}

function outputNewTracking($tracking, $pos) {
	global $jsonOutput;
	global $soap;
	$details = array("tracking"=>$tracking,
					"position"=>$pos);
	$autotune = array("autotune"=>$details); //append details to autotune
	$json = json_encode($autotune);
	
	if($soap) return $json;
	else if ($jsonOutput) {
		echo $json;
	}
	else {	
		$xml = new SimpleXMLElement('<autotune></autotune>');
		$xml->addChild('tracking', $tracking);
		$xml->addChild('position', $pos);
		
		echo $xml->asXML();
	}
	
}

function outputDetails($details, $models) { // both details and models should be arrays
	global $jsonOutput;
	global $soap;
	
	if($soap || $jsonOutput) {
		jsonPrepare($details);
		$details["models"] = $models; //append models to the end of the details array
		$autotune = array("autotune"=>$details); //append details to autotune
		$json = json_encode($autotune);
		
		if($soap) return $json; //return for SOAP
		else if($jsonOutput) {
			echo $json;
		}
	}
	else {
		$xml = new SimpleXMLElement('<autotune></autotune>');
		foreach ($details as $tag=>$value) {
			if($value != null && $value != "") {
				$xml->addChild($tag, $value);
			}		
			else {
				$xml->addChild($tag, '');
			}
		}
		
		$modelSet = $xml->addChild('models');
		
		foreach ($models as $model) {
			$eachModel = $modelSet->addChild('model');
			foreach ($model as $tag=>$value) {
				$eachModel->addChild($tag, $value);
			}
		}
		
		echo $xml->asXML(); //echo for ajax
	}
}

function jsonPrepare(&$array) { //encodes strings in UTF-8 so that it can be json_encode() 'ed
	foreach($array as $key=>$value) {
		if(is_string($value)) {
			$array[$key] = htmlentities($value, UTF-8);
		}
	}
}



/*

baseModel: string of the base IDF file
email: user's email address (optional; defaults to empty string)
full: boolean whether full results should be returned (optional; defaults to False)
model:
	modelId: the model id
	fitness: the model fitness
	file: tuned IDF model
parameters: string of the parameter CSV file
position: current queue position
retune: boolean whether to retune the tracking order
runtime: time (in seconds) a job has been running
schedule: string of the schedule CSV file
terminate: boolean request indicating whether to terminate or stop the order
tracking: the tracking id
userdata: string of the user's CSV file
weather: string for the weather file name


*/



?>