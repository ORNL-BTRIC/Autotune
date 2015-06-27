<?php
/*	ini_set('display_errors',1);
	ini_set('display_startup_errors',1);
	error_reporting(-1);

	$db = new AutotuneDb();
	
	$id = $db->getNewTracking("Hello", "world!");
echo $id;
	
	$array = $db->getInputFiles($id);
	foreach ($array as $key=>$door) {
		echo $key . " -> " . $door . "<br>";
	}
*/
	class AutotuneDb {
		
		private $user = "autotune";
		private $pass = "password";
		private $con;
		
		function __construct() {
		
			try {
				$this->con = new PDO('mysql:host=localhost;dbname=autotune', $this->user, $this->pass); // create a connection
			}
			catch(PDOException $e) { 
				print "Error - " . $e->getMessage();
			}
		}
		
		function newTrackingId() {
			$queue = $this->nextQueuePosition();
			$insert = $this->con->prepare("INSERT INTO  `Tracking` (  `queuePosition` ) VALUES ('$queue')");
			if(!$insert->execute()) {
				echo $insert->errorInfo()[2]; // print any errors
				return false;
			}
			$id = $this->con->lastInsertId();
			return $id;
		}
		
		function getNewTracking($modelFile, $userFile) { // creates a new tracking number 
			$id = $this->newTrackingId();	
			$input['baseModel'] = $modelFile;
			$input['userData'] = $userFile;
			$this->insertInputFile($id, $input);
		
			
			return $id;
		}
		
		function duplicate($tracking) { //dublicates an order by using the same information, but with a new tracking number and queue position. Returns new Tracking number
			
			$insert = $this->con->prepare("INSERT INTO  `Tracking` (`queuePosition`, `baseModel`, `schedule`, `userData` ) 
									SELECT `queuePosition`, `baseModel`, `schedule`, `userData`
									FROM `Tracking`
									WHERE `id` = $tracking");
			if(!$insert->execute()) {
				echo $insert->errorInfo()[2]; // print any errors
			}
			$id = $this->con->lastInsertId();
			$this->updateQueuePosition($id);
			
			return $id;
			
			
		}
		
		function nextQueuePosition() { // returns the next queue position in the orders
			$stmt = $this->con->prepare("SELECT MAX(`queuePosition`) AS queue
										FROM `Tracking` ");
			if(!$stmt->execute()) {
				echo "Could not get last queue position";
			}
			$row = $stmt->fetch(PDO::FETCH_ASSOC);
			$result = $row['queue'];
			if($result != null && $result > 0) {
				return $result+1;
			}
			else {
				return 1;
			}
		}
		
		function getQueuePosition($tracking) { // gets the queue position of an order
			return $this->get($tracking, "Tracking", 'queuePosition');
		}
		
		function updateQueuePosition($tracking) { // updates an order's queue position to the end of the queue
			$position = $this->nextQueuePosition();
			$set['queuePosition'] = $position;
			$where['id'] = $tracking;
			return $this->update("Tracking", $set, $where);
		}
		
		function setWeather($tracking, $str) {
			$set['weather'] = $str;
			$where['id'] = $tracking;
			return $this->update("Tracking", $set, $where);
		
		}
		
		function getWeather($tracking) {
			return $this->get($tracking, "Tracking", 'weather');
		}
		
		function setEmail($tracking, $str) {
			$set['email'] = $str;
			$where['id'] = $tracking;
			return $this->update("Tracking", $set, $where);
		
		}
		
		function getEmail($tracking) {
			return $this->get($tracking, "Tracking", 'email');
		}
		
		function setTerminate($tracking, $bool) { // sets terminate of an order to true/false
			if($bool) {
				$terminate = 1;
			}
			else {
				$terminate = 0;
			}
			$update = $this->con->prepare("UPDATE `Tracking` 
										SET `terminate` = $terminate
										WHERE `id` = '$tracking'");
			
			$success = $update->execute();
			if(!$success) {
				echo $update->errorInfo()[2] . "<br>";
			}
			return $success;
		}
		
		function getTerminate($tracking) {
			return $this->get($tracking, "Tracking", 'terminate');
		}
		
		function validTracking($trackNum) { // determines if argument is a valid tracking number
			$id = $this->get($trackNum, "Tracking", 'id');
			
			if($id != null) {
				return true;
			}
			else{
				return false;
			}
		}
		
		function getRuntime($tracking) {
			return $this->get($tracking, "Tracking", 'runtime');
		}
	
		function createMatch($tracking, $modelNum) { // creates a new tuple in trackingmodel using input values
		
			$insert = $this->con->prepare("INSERT INTO  `TrackingModel` (  `id`,`trackingId`,`modelId` ) 
									VALUES (NULL,'$tracking','$modelNum' )");
			if(!$insert->execute()) {
				echo $insert->errorInfo()[2]; // print any errors
			}
			$id = $this->con->lastInsertId();
			return $id;
		}
		
		function getModelIds($trackNum) { //returns an array of corresponding model ids
			$stmt = $this->con->prepare("SELECT `modelId`
										FROM `TrackingModel`
										WHERE `trackingId` = '$trackNum'");
			$stmt->execute();
			$array = array();
			for($i=0; $row = $stmt->fetch(PDO::FETCH_ASSOC); $i++) {
				$array[$i] = $row["modelId"];
			}
			
			return $array;
			
		}
		
		function modelsAvail($trackNum) { //returns a boolean
			$array = $this->getModelIds($trackNum);
			return !empty($array);
		
		}
	
		function insertInputFile($id, $inputFile) { // parameter - associative array with (db field name) => (File string)
												// returns true on success, and false on failure
												// multiple files can be inserted, but no insertion will be made if there is ANY failure
			$inputs = array("baseModel"=>"model.idf", "parameters"=>"param.csv", "schedule"=>"sched.csv", "userData"=>"udata.csv");
			$zip = new ZipArchive();
			
			
			$zipName = "insertInputFiles".$id.".zip";
			foreach ($inputFile as $field=>$file) {
			
				$zippedContents = $this->zipFile($file, $inputs[$field], $id);
				$zippedFiles[$field] = $zippedContents;
				
			}
			
			$where['id'] = $id;
			return $this->update("Tracking", $zippedFiles, $where);
			
		}	
		
		function insertFile($id, $file, $fit) { // inserts a file and fitness into Model, returns the id
		
			$zippedFile = $this->zipFile($file, "tuned.idf", $id);
			
			$insert = $this->con->prepare("INSERT INTO `Model` (`file`,`fit`)
									VALUES ('$zippedFile','$fit')");
			
			if(!$insert->execute()) {
				echo $insert->errorInfo()[2] . "<br>";
			}
			
			$id = $this->con->lastInsertId();
			return $id;
		}
		
		function getInputFiles($id) { // returns an associative array with input file contents
			// all inputs Autotune will be retrieving
			$inputs = array("baseModel", "parameters", 
							"schedule", "userData");
			$fileNames = array("model.idf", "param.csv", "sched.csv", "udata.csv");
			$output = array();
			
			for($i=0; $i<count($inputs); $i++) {
				$data = $this->get($id, "Tracking", $inputs[$i]);
				
				$str = $this->unzipFile($data, $fileNames[$i], $id);
				$output[$inputs[$i]] = $str;
			}
			return $output;
		}
	
		function getFile($id) { // retrieves the file from Model and returns its contents
			$file = $this->get($id, "Model", "file");
			$str = $this->unzipAndRename($file, "tuned.idf", "tuned_$id.idf", $id);
			return $str;
		}
		
		function validModelId($id) { // determines if argument is a valid tracking number
			$mId = $this->get($id, "Model", 'id');
			if($mId != null) {
				return true;
			}
			else{
				return false;
			}
		}
		
		function getFit($id) { // Returns the fit of a Model
			$stmt = $this->con->prepare("SELECT `fit`
										FROM `Model`
										WHERE `id` = '$id'");
			$stmt->execute();
			$row = $stmt->fetch(PDO::FETCH_ASSOC);
			return $row['fit'];
		}
			
		function downloadFile($filename) { // Downloads file from specified filePath
	
			// What type of file we are outputing
			header('Content-type: application/zip'); // .idf
			// What to call the downloaded file
			header("Content-Disposition: attachment; filename=" . basename("$filename"));
			//header('Content-Length: '.filesize($filename));
		
			
			readfile($filename);
			
			
		}
		
		function get($id, $table, $attr) { //only returns one item, do not use if query will return multiple items -> use getArray
			$array = $this->getArray($id, $table, $attr);
			return $array[0];
		}
		
		function getArray($id, $table, $attr) {
			$stmt = $this->con->prepare("SELECT `$attr`
										FROM `$table`
										WHERE `id` = $id");
			if(!$stmt->execute()) {
				echo "Could not get $attr";
			}
						
			$array = array();
			$row = $stmt->fetch(PDO::FETCH_ASSOC);
			$array[0] = $row["$attr"]; // make sure to get the first item if it is null
			for($i=1; $row = $stmt->fetch(PDO::FETCH_ASSOC); $i++) {
				$array[$i] = $row["$attr"];
			}
			
			return $array;
		
		}
		
		function update($table, $set, $where) { //set and where are associative arrays where key=>value in array is key = value in query
			$sql = "";
			foreach ($set as $attr=>$value) {
				$sql .= ",`$attr` = '$value'";
			}
			$setSql = substr($sql, 1); //take out the first comma, it is not needed in the sql
			
			$sql = "";
			foreach ($where as $attr=>$value) {
				$sql .= ",`$attr` = '$value'";
			}
			$whereSql = substr($sql, 1); //take out the first comma, it is not needed in the sql
			$update = $this->con->prepare("UPDATE `$table` 
										SET $setSql
										WHERE $whereSql");
			$success = $update->execute();
			if(!$success) {
				echo $update->errorInfo()[2] . "<br>";
			}
			return $success;
		}
		
		function zipFile($fileContents, $fileName, $id) {
			$zip = new ZipArchive();
			
			$zipName = substr($fileName, 0, -4) . "_$id.zip";
			if($zip->open($zipName, ZIPARCHIVE::CREATE)){
				
				$zip->addFromString($fileName, $fileContents);
				
				$zip->close();
			}
			else {
				echo "Could not create file<br>";
			}
			$file = addslashes(fread(fopen($zipName, "r"), filesize($zipName)));
			unlink($zipName);
			
			return $file;
		}
		
		function unzipFile($fileContents, $fileName ,$id) {
		
			return $this->unzipAndRename($fileContents, $fileName, $fileName, $id);
		}
		
		function unzipAndRename($fileContents, $fileName, $newFileName, $id) {
			$zipName = substr($fileName, 0, -4) . "_$id.zip";
			file_put_contents($zipName, $fileContents);
			$zip = new ZipArchive();
			
			$dir = "filesFolder";
			if($zip->open($zipName)) {
				$zip->extractTo($dir);
				$zip->close();
			}
			else {
				echo "Unable to open zip file";
			}
			
			
			rename("$dir/$fileName", "$dir/$newFileName");
			$str = @file_get_contents("$dir/$newFileName");
			if ($str != null) {
				unlink("$dir/$newFileName");
				
			}
				
			unlink($zipName);
			return $str;
		}
	
		function __destruct() { //destroys class and ends connection
			$con = null;
		}
	}
