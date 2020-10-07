#!/usr/bin/env python3
# Note: pip install requests
# Note: pip install dateutil
import json, requests
from datetime import datetime, timedelta
from dateutil import tz

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

    def ExecuteAdvancedValidation(self, advanced_validation_id, request_data):
        response = requests.post(self.base_url + 'advanced-validation/%i/execute' % advanced_validation_id, headers=self.headers, json=request_data)
        if response.status_code != 200:
            raise Exception("Fatal error.")
        return json.loads(response.content.decode('utf-8'))

if __name__ == "__main__":
    # Create a new API sessions
    session = Main(API_URL_BASE)
    # Sign-in to the system
    session.Login(API_USERNAME, API_PASSWORD)

    # Call a method: Execute AVW
    tz_utc = tz.gettz('utc')
    t_to = datetime.combine(datetime.today().date(), datetime.min.time())
    t_from = t_to - timedelta(days=1)
    session.ExecuteAdvancedValidation(1234, {
        "dateFrom": t_from.astimezone(tz_utc).isoformat(),
        "dateTo": t_to.astimezone(tz_utc).isoformat(),
        "collectionId": 1,
        "priority": 7,
        "automaticTimeRange": False,
        "expiresAfter": "00:10:00",
        "maxDuration": 0,
        "filterId": 0,
        "validatedObjects": [
            1
        ],
        "validatedObjectsByName": [
        ]
    })
