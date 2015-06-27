<?php
	function mailto($to, $subject, $message, $from) {//multiple headers can be inserted into $from -> "[from address]\r\nReply-To:[reply-to address]\r\n..."
		$headers = "From: $from";//multiple headers must be separated by '\r\n'
			
		//allow periods at beginning of sentence
		$message = str_replace("\n.", "\n..", $message);

		//ensure that all carriage returns are \r\n
		$message = str_replace("\r", "", $message);//take out all \r instances
		$message = str_replace("\n", "\r\n", $message);//replace all \n with \r\n
		
		//wordwrap to ensure that width does not exceed 70
		$message = wordwrap($message, 70, "\r\n");		
		
		return mail($to, $subject, $message, $headers);
	}
?>