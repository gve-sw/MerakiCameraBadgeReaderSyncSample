# coding=utf-8
from flask import Flask, render_template, request, session, jsonify, make_response, redirect as r
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt
from simplepam import authenticate
import time
import requests
import json
import os


import config as c

#badge reader sync with Meraki cameras


app = Flask(__name__)
app.secret_key = c.secret_key

bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()

latestMessagesList=[{'timestamp': "2019-04-12T14:20:29-06:00", 'UserID': "85063715"}, {'timestamp': "2019-04-12T11:40:33-06:00", 'UserID': "86543202"},{'timestamp': "2019-04-12T11:32:33-06:00", 'UserID': "86543201"},{'timestamp': "2019-04-12T11:33:36-06:00",'UserID': "85063685"}]

@auth.verify_password
def verify_pw(username, password):
    return authenticate(str(username), str(password))

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/')
@auth.login_required
def main():
    global latestMessagesList
    global i
    return render_template('main.html',result=latestMessagesList)


@app.route('/DoRetrieveSnapshot', methods=['POST'])
def doRetrieveSnapshot():
    primaryTimeStamp=request.form['primaryTimeStamp']
    primaryUserID=request.form['primaryUserID']

    #Here we will bring up another form to show snapshots for badge in events selected

    print(request.form)
    print(primaryTimeStamp)
    print(primaryUserID)


    url = "https://api.meraki.com/api/v0/networks/L_578149602163689741/cameras/Q2BV-7E5Q-ZZ2X/snapshot"

    querystring = {"timestamp":primaryTimeStamp}

    meraki_key = os.environ.get('MERAKI_KEY', None)

    payload = ""
    headers = {
        'X-Cisco-Meraki-API-Key': meraki_key,
        'cache-control': "no-cache",
        'Postman-Token': "4b84ec0e-ed70-40fa-9603-fb56ce5f42d1"
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    print(response.text)
    theURLDict = json.loads(response.text)
    print(theURLDict["url"])

    #wait for the URL to be valid
    time.sleep(7)

    #Then return it to HTML
#    return jsonify({'status': 'OK', 'value2': value2});
    return render_template('screenshot.html',result=[theURLDict["url"],primaryUserID])

@app.route('/DoOK', methods=['POST'])
def goBackMain():
    print(request.form)
    global latestMessagesList

    #Then return it to HTML
#    return jsonify({'status': 'OK', 'value2': value2});
    return render_template('main.html',result=latestMessagesList)

if __name__ == "__main__":
	#app.run(threaded=True)
	app.run(host='0.0.0.0', port=5000)