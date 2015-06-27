<?php



function getParamFileName($modelType) {
	$modelParam = array(
		'apartment'=>'SampleParameters.csv',
		'fullServiceRestaurant'=>'SampleParameters.csv',
		'hospital'=>'SampleParameters.csv',
		'largeHotel'=>'SampleParameters.csv',
		'large_office'=>'SampleParameters.csv',
		'medium_office'=>'MediumOffice.csv',
		'outPatient'=>'SampleParameters.csv',
		'primarySchool'=>'SampleParameters.csv',
		'quickServiceRestaurant'=>'SampleParameters.csv',
		'secondarySchool'=>'SampleParameters.csv',
		'smallHotel'=>'SampleParameters.csv',
		'small_office'=>'SampleParameters.csv',
		'standAloneRetail'=>'SampleParameters.csv',
		'stripMall'=>'SampleParameters.csv',
		'superMarket'=>'SampleParameters.csv',
		'warehouse'=>'SampleParameters.csv');
	$directory = 'parameters/';
	return $directory . $modelParam[$modelType];
}


?>