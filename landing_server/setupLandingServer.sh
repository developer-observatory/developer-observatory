#!/bin/bash
#! Copyright (C) 2017 Christian Stransky
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.


#Manual configurations go here

#URL to the exit survey
finalSurveyURL="<surveyUrl>"

#The amount of instances that can be started by a single IP.
dailyMaxInstances="2"
#The amount of participants that may start the study - Signing the consent form counts as starting
maxInstances="200"

#Register API keys at https://www.google.com/recaptcha/admin
#These are currently test keys that will pass any verifications.
recaptchaSiteKey='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
recaptchaSecret='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

#AWS Credentials
awsLang='en'
#Amazon access tokens
awsAccessKey=''
awsSecretKey=''
#Region to start the instances in: https://gist.github.com/neilstuartcraig/0ccefcf0887f29b7f240
awsRegion='us-east-1'

# AWS Settings for the task instance
awsImageId='ami-<id>'
#AWS instance types: https://aws.amazon.com/ec2/instance-types/
awsInstanceType='t2.nano'
awsSecurityGroupID='sg-<number>'
awsSshKeyName='SSH Gateway' #You should put your ssh key here, incase that you want to connect to the instances

poolSize="1"

#Dummy verifier, will always return Valid
tokenGetUrl="https://<domain>/dummyToken/gettoken"
tokenSetUrl="https://<domain>/dummyToken/settoken"



####################################################################
##Don't modify below this line, unless you know what you are doing##
####################################################################
taskfilesBasePath="$PWD/../task_generation/generated/"

RED='\033[1;31m'
NC='\033[0m' # No Color

prompt_confirm() {
  while true; do
    read -r -n 1 -p "${1:-Continue?} [y/n]: " REPLY
    case $REPLY in
      [yY]) echo ; return 0 ;;
      [nN]) echo ; return 1 ;;
      *) printf " ${RED} %s \n${NC}" "invalid input"
    esac 
  done  
}

finalSurveyUrlPlaceHolder="%finalSurveyURL%"
taskfilesBasePathPlaceholder="%taskFilesBasePath%"

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[LandingServer] This script must be run as root${NC}" 1>&2
   exit 1
fi

echo -e "${RED}[LandingServer] ------------------------------------------------------------${NC}"
echo -e "${RED}[LandingServer] ------------------------------------------------------------${NC}"
echo -e "${RED}[LandingServer] -- WARNING: This script will provision the landing server --${NC}"
echo -e "${RED}[LandingServer] --- Only run this script on a clean Ubuntu/Debian image  ---${NC}"
echo -e "${RED}[LandingServer] ------------------------------------------------------------${NC}"
echo -e "${RED}[LandingServer] ------------------------------------------------------------${NC}"

prompt_confirm "[LandingServer] Preparing this server to run as the landing server" || exit 0

echo "[LandingServer][apt] Updating package list"
apt-get -qq -y update
echo "[LandingServer][apt] Upgrading packages to latest version"
apt-get -qq -y upgrade

echo "[LandingServer][apt] Checking Webserver requirements"
if [ -x "$(command -v apache2)" ]; then
    echo '[LandingServer][apt] Found apache2 - uninstalling'
    apt-get -qq -y remove apache2
fi
if ! [ -x "$(command -v nginx)" ]; then
    echo '[LandingServer][apt] nginx not found - installing'
    apt-get -qq -y install nginx
fi

echo "[LandingServer][apt] Installing php7.0-fpm php-pgsql php-redis redis-server postgresql python3-flask-sqlalchemy python3-boto3 php-curl composer php-zip php-simplexml python3-psycopg2"
apt-get -qq -y install php7.0-fpm php-pgsql php-redis redis-server postgresql python3-flask-sqlalchemy python3-boto3 php-curl composer php-zip php-simplexml python3-psycopg2


#Generate Passwords for the database in the first run. Replace in the files directly
pwUser1=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
pwUser2=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
pwUser3=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
sed -i "s|%pwUser1%|$pwUser1|g" postgres/dbSchema.sql
sed -i "s|%pwUser1%|$pwUser1|g" landing/webpageConf/config.php
sed -i "s|%pwUser2%|$pwUser2|g" postgres/dbSchema.sql
sed -i "s|%pwUser2%|$pwUser2|g" landing/submit/configSubmitDB.py
sed -i "s|%pwUser3%|$pwUser3|g" postgres/dbSchema.sql
sed -i "s|%pwUser3%|$pwUser3|g" landing/submit/configGetCode.py

#Generate Tasks
#cd ../task_generation/
#python generateNotebooks.py
#cd ../landing_server/

#Import data to postgres
echo "[LandingServer] Importing data to database"
su postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname = 'notebook'\" | grep -q 1 || psql -c \"CREATE DATABASE notebook\""
su postgres -c "psql -f postgres/dbSchema.sql"
su postgres -c "psql -d notebook -f ../task_generation/generated/dbSchema.sql"

echo "[LandingServer] Checking if user 'flaskserver' exists"
user_exists=$(id -u flaskserver > /dev/null 2>&1; echo $?) 
if [ $user_exists == 1 ]; then
    #Create a system account for jupyter and disable logins
    user_created=$(adduser flaskserver --system --group --shell=/bin/false --disabled-login > /dev/null 2>&1; echo $?)
    if [ $user_created == 0 ]; then
        echo "[LandingServer] User 'flaskserver' created"
    else
        echo -e "${RED}[LandingServer] User 'flaskserver' could not be created - aborting"
        exit 1
    fi
else
    echo "[LandingServer] User 'flaskserver' already exists"
fi

#Copy files
echo "[LandingServer] Copying configuration files"
cp landing/submit/submitDB.py /usr/local/bin/submitDB.py
cp landing/submit/configSubmitDB.py /usr/local/bin/configSubmitDB.py
sed -i "s|$finalSurveyUrlPlaceHolder|$finalSurveyURL|g" /usr/local/bin/submitDB.py
cp landing/submit/submitDB.service /etc/systemd/system/submitDB.service
cp landing/submit/getCode.service /etc/systemd/system/getCode.service
cp landing/submit/getCode.py /usr/local/bin/getCode.py
sed -i "s|$taskfilesBasePathPlaceholder|$taskfilesBasePath|g" /usr/local/bin/getCode.py
cp landing/submit/configGetCode.py /usr/local/bin/configGetCode.py

cp -rfT landing/webpageConf/ /var/www/webpageConf/
sed -i "s|%dailyMaxInstances%|$dailyMaxInstances|g" /var/www/webpageConf/config.php
sed -i "s|%maxInstances%|$maxInstances|g" /var/www/webpageConf/config.php
sed -i "s|%recaptchaSiteKey%|$recaptchaSiteKey|g" /var/www/webpageConf/config.php
sed -i "s|%recaptchaSecret%|$recaptchaSecret|g" /var/www/webpageConf/config.php
sed -i "s|%awsLang%|$awsLang|g" /var/www/webpageConf/config.php
sed -i "s|%awsAccessKey%|$awsAccessKey|g" /var/www/webpageConf/config.php
sed -i "s|%awsSecretKey%|$awsSecretKey|g" /var/www/webpageConf/config.php
sed -i "s|%awsRegion%|$awsRegion|g" /var/www/webpageConf/config.php
sed -i "s|%awsImageId%|$awsImageId|g" /var/www/webpageConf/config.php
sed -i "s|%awsInstanceType%|$awsInstanceType|g" /var/www/webpageConf/config.php
sed -i "s|%awsSecurityGroupID%|$awsSecurityGroupID|g" /var/www/webpageConf/config.php
sed -i "s|%sshKeyName%|$awsSshKeyName|g" /var/www/webpageConf/config.php
sed -i "s|%poolSize%|$poolSize|g" /var/www/webpageConf/config.php
sed -i "s|%tokenGetUrl%|$tokenGetUrl|g" /var/www/webpageConf/config.php
sed -i "s|%tokenSetUrl%|$tokenSetUrl|g" /var/www/webpageConf/config.php


mkdir -p /home/flaskserver/.aws/
cp landing/submit/boto.conf /home/flaskserver/.aws/config
sed -i "s|%awsAccessKey%|$awsAccessKey|g" /home/flaskserver/.aws/config
sed -i "s|%awsSecretKey%|$awsSecretKey|g" /home/flaskserver/.aws/config
sed -i "s|%awsRegion%|$awsRegion|g" /home/flaskserver/.aws/config

cp -rfT landing/webpage/ /var/www/html/
cp -rfT landing/tools/ /var/www/tools/
cp nginx/defaultLandingServer /etc/nginx/sites-enabled/default
cp redis/redis.conf /etc/redis/redis.conf

#Get external dependencies
echo "[LandingServer] Installing composer dependencies"
cd /var/www/html/
composer require google/recaptcha "~1.1"
composer require aws/aws-sdk-php
composer install

#Enable service
echo "[LandingServer] Enabling services"
systemctl daemon-reload
systemctl enable submitDB
systemctl enable getCode

echo "[LandingServer] Starting services"
service submitDB stop
service submitDB start
service getCode stop
service getCode start
service nginx reload
service redis-server restart

#Color the terminal red for future connects to ensure that the user notices, that he is working on a live server
export PS1='\A \033[1;31m\u@landing-server\033[0m:\w\$ '
grep -q -F "export PS1='$PS1'" ~/.bashrc || echo "export PS1='$PS1'" >> ~/.bashrc
source ~/.bashrc
echo "[LandingServer] Ready"