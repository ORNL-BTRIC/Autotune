<?php
	include "service.php";
	//SOAP
	//-----------------------------------------------------------------------------------

	ini_set("soap.wsdl_cache_enabled", "0"); // disabling WSDL cache
	$server = new SoapServer("autotune.wsdl");
	$functions = array("tune", "resume", "retune", "getOutput", "getFullOutput","getModel", "terminate");
	$server->addFunction($functions);
	$server->handle();


	//-----------------------------------------------------------------------------------
	
	/*
	tune($uData, $bModel, $schedule, $parameters, $weather, $email)
	-creates a new job in autotune. 
		Email can be given as an empty string.
		A string is returned in JSON format.
		Output includes the tracking and position of the new job"
		
		
	retune($tracking)	
	-creates a new job with the same initial inputs. Similar to restarting a tune with a new tracking.
		A string is return in JSON format. 
		Output includes the new tracking number and its position
		
	resume($tracking)
	-resumes the order until completed.
		A string is return in JSON format.
		Output includes tracking, position, terminate, runtime, model ids, and model fits	
		
	getOutput($tracking)
	-returns the default details about an order.
		A string is returned in JSON format.
		Output includes the tracking number, position, terminate, runtime, model ids, and corresponding model fits;

	getFullOutput($tracking)
	-returns the full details of an order.
		A string is returned in JSON format.
		Output includes tracking number, position, runtime, model ids, model fits, weather file, baseModel, parameters, schedule, userData, and model files

	getModel($tracking, $modelId)
	-returns information on a particular generated model.
		A string is returned in JSON format.
		Output includes tracking number, runtime, model id, model file, and model fit

	terminate($tracking)
	-sets the terminate field in the database. If true, the order will be stopped. If it is currently running, it will stop when it finishes with its current generation of models.
		A string is return in JSON format.
		Output includes tracking, position, terminate, runtime, model ids, and model fits

*/
?>