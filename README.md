# Autotune
Automatic calibration methodology

Requirements:

Ubuntu, PHP 5, PHP MySQL, Python 2.7, Python suds, Energyplus 7.0 in default install location

Install steps:

* Install location assumes /var/www/html/autotune
* Grep for all locations of racoon.ornl.gov and replace with your domain name
* Get your Google maps API key and insert in frontend/selectingModelPage.php and frontend/iptolatlng.php
* Setup mysql database, user, and password, and create tables with autotune.sql
* Setup your mail server credentials in backend/autotune.py
