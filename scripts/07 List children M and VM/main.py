#!/usr/bin/env python3
# Note: pip install requests
import json, requests, sys, time, os
from datetime import datetime, timedelta
from dateutil import tz

argv = list(sys.argv)
argv.extend((None, None,))

# == Settings ==
#                        This is just a sample! Arguments below in the endpoint call has to be modified accordingly!
# Authentication
API_USERNAME = argv[1] or os.environ.get('C4_USER', '')
API_PASSWORD = argv[2] or os.environ.get('C4_PASS', '')
# API root URI
API_URL_BASE = 'https://test.metering.space/api/'
# API call origin and referer
ORIGIN = API_URL_BASE
# Parameters
COMMUNICATION_PATH_ID = 107171
# ==============

class ConvergeSession:
    # The class implements session.

    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json',
                        'Referer': ORIGIN,
                        'Origin': ORIGIN}

    def Login(self, username, password):
        content = {'userName': username, 'password': password}
        response = requests.post(self.base_url + 'login/user-login', headers=self.headers, json=content)
        if response.status_code != 200:
            raise Exception("Authentication has failed.")
        self.headers['Authorization'] = 'Bearer %s' % json.loads(response.content.decode('utf-8'))['token']

class Main(ConvergeSession):
    # The main script method used below

    def __init__(self, *args, **kwagrs):
        super().__init__(*args, **kwagrs)

    def GetMeters(self, communication_path_id):
        response = requests.get(self.base_url + 'acquisition/comm-path/%i/meter/list' % communication_path_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

    def GetVirtualMeters(self, meter_id):
        response = requests.get(self.base_url + 'acquisition/meter/%i/virtual-meter/list' % meter_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

    def ListAttributes(self, vm_id):
        response = requests.get(self.base_url + 'acquisition/virtual-meter/%i' % vm_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

if __name__ == "__main__":
    # Create a new API sessions
    session = Main(API_URL_BASE)
    # Sign-in to the system
    session.Login(API_USERNAME, API_PASSWORD)

    # Call a method: Get list of CPs
    meter_list = session.GetMeters(COMMUNICATION_PATH_ID)
    for meter in meter_list:    	
    	print('Meter:', meter['name'])
    	for virtual_meter in session.GetVirtualMeters(meter['id']):
    		print('    Virtual Meter:', virtual_meter['name'])
    		for attribute in session.ListAttributes(virtual_meter['id'])['attributes']:
    			#print(attribute)
    			print('        %-25s: %s' % (attribute['id'], attribute['value']))

