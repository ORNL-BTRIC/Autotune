<?php 
include('ip2locationlite.class.php');

$api_key = "ENTER_YOUR_API_KEY";
 
//Load the class
$ipLite = new ip2location_lite;
$ipLite->setKey($api_key);

$ip = $_SERVER["REMOTE_ADDR"];
$locations = $ipLite->getCity($ip);
if($ip == "127.0.0.1") {
    echo "33 -86";
}
else if(!empty($locations) && is_array($locations)) {
    echo $locations["latitude"] . " " . $locations["longitude"];
}
else {
    echo "unknown";
}
?>
