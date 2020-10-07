#!/usr/bin/env python3
# Note: pip install requests
import json, requests, sys, time, os
from datetime import datetime, timedelta
from dateutil import tz

argv = list(sys.argv)
argv.extend(('', '',))

# == Settings ==
#                        This is just a sample! Arguments below in the endpoint call has to be modified accordingly!
# Authentication
API_USERNAME = argv[1] or os.environ.get('C4_USER', '')
API_PASSWORD = argv[2] or os.environ.get('C4_PASS', '')
# API root URI
API_URL_BASE = 'https://test.metering.space/api/'
# API call origin and referer
ORIGIN = API_URL_BASE
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

    def SetupCommPath(self, cp_id, ip, port):
        # Get CP
        response = requests.get(self.base_url + 'acquisition/comm-path/%s' % cp_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        data_source = json.loads(response.content.decode('utf-8'))
        # Set IP and port
        data = []
        for attr in data_source:
            if (attr['idSource'] == 1) and (attr['id'] == 'PathIPAddress'):
                if attr['value'] != ip:
                    data.append({
                        'id': attr['id'],
                        'idSource': attr['idSource'],
                        'value': ip,
                        'valueType': attr['valueType'],
                        'valueNullable': attr['valueNullable'],
                        })
                    continue
            if (attr['idSource'] == 1) and (attr['id'] == 'TCPPortNumber'):
                if attr['value'] != port:
                    data.append({
                        'id': attr['id'],
                        'idSource': attr['idSource'],
                        'value': port,
                        'valueType': attr['valueType'],
                        'valueNullable': attr['valueNullable'],
                        })
                    continue
            if attr['required']:
                data.append({
                    'id': attr['id'],
                    'idSource': attr['idSource'],
                    'value': attr['value'],
                    'valueType': attr['valueType'],
                    'valueNullable': attr['valueNullable'],
                    })

        # If set, post it back
        if data:
            response = requests.put(self.base_url + 'acquisition/comm-path/%s' % cp_id, headers=self.headers, json=data)
            if response.status_code != 200:
                raise Exception("Fatal error (%s)." % response.status_code)

    def GetMeters(self, cp_id):
        response = requests.get(self.base_url + 'acquisition/comm-path/%s/meter/list' % cp_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

    def SetupMeter(self, m_id, physical_address):
        # Get M
        response = requests.get(self.base_url + 'acquisition/meter/%s' % m_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        data_source = json.loads(response.content.decode('utf-8'))
        # Set DLMSDestAddrPhysical
        data = []
        for attr in data_source:
            if attr['idSource'] == 1:
                if attr['id'] == 'DLMSDestAddrPhysical':
                    if attr['value'] != physical_address:
                        data.append({
                            'id': attr['id'],
                            'idSource': attr['idSource'],
                            'value': physical_address,
                            'valueType': attr['valueType'],
                            'valueNullable': attr['valueNullable'],
                            })
                        continue
            if attr['required']:
                data.append({
                    'id': attr['id'],
                    'idSource': attr['idSource'],
                    'value': attr['value'],
                    'valueType': attr['valueType'],
                    'valueNullable': attr['valueNullable'],
                    })

        # If set, post it back
        if data:
            response = requests.put(self.base_url + 'acquisition/meter/%s' % m_id, headers=self.headers, json=data)
            if response.status_code != 200:
                raise Exception("Fatal error (%s)." % response.status_code)

    def CreateAll(self, name):
        # CP/M/VM data definition
        data = {
          "segment": {
            "id": 666001
          },
          "communicationPathType": {
            "id": "LG_E650_DLMS"
          },
          "communicationPathName": "CP %s" % name,
          "mainPool": {
            "id": 11949
          },
          "backupPool": None,
          "meterType": {
            "id": "LG_E650_DLMS"
          },
          "meterName": "M %s" % name,
          "createVirtualMeter": True,
          "virtualMeterTemplate": {
            "id": 1896
          },
          "virtualMeterName": "VM %s" % name,
          "virtualMeterType": {
            "id": 11972
          }
        }
        # Post it
        response = requests.post(self.base_url + 'acquisition/definition', headers=self.headers, json=data)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

if __name__ == "__main__":
    # Create a new API sessions
    session = Main(API_URL_BASE)
    # Sign-in to the system
    session.Login(API_USERNAME, API_PASSWORD)
    # Call a method: Create CP/M/VM
    cp_id = session.CreateAll("Sibelga_"+datetime.now().strftime("%Y%m%d_%H%M%S"))
    print("Communication Path created! Id =", cp_id)
    # Setup some parameters
    session.SetupCommPath(cp_id, "127.0.0.1", 4059)
    print("Communication Path IP/port has been set.")
    # Setup child meters (should be one if nobody added meanwhile another one)
    for meter in session.GetMeters(cp_id):
        session.SetupMeter(meter['id'], 50)
        print("Meter '%s' HDLC address has been set." % meter['name'])
