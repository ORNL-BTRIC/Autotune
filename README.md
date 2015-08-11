# Autotune
Automatic calibration methodology

## Requirements:

Ubuntu, PHP 5, PHP MySQL, Python 2.7, Python suds, Energyplus 7.0 in default install location

## Install steps:

### Get prerequisites

1. `sudo apt-get install git`
2. sudo apt-get install lamp-server^ (it will prompt for mysql password)
3. sudo apt-get install php-soap
4. sudo apt-get install python-mysqldb
5. sudo apt-get install python-pip
6. sudo pip install inspyred
7. Install EnergyPlus, use default locations
`sudo ./SetEPlusV700036-lin.sh`

Use the correct password you obtained for this version of EnergyPlus

### Extract additional weather files to WeatherData directory of EnergyPlus
tar zxvf WeatherData.tar.gz

sudo mv WeatherData/* /usr/local/EnergyPlus-7-0-0/WeatherData/


### Modify MySQL settings
In /etc/mysql/my.cnf

max_allowed_packet = 64M

Underneath the [mysqld] section.add:

lower_case_table_names = 1

### Restart MySQL 
sudo /etc/init.d/mysql restart

### Create MySQL database
mysql -u root -p

create database autotune;

create user 'autotune'@'%' identified by 'password';

grant all on autotune.* to 'autotune'@'%';

mysql -u root -p autotune < backend/autotune.sql


### Modify PHP settings
In php.ini

max_execution_time = 180

max_input_time = 180

post_max_size = 64M

upload_max_filesize = 64M



### Setup the installation
Modify the installer/install-settings.ini to supply appropriate values 

Run sudo python install.py 

### Additional permission changes
In the location of the autotune on the web-server:

### Change directory permissions
sudo chmod 777 backend

sudo chmod 777 frontend

sudo chmod 777 service


The autotune.log has to be writable
sudo chmod 777 backend/autotune.log

### Example:
To run the example in /service/example

Run:

python pyClient.py





