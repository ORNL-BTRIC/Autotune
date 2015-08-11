<!DOCTYPE html>
<html>
	<head>
		<title>Tracking Progress</title>
		
		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, minimum-scale=1" />
		
		<link type="text/css" rel="stylesheet" href="stylePractice2.css" />
		<link type="text/css" rel="stylesheet" href="mobile.css" />
		<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
		<link href="css/custom-theme/jquery-ui-1.10.2.custom.css" rel="stylesheet">  
		<script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script> 
		<script src="jquery/JQProgress.js"></script>
		<script src="jquery/JQHome.js"></script>
	</head>
	
	<body>
	
		<div id="logo">
			<a href="home.html"><img src="pictures/Logo.png"/></a>
		</div>
		<div class="inside">
			<div id="content">
				
				<?php		
					$tracking = $_GET['tracking'];

					echo "<h2>Tracking Number:<span id=\"modelNum\">$tracking</span></h2><br>";
					
					$url = "http://yourdomain.com/autotune/service/service.php?tracking=".$tracking;
					$output = file_get_contents($url);
					$xml = new SimpleXMLElement($output);
									
					$modelsAvail = count($xml->models->model) > 0; //true if there are no models available
				?>

				<div id="ajaxOutput"></div>
				<form  action="http://yourdomain.com/autotune/service/download.php" method="get">
					<div class="left">
					<?php if($modelsAvail):?>
						<div class="box">
						
							<h1> Downloading Models </h1>
							<p>The models below represent the best found so far by the Autotune process. The model's error compared to the supplied data is listed beside each model, and they are ordered from lowest to highest error (where the model with the lowest error is highlighted). Please check the box beside any model that you would like to download.</p>
							<hr>
							<?php
									
									//get model id's and fits
									$fit = array();
									for($i=0; $i<count($xml->models->model); $i++) {
										$fit[(int)$xml->models->model[$i]->id] = (float)$xml->models->model[$i]->fitness;
									
									}
									
									
									//sort by fit
									asort($fit);
									
									$first = true;
									echo "<table>";
									echo "<tr>
											<th></th>
											<th>Model Id</th>
											<th>Error</th>
										  </tr>";
									
									foreach($fit as $id=>$fitness) {
										$highlight = "";
										if($first) { //highlight the lowest(first) fitness/model
											$highlight = "class=\"highlight\"";
											$first = false;
										}
										echo "<tr $highlight><td><input type=\"checkbox\" name=\"models[]\" value=\"$id\" checked></td><td>$id</td><td>$fitness</td>";
									}
									echo "</table>";
									
							?>
						<a id="check" class="option" >Check All</a>/<a id="uncheck" class="option" >Uncheck All</a><br>
						<form id="trackingInfo">
							<input type="hidden" name="tracking" value="<?php echo $tracking; ?>" />
						</form>
						
							<input type="hidden" name="id" value="<?php echo $trackingNum; ?>">
							<br><input class="button left" type="submit" value="Download">
							<a class="button right" href="home.html">Home</a>
						
						</div>
					</form>
				</div>
				<div class="right">
				<?php endif; ?>	
					<h2>Additional Options</h3>
					<div id="accordion">
						<?php
							
							$disableStop = "";
							$disableResume = "";
							
							//get position
							$position = (int)$xml->position;
							$terminate = (int)$xml->terminate;
							if(!$terminate && $position >= 0) {
								$disableResume = 'style="display:none;"';
							}
							else {
								$disableStop = 'style="display:none;"';
							}
							
							 echo "<h3 class=\"stopOption\" $disableStop>Stop</h3>
								  <div class=\"stopOption\" $disableStop>
										<p> If you would like to stop your order, click here: <span id=\"stop\" class=\"button\">Stop</span> </p>
										
								  </div>";
							  
							 echo "<h3 class=\"resumeOption\" $disableResume>Resume</h3>
								  <div class=\"resumeOption\" $disableResume>
										<p> If you would like to resume or continue you order, click here:<span id=\"resume\" class=\"button\">Resume</span></p>
										<p>This option will continue to produce more results for your order.</p>
								  </div>";
							  
							 echo "<h3 class=\"retuneOption\">ReTune</h3>
								  <div class=\"retuneOption\">
										<p>If you would like to start the tuning process again with a new order, click here:<span id=\"retune\" class=\"button \">ReTune</span></p>
								  </div>";
						  
						  ?>
					</div>
					
				</div>
				
				<div id="dialog-modal" title="Confirmation">
					<div id="stopDialog">
						<p>Your order has been stopped</p>
					</div>
					<div id="resumeDialog">
						<p>Your order has been resumed</p>
					</div>
					<div id="retuneDialog">
						<h4>Reciept<h4>
						<p id="ajax"></p>
					</div>
				</div>
			</div>
		</div>
	</body>
</html>

