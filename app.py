# coding=utf-8
from flask import Flask, render_template, request, session, jsonify, make_response, redirect as r
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt
from simplepam import authenticate
import asyncio
import time
from threading import Thread
import requests
import json
import os


import config as c

#badge reader sync with Meraki cameras

isConnected=False
i=0

def start_update_sessions_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def update_sessions_work():
    i=0
    global latestMessagesList
    while isConnected:
        #final loop getting updates on sessions
        latestMessagesList=[{'timestamp': "2019-01-24T09:53:18-06:00", 'state': "DISCONNECTED", 'userName': "looped-pc"+str(i), 'ipAddresses': "172.16.13.25", 'macAddress': "c4:b3:01:b7:42:d1"}, {'timestamp': "2019-01-24T09:53:18-06:00", 'state': "DISCONNECTED", 'userName': "user-pc", 'ipAddresses': "172.16.13.25", 'macAddress': "c4:b3:01:b7:42:d2"}, {'timestamp': "2019-01-24T09:53:18-06:00", 'state': "DISCONNECTED", 'userName': "user-pc", 'ipAddresses': "172.16.13.25", 'macAddress': "c4:b3:01:b7:42:d3"}]
        i=i+1
        print(i)
        time.sleep(3)

new_loop = asyncio.new_event_loop()
t = Thread(target=start_update_sessions_loop, args=(new_loop,))
t.start()


app = Flask(__name__)
app.secret_key = c.secret_key

bcrypt = Bcrypt(app)
auth = HTTPBasicAuth()

latestMessagesList=[{'timestamp': "2019-04-12T11:40:33-06:00", 'state': " ", 'UserID': "86543202", 'ipAddresses': " ", 'macAddress': " "},{'timestamp': "2019-04-12T11:32:33-06:00", 'state': " ", 'UserID': "86543201", 'ipAddresses': " ", 'macAddress': " "},{'timestamp': "2019-04-12T11:33:36-06:00", 'state': " ", 'UserID': "85063685", 'ipAddresses': " ", 'macAddress': " "}]

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



@app.route('/DoStart', methods=['POST'])
def startShowingSessions():
    global isConnected
    print(request.form)
    updatedMessagesList=[{'timestamp': "2019-01-24T09:53:18-06:00", 'state': "DISCONNECTED", 'userName': "user-pc", 'ipAddresses': "172.16.13.25", 'macAddress': "c4:b3:01:b7:42:d1"}, {'timestamp': "2019-01-24T09:53:18-06:00", 'state': "DISCONNECTED", 'userName': "user-pc", 'ipAddresses': "172.16.13.25", 'macAddress': "c4:b3:01:b7:42:d2"}, {'timestamp': "2019-01-24T09:53:18-06:00", 'state': "DISCONNECTED", 'userName': "user-pc", 'ipAddresses': "172.16.13.25", 'macAddress': "c4:b3:01:b7:42:d3"}]

    #testing with values sent from the HTML template
    primaryIPinput=request.form['primaryIPinput']

    primaryTimeStamp=request.form['primaryTimeStamp']

    pxGridServerCAinput=request.form['pxGridServerCAinput']
    pxGridServerCAKeyinput=request.form['pxGridServerCAKeyinput']
    deviceCertinput=request.form['deviceCertinput']
    clientNodeNameinput=request.form['clientNodeNameinput']

    print("primaryIPinput: ",primaryIPinput)
    print("pxGridServerCAinput: ",pxGridServerCAinput)
    print("pxGridServerCAKeyinput: ",pxGridServerCAKeyinput)
    print("deviceCertinput: ",deviceCertinput)
    print("clientNodeNameinput: ",clientNodeNameinput)

    isConnected=True

    value2="just some more test data"
    new_loop.call_soon_threadsafe(update_sessions_work)
    print("continued after starting thread!!")

    #Then return it to HTML

#    return jsonify({'status': 'OK', 'value2': value2});
    return render_template('main.html',result=updatedMessagesList)

@app.route('/DoStop', methods=['POST'])
def stopShowingSessions():
    global isConnected
    global latestMessagesList
    print(request.form)
    latestMessagesList=[{'timestamp': " ", 'state': " ", 'userName': " ", 'ipAddresses': " ", 'macAddress': " "}]
    isConnected=False

    #Then return it to HTML
#    return jsonify({'status': 'OK', 'value2': value2});
    return render_template('main.html',result=latestMessagesList)

@app.route('/DoResetSessions', methods=['POST'])
def doResetSessions():
    primaryTimeStamp=request.form['primaryTimeStamp']
    primaryUserID=request.form['primaryUserID']

    #Here we will bring up another form to reset sessions that have been selected

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