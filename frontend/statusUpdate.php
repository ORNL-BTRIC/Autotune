<?php
	
	$tracking = $_GET['trackingId'];
	$url = "http://racoon.ornl.gov/autotune/service/service.php?tracking=".$tracking;
	$output = file_get_contents($url);
	$xml = new SimpleXMLElement($output);
	
	$pos = $xml->position;
	if($pos < 0) {
		$status = "Finished";
	}
	else if($pos == 0) {
		$status = "Running";
	}
	else {
		$status = "Waiting";
	}
	echo $status;

?>
