# Autotune
Automatic calibration technology - applied to EnergyPlus building energy models for matching measured data.

[demo](demo) - quickest way to see Autotune run
[installer](installer) - install scripts to setup Autotune web-service
[frontend](frontend) - webpage for defining residential or medium office building and starting Autotune
[backend](backend) - Autotune server that listens and processes new jobs
[service](service) - web service for accepting new job requests
[example](service\example) - web service client for calling the web service (with example data files)

## Background
Building energy models (EnergyPlus, energy audit tools, etc.) of existing buildings are unreliable unless calibrated so they correlate well with actual energy usage. Calibrating models is costly because it is currently an “art”, requiring significant manual effort by an experienced, skilled professional. Manual tuning is also imperfect, non-repeatable, and non-transferable.

## Goals
Deploy a generalized, automated building energy model tuning methodology that enables models to reproduce measured data by selecting best-match input parameters in a systematic, automated, and repeatable fashion. In application, this aims to significantly reduce the costs to develop building energy models, enhance the cost-effectiveness of retrofit projects, and expand the market to smaller buildings. It also improves the state of the art in energy savings measurement and verification (M&V) for performance contracting, fault-detection and diagnostics (FDD), building automation, and related purposes.

## Scope
The related research addresses: multi-objective optimization, web services for easy integration with existing business processes, field-deployable systems, sensitivity analysis, quality assurance and control for missing or corrupt data, big data mining, a suite of machine learning algorithms to generate calibration functions, optimal calibration algorithm selection using high performance computing resources, quantified assessments of trade-offs between tuning accuracy and amount of data available, calibration using monthly data (12 points/year), demonstrations using research houses with 15-minute sensor channels (700,000 data points per year), and implementation of a testing methodology for quantifying accuracy of the final calibrated model to the real building. For more information on the research behind Autotune, please see http://bit.ly/autotune_papers.

# Windows Demonstration

* Windows operating system - desktops, laptops, netbooks
* [EnergyPlus 7.0](http://apps1.eere.energy.gov/buildings/energyplus/energyPlus_download.cfm?previous Legacy EnergyPlus 7.0)
* [Python 2.7](https://www.python.org/downloads/release/python-2710/ Python 2.7 Downloads]
  * Note - When selecting options, enable "Add python.exe to Path" at the bottom of the list
* Install inspyred
  * Open a command prompt (Start->cmd->enter)
  * Type "pip install inspyred"
* Run Autotune
  * Double-click AT_DEMO\Autotune.bat

# Installation

## Windows Server
Requirements:

* Windows operating system - we recommend installing on a centralized web server for widespread use as a web service
* [EnergyPlus 7.0](http://apps1.eere.energy.gov/buildings/energyplus/energyPlus_download.cfm?previous Legacy EnergyPlus 7.0)
* [PHP 5.x](http://windows.php.net/download#php-5.6 "PHP Downloads")
  * [Apache PHP](https://www.youtube.com/watch?v=6Y6lOHov3Bk "Example PHP install video")
  * [IIS PHP] (https://www.youtube.com/watch?v=3Q27FJYmpwQ "Example PHP install video")
* MySQL
* Python 2.7
* Python suds

Install steps:

* Install location assumes /var/www/html/autotune
* Grep for all locations of racoon.ornl.gov and replace with your domain name
* Get your Google maps API key and insert in frontend/selectingModelPage.php and frontend/iptolatlng.php
* Setup mysql database, user, and password, and create tables with autotune.sql
* Setup your mail server credentials in backend/autotune.py

## Linux Server
Requirements:

Linux (instructions below are for Ubuntu), [PHP 5.x](http://windows.php.net/download#php-5.6 "PHP Downloads"), MySQL, Python 2.7, Python suds, EnergyPlus 7.0 in default install location

Install steps:

* Install location assumes /var/www/html/autotune
* Grep for all locations of racoon.ornl.gov and replace with your domain name
* Get your Google maps API key and insert in frontend/selectingModelPage.php and frontend/iptolatlng.php
* Setup mysql database, user, and password, and create tables with autotune.sql
* Setup your mail server credentials in backend/autotune.py


# Autotune
Automatic calibration methodology

## Requirements

Ubuntu, PHP 5, PHP MySQL, Python 2.7, Python suds, Energyplus 7.0 in default install location

## Install steps

### Get prerequisites

1. `sudo apt-get install git`
2. `sudo apt-get install lamp-server^` (it will prompt for mysql password)
3. `sudo apt-get install php-soap`
4. `sudo apt-get install python-mysqldb`
5. `sudo apt-get install python-pip`
6. `sudo apt-get install python-numpy`
7. `sudo pip install inspyred`
8. Install EnergyPlus, use default locations
	`sudo ./SetEPlusV700036-lin.sh`
	Use the password you obtained for this version of EnergyPlus

### Extract additional weather files to WeatherData directory of EnergyPlus
`tar zxvf WeatherData.tar.gz`

`sudo mv WeatherData/* /usr/local/EnergyPlus-7-0-0/WeatherData/`


### Modify MySQL settings
In `/etc/mysql/my.cnf`

`max_allowed_packet = 64M`

Underneath the [mysqld] section.add:

`lower_case_table_names = 1`

### Restart MySQL 
`sudo /etc/init.d/mysql restart`


### Modify PHP settings
In `php.ini`

`max_execution_time = 180`

`max_input_time = 180`

`post_max_size = 64M`

`upload_max_filesize = 64M`



### Setup the installation
Clone/export the git repo

Modify the `installer/install-settings.ini` to supply appropriate values 

Run `sudo python install.py`

### Additional permission changes
In the location of the autotune on the web-server:

### Change directory permissions
`sudo chmod 777 backend`

`sudo chmod 777 frontend`

`sudo chmod 777 service`


The autotune.log has to be writable
`sudo chmod 777 backend/autotune.log`

### Create MySQL database
 
`mysql -u root -p`

`create database autotune;`

`create user 'autotune'@'%' identified by 'password';`

`grant all on autotune.* to 'autotune'@'%';`

`mysql -u root -p autotune < backend/autotune.sql`

## Example:
To run the example in `service/example`

Run:

`python pyClient.py`

Web frontend:

Go to: `http://localhost/autotune/frontend/home.html`

