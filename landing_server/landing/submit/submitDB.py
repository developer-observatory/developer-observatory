#! Copyright (C) 2017 Christian Stransky
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.

from flask import Flask
from flask import request
from flask import make_response
from flask import jsonify
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
import datetime
import json

app = Flask(__name__)
app.config.from_object('configSubmitDB')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MAX_LENGTH = 1000000 #max length for json size

db = SQLAlchemy(app)

# Jupyter Notebook model
class Jupyter(db.Model):
    __tablename__ = 'jupyter'
    
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String())
    token = db.Column(db.String())
    code = db.Column(JSON)
    time = db.Column(JSON)
    status = db.Column(db.String(1)) # B: "Ok, got it!" button was hit, R: runing btn is hit, N: the next btn is hit, F: final submission
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, userid, token, code, time, status):
        self.userid = userid
        self.code = code
        self.time = time
        self.status = status
        self.token = token
    
    def __repr__(self):
        return '<User %s>' %{self.userid}

# createdInstances model
class CreatedInstances(db.Model):
    __tablename__ = "createdInstances"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String())
    ip = db.Column(db.String())
    time = db.Column(db.DateTime, default=db.func.current_timestamp())
    ec2instance = db.Column(db.String())
    category = db.Column(db.Integer)
    condition = db.Column(db.Integer)
    instanceid = db.Column(db.String())
    terminated = db.Column(db.Boolean)
    heartbeat = db.Column(db.DateTime, default=db.func.current_timestamp())
    instanceTerminated = db.Column(db.Boolean)

# conditions model
class Conditions(db.Model):
    __tablename__ = "conditions"
   
    category = db.Column(db.Integer, primary_key=True) 
    condition = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String())
    hash = db.Column(db.String())

# copy&paste code model
class CopyPastedCode(db.Model):
    __tableName__ = "copyPastedCode"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String())
    token = db.Column(db.String())
    tasknum = db.Column(db.String())
    cellid = db.Column(db.String())
    code = db.Column(db.String())
    time = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, userid, token, tasknum, cellid, code):
        self.userid = userid
        self.token = token
        self.tasknum = tasknum
        self.cellid = cellid
        self.code = code


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    
@app.route('/survey/<string:userid>/<string:token>')
def redirectToSurvey(userid, token):
    from flask import redirect
    import boto3

    row = CreatedInstances.query.filter_by(userid = userid).first()
    if row == None:
        return 'userid ' + userid + ' does not exist!'

    ec2 = boto3.resource('ec2')
    instanceid = [row.instanceid]
    
	# shut down the instance
    if row.terminated != 'true':
        try:
            ec2.instances.filter(InstanceIds=instanceid).terminate()
            row.terminated = 'true'
            db.session.commit()
        except Exception as e:
            print(e)

    url = "%finalSurveyURL%/?uid="+userid+"&tok="+token+"&newtest=Y"
    if(not (url.startswith("http://") or url.startswith("https://"))):
        url = "https://" + url
    return redirect(url, code=302)

@app.route('/submit', methods=['POST'])
def submit():
    data = json.loads(request.data)
    if data['auth-token'] == "q9c(,}=C{mQD~)2#&t3!`fLQ3zk`9,":
        try:
            jsonPayload = json.loads(data['json-payload'])
            if(len(jsonPayload) <= MAX_LENGTH):
                if (jsonPayload['type'] == 'pasted'):
                    row = CopyPastedCode(jsonPayload['user_id'], jsonPayload['token'], jsonPayload['tasknum'], jsonPayload['cellid'], jsonPayload['code'])
                    db.session.add(row)
                    db.session.commit()
                elif (jsonPayload['type'] == 'code'):
                    row = Jupyter(jsonPayload['user_id'], jsonPayload['token'], jsonPayload['code'], jsonPayload['time'], jsonPayload['status']) 
                    db.session.add(row)
                    db.session.commit()
            else:
                return "Input exceeded max length"
        except Exception as e:
            print(e)
            db.session.rollback()
            return "Error inserting json payload into database."
            
        return "Successfully inserted json payload into database."
    else:
        abort(400)        


if __name__ == '__main__':
    #app.debug = True
    app.run(host='127.0.0.1', port=6200)
