<?php
	//proxy is used for jquery load --> allows for remote requests to be made
	if(isset($_GET['url'])) {
		$url = urldecode($_GET['url']);
		echo file_get_contents($url);
	}
?>