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
from functools import wraps
from flask import redirect, request, current_app


app = Flask(__name__)
app.config.from_object('configGetCode')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MAX_LENGTH = 1000000 #max length for json size
NUM_RETRY = 5 # retry to fetch
TASKFILES_BASE_PATH = "%taskFilesBasePath%"


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

class Invites(db.Model):
    """ Model for invited email addresses """
    __tablename__ = "invites"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    invited = db.Column(db.DateTime, nullable=True)
    blacklisted = db.Column(db.DateTime, nullable=True)
    bounced = db.Column(db.Boolean, nullable=True)
    pinged = db.Column(db.Integer, default=0)

    def __init__(self, emailid, email, token, invited, blacklisted, bounced, pinged):
        self.id = emailid
        self.email = email
        self.token = token
        invited = invited
        blacklisted = blacklisted
        bounced = bounced
        pinged = pinged

class CreatedInstances(db.Model):
    """ Model for created AWS instances """
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

class Conditions(db.Model):
    """ Model for conditions """
    __tablename__ = "conditions"
    category = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String())
    hash = db.Column(db.String())
    
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    
class CopyPastedCode(db.Model):
    """ Model for storage of copy and pasted code """
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


@app.route('/getcode/<string:userid>/<string:token>')
def getcode(userid, token):
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter

    row = Jupyter.query.filter_by(userid = userid).filter_by(token = token).filter_by(status = 'f').first()
    if row == None:
        return "NotFound"
    code = {}
    for cell in row.code['cells']:
        if cell['cell_type'] == 'code':
            tasknum =  cell['metadata'].get('tasknum')
            if tasknum == None:
                continue
            plain_code = cell['source']
            highlighted_code = highlight(plain_code, PythonLexer(), HtmlFormatter())
            code['code'+tasknum] = highlighted_code
    callback = request.args.get('callback', False)
    if callback:
        content = str(callback) + '(' + str(json.dumps(code)) + ')'
        return current_app.response_class(content, mimetype='application/json')

    return json.dumps(code)

    
# Retrieve latest ipynb for the user from the DB.
# Or if new user, then return default task file.
@app.route('/get_ipynb/<string:userid>/<string:token>')
def get_ipynb(userid, token):
    row = Jupyter.query.filter_by(userid = userid).filter_by(token = token).order_by(Jupyter.id.desc()).first()
    if row == None:
        user_row = CreatedInstances.query.filter_by(userid = userid).first()
        condition_row = Conditions.query.filter_by(condition = user_row.condition).first()
        with open(TASKFILES_BASE_PATH+condition_row.filename) as file:
            return file.read()
        
    return json.dumps(row.code)


if __name__ == '__main__':
    #app.debug = True
    app.run(host='127.0.0.1', port=6201)
