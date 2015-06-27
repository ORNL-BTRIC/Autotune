<?php
	
	$tracking = $_GET["tracking"];
	
	// get queue position
	$url = "http://racoon.ornl.gov/autotune/service/service.php?tracking=" . $tracking;
	$output = file_get_contents($url); //get xml string
	$xml = new SimpleXMLElement($output);
	
	echo "<hr>";
	if($xml->error->code != "") {
		echo "<p>" . $xml->error->description . "</p>";
	}
	else {
		$pos = (int)$xml->position;
		$completed = ($pos < 0);
		$running = ($pos == 0);
		$waiting = ($pos > 0);
		
	
		$stopped = (int)$xml->terminate;
	
		if($completed) {
			echo "<p>Your order is finished!<p>";	
		}
		else if($running){
			//check if there are any models available
			echo "<p>Your order is currently running.</p>";
		}
		else if($stopped) {
			echo "<p>Your order has been stopped.</p>";
		}
		else if($waiting){
			//get queue position of the order
			echo "<p>";
			if($pos == 1) {
				echo "Your order is next to be processed.";
			}
			else if($pos > 20) {
				echo "Your order is waiting to be processed.";
			}
			else {
				echo "There are " . $pos . " orders ahead of yours.";
			}
			echo "</p>";
		}
		
		$modelsAvail = (count($xml->models->model) > 0);
		if($modelsAvail) {
			echo "<p>You have models available.<p>";
			echo '<p>If you would like to download your models, click here:<a href="trackingProgress.php?tracking=' . $tracking . '">Get models</a></p>';
		}
		else {
			echo '<p>You can view any options by clicking here:<a href="trackingProgress.php?tracking=' . $tracking . '">Options</a></p>';
		}
	}
?>
