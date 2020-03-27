#! Copyright (C) 2017 Christian Stransky
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.

from flask import Flask, redirect, request, make_response
from shutil import copyfile
import json
import requests
import os.path
import uuid
import urllib

app = Flask(__name__)

remote_task_file = "%landingURL%/get_ipynb/"
target_file = "/home/jupyter/tasks.ipynb"
user_data_file = "/home/jupyter/.instanceInfo"

@app.route('/')
def init():
    user_id = request.args.get('userId') 
    token = request.args.get('token')
    user_data = {}
    user_data["user_id"] = user_id
    user_data["token"] = token
    
    #Check if a task file already exists on this instance
    if not os.path.isfile(target_file):
        #If not, then request data for this user from the landing page
        task_file = urllib.request.URLopener()
        task_file.retrieve(remote_task_file+user_id+"/"+token, target_file)
        
    #Prepare the response to the client -> Redirect + set cookies for uid and token
    response = make_response(redirect('/nb/notebooks/tasks.ipynb'))
    response.set_cookie('userId', user_id)
    response.set_cookie('token', token)
    
    # Check if we already stored user data on this instance
    if not os.path.isfile(user_data_file):
        with open(user_data_file, "w") as f:
            #writing the data allows us to retrieve it anytime, if the user has cookies disabled for example.
            json.dump(user_data, f)
    return response

if __name__ == '__main__':
    #app.debug = True
    app.run(host='127.0.0.1', port=60000)
