<?php
	require 'mailto.php';

	function request($input, $default) {
		if(isset($_REQUEST[$input]) && $_REQUEST[$input] != "") {
			return $_REQUEST[$input];
		}
		else {
			return $default;
		}
	}
	$to = request('to', 'youremail');
	$from = request('from', 'Not_Given');
	$subject = request('subject', 'No_Subject');
	$message = request('body', 'No_Message');
	
	$fName = request('fName', '');
	$lName = request('lName', '');

	//add full name to message
	$message = "$message\r\n\r\n$fName $lName\r\n$from";
	
	//add additional information to subject
	$subject = "Autotune Website: $subject";

	if(mailto($to, $subject, $message, $from)){
		echo "Your message has been successfully submitted";
	}
	else {
		echo "An error occured with submission";
	}

?>
