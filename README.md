# Autotune
Automatic optimization/calibration technology - applied to EnergyPlus building energy models for matching measured data.

**Directories:**
* [demo](demo) - quickest way to see Autotune run (uses 15-minute data)
* [installer](installer) - install scripts to setup Autotune web-service
* [frontend](frontend) - webpage for defining residential or medium office building and starting Autotune
* [backend](backend) - Autotune server that listens and processes new jobs
* [service](service) - web service for accepting new job requests
  * [example](service\example) - web service client for calling the web service (with example data files)

## Background
Building energy models (EnergyPlus, energy audit tools, etc.) of existing buildings are unreliable unless calibrated so they correlate well with actual energy usage. Calibrating models is costly because it is currently an “art”, requiring significant manual effort by an experienced, skilled professional. Manual tuning is also imperfect, non-repeatable, and non-transferable.

## Goals
Deploy a generalized, automated building energy model tuning methodology that enables models to reproduce measured data by selecting best-match input parameters in a systematic, automated, and repeatable fashion. In application, this aims to significantly reduce the costs to develop building energy models, enhance the cost-effectiveness of retrofit projects, and expand the market to smaller buildings. It also improves the state of the art in energy savings measurement and verification (M&V) for performance contracting, fault-detection and diagnostics (FDD), building automation, and related purposes.

## Scope
The related research addresses: multi-objective optimization, web services for easy integration with existing business processes, field-deployable systems, sensitivity analysis, quality assurance and control for missing or corrupt data, big data mining, a suite of machine learning algorithms to generate calibration functions, optimal calibration algorithm selection using high performance computing resources, quantified assessments of trade-offs between tuning accuracy and amount of data available, calibration using monthly data (12 points/year), demonstrations using research houses with 15-minute sensor channels (700,000 data points per year), and implementation of a testing methodology for quantifying accuracy of the final calibrated model to the real building. For more information on the research behind Autotune, please see http://bit.ly/autotune_papers.

# Quick Demonstrations

## Lean Windows Demo
This illustrates the basic Autotune calibration functionality in the quickest way possible and with a minimum amount of user effort. This demonstrates calibration of 303 parameters running only 16 EnergyPlus simulations, so a user shouldn't expect much of an improvement in error for this short demo.

* Windows operating system - desktops, laptops, netbooks
* [EnergyPlus 7.0](http://apps1.eere.energy.gov/buildings/energyplus/energyPlus_download.cfm?previous Legacy EnergyPlus 7.0)
* [Python 2.7](https://www.python.org/downloads/release/python-2710/ Python 2.7 Downloads)
  * Note - When selecting options, enable "Add python.exe to Path" at the bottom of the list
* Install inspyred
  * Open a command prompt (Start->cmd->enter)
  * `pip install inspyred`
* Run Autotune
  * Double-click demo\autotune.bat
  * This example will show results after each of 3 generations and completes in ~5 minutes.
  
## Larger demo on a virtual machine
This larger demo illustrates the full functionality of having Autotune running on a server as a web-service. A virtual machine of the setup is provided for getting up and running fairly quickly.

A fully functioning Ubuntu Linux Virtual Machine has been created with all dependencies to provide a quick demonstration of Autotune. Just VirtualBox and Vagrant are required to download and launch this image.
* Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](http://www.vagrantup.com/downloads.html)
* On a command line terminal, in a new directory of your choice, run
  * `vagrant init sanyalj/ornl-autotune`<br>
  This will create a Vagrantfile. Edit the Vagrantfile to add the following snippet within the `Vagrant.configure(2) do |config|` ... `end` section:
    ```
    # Config username
    config.ssh.username = "autotune"
  
    # start GUI
    config.vm.provider "virtualbox" do |v|
	  v.gui = true
    end
    ```
  * `vagrant up --provider virtualbox` <br>
  This will download the VM from Atlas (the new version of VagrantCloud) and then power up the instance with an Ubuntu GUI.
* TODO: Add steps to use the VM for demo
  
  
# Server Installations
These instructions are used to setup a machine so that Autotune can be invoked through the provided website and/or web service.

## Windows Server
Requirements:
* Windows operating system - we recommend installing on a centralized web server for widespread use as a web service
* [EnergyPlus 7.0](http://apps1.eere.energy.gov/buildings/energyplus/energyPlus_download.cfm?previous Legacy EnergyPlus 7.0)
* [PHP 5.x](http://windows.php.net/download#php-5.6 "PHP Downloads")
  * [Apache PHP](https://www.youtube.com/watch?v=6Y6lOHov3Bk "Example PHP install video")
  * [IIS PHP] (https://www.youtube.com/watch?v=3Q27FJYmpwQ "Example PHP install video")
* [Python 2.7](https://www.python.org/downloads/release/python-2710/ Python 2.7 Downloads)
* Python suds
  * Open a command prompt (Start->cmd->enter)
  * `pip install inspyred`
* MySQL

## Linux Server
Linux (Ubuntu example here), PHP 5.x, MySQL, Python 2.7, Python suds, Energyplus 7.0 in default install location

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

### Weather Files
1. Extract additional weather files to WeatherData directory of EnergyPlus
2. Download [WeatherData.tar.gz](http://elessar.ornl.gov/autotune_data/WeatherData.tar.gz "Weather Data")
2. `tar zxvf WeatherData.tar.gz`
3. `sudo mv WeatherData/* /usr/local/EnergyPlus-7-0-0/WeatherData/`

### MySQL settings
1. In `/etc/mysql/my.cnf`
  * `max_allowed_packet = 64M`
2. Underneath the [mysqld] section:
  * add `lower_case_table_names = 1`
3. Restart MySQL
  * `sudo /etc/init.d/mysql restart`

### PHP settings
1. In `php.ini`
2. `max_execution_time = 180`
3. `max_input_time = 180`
4. `post_max_size = 64M`
5. `upload_max_filesize = 64M`

### Setup the installation
1. Clone/export the git repo
2. Modify the `installer/install-settings.ini` to supply appropriate values 
3. Run `sudo python install.py`

### Permission changes
1. In the location of the autotune on the web-server:
2. `sudo chmod 777 backend`
3. `sudo chmod 777 frontend`
4. `sudo chmod 777 service`
5. `sudo chmod 777 backend/autotune.log`

### Create MySQL database
1. `mysql -u root -p`
2. `create database autotune;`
3. `create user 'autotune'@'%' identified by 'password';`
4. `grant all on autotune.* to 'autotune'@'%';`
5. `mysql -u root -p autotune < backend/autotune.sql`

## Example Test
1. To run the example in `service/example`
  * `python pyClient.py`
2. Web frontend:
  * Go to: `http://localhost/autotune/frontend/home.html`
