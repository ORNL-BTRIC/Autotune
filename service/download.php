<?php
/*
-REQUEST (GET or POST)
tracking, modelId

All output will be passed to the browser for the user to download

----------Download all models for one tracking---------
	Input
		Required -> tracking
	Output
		Zip file
			Name = "[tracking].zip"
			Contents = all models named as "tuned_[modelId].idf"
		
		
----------Download one model------------
	Input
		Required -> tracking, modelId
	Output
		Model file
			Name = "tuned_[modelId].idf"
	
	
----------Download multiple models------------
	Input
		Required -> tracking, models
	Output
		Zip file
			Name = "[tracking].zip"
			Contents = all models named as "tuned_[modelId].idf"
			
If modelId and models are both included, models will be used by default and modelId will be ignored.
If models contains an invalid model, all models for the tracking will be provided instead.
*/

require 'dbAccess.php';
$db = new AutotuneDb();


if(isset($_REQUEST['tracking'])) {
	$tracking = $_REQUEST['tracking'];
	
	//check if tracking is valid
	if($db->validTracking($tracking)) {
		
		// download a single model
		if(isset($_REQUEST['modelId']) && !isset($_REQUEST['models'])) {
			$modelId = $_REQUEST['modelId'];
			
			//check if model id is valid
			if($db->validModelId($modelId)) {
			
				$fileName = "tuned_$modelId.idf";
				$dir = "filesFolder";
				file_put_contents("$dir/$fileName", $db->getFile($modelId));
				$db->downloadFile("$dir/$fileName");
				unlink("$dir/$fileName");
			}
		}
		
		
		// download multiple models for a tracking number
		else {
			$zipName = $tracking . ".zip";
			$zip = new zipArchive();
			if($zip->open($zipName, ZIPARCHIVE::CREATE)){
				
				$validModels = true;
				if(isset($_REQUEST['models'])) {
					$modelIds = $_REQUEST['models'];
					//validate
					
					foreach ($modelIds as $modelId) {
						if(!$db->validModelId($modelId)) {
							$validModels = false;
						}
					}
				}
				if(!isset($_REQUEST['models']) || !$validModels) {
					$modelIds = $db->getModelIds($tracking);
				}
				
				//execute this if there are any models
				if((int)count($modelIds) > 0) {
					for($i = 0; $i<count($modelIds); $i++) {
						$file = $db->getFile($modelIds[$i]);			
						$zip->addFromString("tuned_$modelIds[$i].idf", $file);
						
					}

					$zip->close();
					$db->downloadFile($zipName);
					unlink($zipName);
				}
			}
		}
	}
}
else {
	// tracking was not given
}



?>