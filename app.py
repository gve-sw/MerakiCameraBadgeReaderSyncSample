# coding=utf-8
"""
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
from flask import Flask, render_template, request, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt
from simplepam import authenticate
import time
import requests
import json


import config as c

#badge reader sync with Meraki cameras


app = Flask(__name__)
app.secret_key = c.secret_key

bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()

sampleBadgeReaderEvents=[{'timestamp': "2019-04-12T14:20:29-06:00", 'UserID': "85063715"},
                         {'timestamp': "2019-04-12T11:40:33-06:00", 'UserID': "86543202"},
                         {'timestamp': "2019-04-12T11:32:33-06:00", 'UserID': "86543201"},
                         {'timestamp': "2019-04-12T11:33:36-06:00",'UserID': "85063685"}]

@auth.verify_password
def verify_pw(username, password):
    return authenticate(str(username), str(password))

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/')
@auth.login_required
def main():
    global sampleBadgeReaderEvents
    global i
    return render_template('main.html',result=sampleBadgeReaderEvents)


@app.route('/DoRetrieveSnapshot', methods=['POST'])
def doRetrieveSnapshot():
    primaryTimeStamp=request.form['primaryTimeStamp']
    primaryUserID=request.form['primaryUserID']

    #Here we will bring up another form to show snapshots for badge in events selected
    url = "https://api.meraki.com/api/v0/networks/"+c.meraki_network+"/cameras/"+c.camera_serial+"/snapshot"

    querystring = {"timestamp":primaryTimeStamp}

    payload = ""
    headers = {
        'X-Cisco-Meraki-API-Key': c.meraki_key,
        'cache-control': "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    print("response: ", response)
    print("response.text: ", response.text)
    theURLDict = json.loads(response.text)
    print("the URL: ",theURLDict["url"])

    #wait for the URL to be valid
    time.sleep(7)

    #Then return it to HTML
    return render_template('screenshot.html',result=[theURLDict["url"],primaryUserID])

@app.route('/DoOK', methods=['POST'])
def goBackMain():
    print(request.form)
    global sampleBadgeReaderEvents

    #Then return it to HTML
    return render_template('main.html',result=sampleBadgeReaderEvents)

if __name__ == "__main__":
	#app.run(threaded=True)
	app.run(host='0.0.0.0', port=5000,debug=True)