# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import datetime
import os
import requests
import sys

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
@app.route('/', methods=['GET'])
def banuhook():
    return("welcome thalaivi banu")
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    sys.stdout.flush()
    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req['result']['action'] != "bookappt":    
        return {}
    print(req['result']['action'],type(req['result']['action']))
    result = req.get("result")
    parameters = result.get("parameters")
    docname = parameters.get("doctor-name")
    apptday = parameters.get("appt-day")
    email = parameters.get("appt-email")
    
    data = {}
    #data['business_id'] = "100"
    data['business_name'] = docname
    data['customer_email'] = email
    data['customer_appointment_date'] = apptday
    json_data = json.dumps(data)
    
    print("Request Parsed,Success...")
    print("Sending JSON Data...")
    print(json_data)

    
    sys.stdout.flush()
    res = makeWebhookResult(json_data)
    return res

def makeWebhookResult(json_data):

   result = None
   res = None
   averagetime = None
    # print(json.dumps(item, indent=4))
   appturl = 'https://postgresheroku.herokuapp.com/update'
   headers = {'content-type': 'application/json'}
    
   print("JSON Data, Before requests.post")
   print(json_data)
    
   result = requests.post(appturl, data = json_data, headers=headers)
   res = json.loads(result.text)
    
   print('res',json.dumps(res, indent=4))
    
    # get wait time 
   if res.get('Message') is  "AlreadyExists":
         print("in if statement")
         speech = "You have already received Token.Token Number is :" + res.get('Token')
         print("in if statement")
   else:        
    averagetime = res.get('Average_Wait_Time')
    t=int(averagetime)*60
    day= t//86400
    hour= (t-(day*86400))//3600
    minit= (t - ((day*86400) + (hour*3600)))//60
    seconds= t - ((day*86400) + (hour*3600) + (minit*60))
    #print(hour,' hours', minit, 'minutes')
    avgwaittimeformat = hour,' hours', minit, 'minutes'
    print(avgwaittimeformat)
    
    business_hour_st = res.get('business_hour_start')
    business_hour_end = res.get('business_hour_end')
    break_st = res.get('breaktime_st')
    break_end = res.get('breaktime_end')
    business_add = res.get('business_address')
    print(business_hour_st)
    print(business_hour_end)
    print(break_st, break_end,business_add)
    
    print("in if statement")

    speech = "Appointment is confirmed! Your Token Number: " + res.get('Token') + ". Appx Wait Time: " + str(hour)+ " hr(s) " + str(minit) + " min(s) "  +  "Address:" + str(business_add)+" Business_hour:"+str(business_hour_st)+"-"+str(business_hour_end)+"."+"Break_Time:"+str(break_st)+"-"+str(break_end)
       #  speech = "Appointment is confirmed! Your Token Number: " + res.get('Token') + ". Appx Wait Time: " + str(hour)+ " hr(s) " + str(minit) + " min(s) "  
      
    print("Response:")
    print(speech)
    #sys.stdout.flush()

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
