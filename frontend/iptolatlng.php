<?php 
include('ip2locationlite.class.php');

$api_key = "yourapikey";
 
//Load the class
$ipLite = new ip2location_lite;
$ipLite->setKey($api_key);

$ip = $_SERVER["REMOTE_ADDR"];
$locations = $ipLite->getCity($ip);
if($ip == "127.0.0.1") {
    echo "35.9846572 -84.2957059";
}
else if(!empty($locations) && is_array($locations)) {
    echo $locations["latitude"] . " " . $locations["longitude"];
}
else {
    echo "unknown";
}
?>
