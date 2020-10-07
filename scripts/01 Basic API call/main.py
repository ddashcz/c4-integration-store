#!/usr/bin/env python3
# Note: pip install requests
import json, requests

# == Settings ==
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

    def GetMeterData(self, request_data):
        response = requests.post(self.base_url + 'extension/basic-data-interface/virtual-meter/meter-data/list', headers=self.headers, json=request_data)
        if response.status_code != 200:
            raise Exception("Fatal error.")
        return json.loads(response.content.decode('utf-8'))

    def GetMeterEvents(self, request_data):
        response = requests.post(self.base_url + 'extension/basic-data-interface/virtual-meter/event/list', headers=self.headers, json=request_data)
        if response.status_code != 200:
            raise Exception("Fatal error.")
        return json.loads(response.content.decode('utf-8'))

if __name__ == "__main__":
    # Create a new API sessions
    session = Main(API_URL_BASE)
    # Sign-in to the system
    session.Login(API_USERNAME, API_PASSWORD)

    # Call a method: Get and show meter data
    data = session.GetMeterData({
        "dateFrom": "2019-09-05T18:47:00.478Z",
        "dateTo": "2019-09-05T19:47:00.478Z",
        "virtualMeterFilter": {
            'VMSerialNumber': '123456999999999hhh'
        },
        "variableFilter": [
            0, 1, 2
        ]
    })

    for variable in data:
        print('Variable')
        print('  Id  ', variable['variableId'])
        print('  Name', variable['variableName'])
        print('  Type', variable['variableType'])
        print('  Data')
        #print(variable['variableId'])
        for row in zip(variable['dateTime'], variable['normValue'], variable['normUnit'], variable['status'], variable['peakTime']):
            print("    ", row)

    # Call a method: Get and show meter events
    data = session.GetMeterEvents({
        "dateFrom": "2019-07-05T18:47:00.478Z",
        "dateTo": "2019-09-05T19:47:00.478Z",
        "virtualMeterFilter": {
            'VMSerialNumber': '123456999999999hhh'
        },
        "eventCategories": [
            14
        ]
    })

    for event in data:
        print('Event')
        for k in event.keys():
            print('   %-20s %s' % (k, event[k],))
