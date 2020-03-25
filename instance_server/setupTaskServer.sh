#!/bin/bash

#! Copyright (C) 2017 Christian Stransky
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.

#URL of the landing server - You should use HTTPS in any case!
#Don't use a slash at the end
landingURL="https://<URL>"

#This URL will be opened in a window, if a participants decides to skip a task
skippedTaskSurveyURL="https://<URL>"

#The amount of tasks in your task files.
taskCount="3"

####################################################################
##Don't modify below this line, unless you know what you are doing##
####################################################################
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

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[TaskInstance] This script must be run as root${NC}" 1>&2
   exit 1
fi

echo -e "${RED}[TaskInstance] ------------------------------------------------------------${NC}"
echo -e "${RED}[TaskInstance] ------------------------------------------------------------${NC}"
echo -e "${RED}[TaskInstance] --- WARNING: This script will provision the task server  ---${NC}"
echo -e "${RED}[TaskInstance] --- Only run this script on a clean Ubuntu/Debian image  ---${NC}"
echo -e "${RED}[TaskInstance] ------------------------------------------------------------${NC}"
echo -e "${RED}[TaskInstance] ------------------------------------------------------------${NC}"

prompt_confirm "[TaskInstance] Preparing this server to run as an instance of the task server" || exit 0

urlPlaceHolder="%landingURL%"
skippedUrlPlaceHolder="%skippedTaskSurveyURL%"
taskCountPlaceHolder="%taskCount%"

echo "[TaskInstance][apt] Updating package list"
apt-get -qq -y update
echo "[TaskInstance][apt] Upgrading packages to latest version"
apt-get -qq -y upgrade

echo "[TaskInstance][apt] Checking Webserver requirements"
if [ -x "$(command -v apache2)" ]; then
    echo '[TaskInstance][apt] Found apache2 - uninstalling'
    apt-get -qq -y remove apache2
fi
if ! [ -x "$(command -v nginx)" ]; then
    echo '[TaskInstance][apt] nginx not found - installing'
    apt-get -qq -y install nginx
fi

echo "[TaskInstance][apt] Installing pip3, python3-flask, python3-requests from apt"
apt-get -qq -y install python3-pip python3-flask python3-requests
echo "[TaskInstance][pip] Upgrading pip3 to latest version"
pip3 install --quiet --upgrade pip
echo "[TaskInstance][pip] Installing jupyter"
pip3 install --quiet jupyter

echo "[TaskInstance] Checking if user 'jupyter' exists"
user_exists=$(id -u jupyter > /dev/null 2>&1; echo $?) 
if [ $user_exists == 1 ]; then
    #Create a system account for jupyter and disable logins
    user_created=$(adduser jupyter --system --group --shell=/bin/false --disabled-login > /dev/null 2>&1; echo $?)
    if [ $user_created == 0 ]; then
        echo "[TaskInstance] User 'jupyter' created"
    else
        echo -e "${RED}[TaskInstance] User 'jupyter' could not be created - aborting"
        exit 1
    fi
else
    echo "[TaskInstance] User 'jupyter' already exists"
fi

echo "[TaskInstance][apt] Installing additional packages"
#Let's install some libs for our participants
apt-get -qq -y install $(cat apt-additional-packages.txt)

echo "[TaskInstance][pip] Installing additional packages"
pip3 install -r pip-additional-packages.txt

echo "[TaskInstance] Stopping services..."
service jupyter stop
service jupyterSubmit stop
service jupyterStartpage stop

#Generate Tasks
#echo "[TaskInstance] Generating task files..."
#cd task-generation
#python generateNotebooks.py
#cd ..

#Copy files
echo "[TaskInstance] Copying service files..."
cp services/jupyter.service /etc/systemd/system/jupyter.service
cp services/jupyterSubmit.service /etc/systemd/system/jupyterSubmit.service
cp services/jupyterStartpage.service /etc/systemd/system/jupyterStartpage.service
cp services/startpage.py /usr/local/bin/jupyterStartpage.py
cp services/submit.py /usr/local/bin/jupyterSubmit.py
sed -i "s|$urlPlaceHolder|$landingURL|g" /usr/local/bin/jupyterStartpage.py
sed -i "s|$urlPlaceHolder|$landingURL|g" /usr/local/bin/jupyterSubmit.py

echo "[TaskInstance] Copying task related files..."
#Copy files required for a certain task
#cp task-generation/base/db.sqlite /home/jupyter/db.sqlite

#Ensure the jupyter folder exists
mkdir -p /home/jupyter/.jupyter/custom/
mkdir -p /home/jupyter/.jupyter/nbconfig/

#Change ownership of the jupyter folder to the jupyter user, otherwise jupyter won't be able to start
chown -R jupyter:jupyter /home/jupyter
cp template/custom.js /home/jupyter/.jupyter/custom/custom.js
sed -i "s|$urlPlaceHolder|$landingURL|g" /home/jupyter/.jupyter/custom/custom.js
sed -i "s|$skippedUrlPlaceHolder|$skippedTaskSurveyURL|g" /home/jupyter/.jupyter/custom/custom.js
sed -i "s|$taskCountPlaceHolder|$taskCount|g" /home/jupyter/.jupyter/custom/custom.js
cp template/custom.css /home/jupyter/.jupyter/custom/custom.css
cp template/nbconfig/notebook.json /home/jupyter/.jupyter/nbconfig/notebook.json

cp template/notebook.html /usr/local/lib/python3.6/dist-packages/notebook/templates/notebook.html
cp config/jupyter_notebook_config.py /home/jupyter/.jupyter/jupyter_notebook_config.py
cp config/nginxTaskServer.conf /etc/nginx/sites-enabled/default

echo "[TaskInstance] Enabling services"
#Enable service
systemctl daemon-reload
systemctl enable jupyter
systemctl enable jupyterSubmit
systemctl enable jupyterStartpage
echo "[TaskInstance] Starting services"
service jupyter start
service jupyterSubmit start
service jupyterStartpage start
service nginx reload
export PS1='\A \u@task-server:\w\$ '
grep -q -F "export PS1='$PS1'" ~/.bashrc || echo "export PS1='$PS1'" >> ~/.bashrc
source ~/.bashrc
echo "[TaskInstance] Ready"