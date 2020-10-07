#!/usr/bin/env python3
# Note: pip install requests
import json, requests, sys, time
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
API_URL_BASE = 'http://10.42.210.60:5000/api/'
#API_URL_BASE = 'http://192.168.33.118:8081/api/'
#API_URL_BASE = 'http://localhost:8080/api/'
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

    def GetCommPaths(self):
        response = requests.get(self.base_url + 'acquisition/comm-path/list', headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

    def CreateCommPath(self, name):
        data = {
            "name": name,
            "communicationPathType": {
                "id": "LG_E650_DLMS"
            },
            "segment": {
                "id": 666001,
            },
            "phoneNumber": "",
            "mainPool": {
                "id": 11949,
            },
            "backupPool": None
        }
        response = requests.post(self.base_url + 'acquisition/comm-path', headers=self.headers, json=data)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

    def SetupCommPath(self, cp_id, ip, port):
        response = requests.get(self.base_url + 'acquisition/comm-path/%s' % cp_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        data = json.loads(response.content.decode('utf-8'))
        mod = False
        for attr in data:
            del attr['constraint']
            if (attr['idSource'] == 1) and (attr['id'] == '580'):
                if attr['value'] != ip:
                    attr['value'] = ip
                    mod = True
            if (attr['idSource'] == 1) and (attr['id'] == '612'):
                if attr['value'] != port:
                    attr['value'] = port
                    mod = True
        if mod:
            response = requests.put(self.base_url + 'acquisition/comm-path/%s' % cp_id, headers=self.headers, json=data)
            if response.status_code != 200:
                raise Exception("Fatal error (%s)." % response.status_code)

    def SetupMeter(self, m_id, physical_address):
        response = requests.get(self.base_url + 'acquisition/meter/%s' % m_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        data_source = json.loads(response.content.decode('utf-8'))
        data = []
        mod = False
        for attr in data_source:
            if attr['idSource'] == 1:
                if attr['id'] == '685':
                    if attr['value'] != physical_address:
                        attr['value'] = physical_address
                        mod = True
                elif attr['id'] == '509':
                    continue

            if not attr['readonly']:
                data.append({
                    'id': attr['id'],
                    'idSource': attr['idSource'],
                    'value': attr['value'],
                    'valueType': attr['valueType'],
                    'valueNullable': attr['valueNullable'],
                    })
        if mod:
            response = requests.put(self.base_url + 'acquisition/meter/%s' % m_id, headers=self.headers, json=data)
            if response.status_code != 200:
                raise Exception("Fatal error (%s)." % response.status_code)

    def GetMeters(self, cp_id):
        response = requests.get(self.base_url + 'acquisition/comm-path/%s/meter/list' % cp_id, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

    def CreateAll(self, name):
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
        response = requests.post(self.base_url + 'acquisition/definition', headers=self.headers, json=data)
        if response.status_code != 200:
            raise Exception("Fatal error (%s)." % response.status_code)
        return json.loads(response.content.decode('utf-8'))

if __name__ == "__main__":
    # Create a new API sessions
    session = Main(API_URL_BASE)
    # Sign-in to the system
    session.Login(API_USERNAME, API_PASSWORD)

    # Call a method: Get list of CPs
    cps = session.GetCommPaths()['rows']
    cp_list = []
    for ip4 in range(50, 70):
        for port in range(16097, 62001):
            name = 'perftest %s at %s' % (port, ip4,)
            cp_name = 'CP %s' % name
            cp_row = [cp for cp in cps if cp['1'] == cp_name]
            if cp_row:
                cp_id = int(cp_row[0]['0'])
            else:
                max_err = 5
                while True:
                    try:
                        cp_id = int(session.CreateAll(name))
                        break
                    except KeyboardInterrupt:
                        raise
                    except Exception as ex:
                        print("CP", ex)
                        max_err = max_err - 1
                        if not max_err:
                            max_err = -1
                            break
                        time.sleep(1)
                if max_err == -1:
                    continue

            print('CP_ID=%s' % (cp_id,))
            while True:
                try:
                    session.SetupCommPath(cp_id, '192.168.33.%s' % ip4, port)
                    meters = session.GetMeters(cp_id)
                    if meters:
                        m_id = meters[0]['id']
                        session.SetupMeter(m_id, (port % 10000) + 1000)
                        print('M_ID=%s' % (m_id,))
                    break
                except KeyboardInterrupt:
                    raise
                except Exception as ex:
                    print("M", ex)
                    time.sleep(1)
