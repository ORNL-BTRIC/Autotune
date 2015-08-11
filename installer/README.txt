sudo apt-get install git
sudo apt-get install lamp-server^

mysql password: autotune
root password: autotune
autotune user password: autotune


Need PHP SOAP
sudo apt-get install php-soap


Assume Python 2.7 is installed
sudo apt-get install python-pip
sudo pip install inspyred

Modify PHP and MySQL settings:
php.ini
max_execution_time = 180
max_input_time = 180
post_max_size = 64M
upload_max_filesize = 64M

my.ini
max_allowed_packet = 64M
lower_case_table_names = 1

The following three lines gave me an error; I skipped them.
innodb_buffer_pool_size = 64M
innodb_additional_mem_pool_size = 16M
innodb_log_file_size = 16M

Autotune needs case insensetive mysql tables:
Open terminal and edit /etc/mysql/my.cnf
sudo nano /etc/mysql/my.cnf
Underneath the [mysqld] section.add:
lower_case_table_names = 1
Restart mysql
sudo /etc/init.d/mysql restart


Install EnergyPlus, use default locations
sudo ./SetEPlusV700036-lin.sh

Extract additional weather files to WeatherData directory of EnergyPlus
tar zxvf WeatherData.tar.gz
sudo mv WeatherData/* /usr/local/EnergyPlus-7-0-0/WeatherData/

create mysql database, username and password
mysql -u root -p
create database autotune;
create user 'autotune'@'%' identified by 'password';
grant all on autotune.* to 'autotune'@'%';
mysql -u root -p autotune < backend/autotune.sql


Run installer/install.py after making requisite changes to install-settings.ini

Autotune needs MySQLDB
sudo apt-get install python-mysqldb

Change directory permissions
TODO: sudo chmod 777 backend

autotune.log needs to be writable
sudo chmod 777 autotune.log

To run the example in /service/example
Install suds
sudo apt-get install python-suds

Run:
python pyClient.py




