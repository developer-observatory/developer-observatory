#! Copyright (C) 2017 Christian Stransky
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.

from flask import Flask
from flask import request, redirect, make_response, jsonify
import json

app = Flask(__name__)

DB_HOST = "%landingURL%"
DB_URL = "{:s}/submit".format(DB_HOST)
user_data_file = "/home/jupyter/.instanceInfo"

def sendData(data):
    import urllib3
    from urllib3.util import Timeout
    
    #Ensure we have the correct data for this user
    try:
        with open(user_data_file) as data_file:    
            user_data = json.load(data_file)
            data["user_id"] = user_data["user_id"]
            data["token"] = user_data["token"]
    except Exception:
        pass

    https = urllib3.PoolManager()
    dataRaw = {}
    dataRaw['auth-token'] = "q9c(,}=C{mQD~)2#&t3!`fLQ3zk`9," # our client authentication, should be switched to a dynamic token
    dataRaw['json-payload'] = json.dumps(data).encode('utf-8')
    encoded_body = json.dumps(dataRaw).encode('utf-8')
    https.request('POST', DB_URL, headers={'Content-Type': 'application/json'}, body=encoded_body)

@app.route("/survey", methods=['GET'])
def forward_to_survey():
    '''
    User has finished, now redirect to the exit survey.
    '''
    try:
        with open(user_data_file) as data_file:    
            user_data = json.load(data_file)
            user_id = user_data["user_id"]
            token = user_data["token"]
            return redirect(DB_HOST+"/survey/"+user_id+"/"+token)
    except Exception:
        pass
    
@app.route("/submit", methods=['POST'])
def send_notebook():
    '''
    This function sends the participant code to the landing server.
    It also verifies that the JSON data is less than 1 MB to avoid unnecessary traffic by malicious users who could let the JSON file grow.
    '''
    if request.method == 'POST' and request.json:
        # check json size
        # only send, if size is less than 1 MB
        if len(request.json) < 1*1024*1024:
            sendData(request.json)
            return ""
        abort(400)
    else:
        abort(400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == "__main__":
    #app.debug = True
    app.run(host='127.0.0.1', port=6200)
