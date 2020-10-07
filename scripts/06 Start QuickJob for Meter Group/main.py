#!/usr/bin/env python3
# Note: pip install requests
import json, requests
from requests_ntlm import HttpNtlmAuth
from datetime import datetime, timedelta
from dateutil import tz

# == Settings ==
#                        This is just a sample! Arguments below in the endpoint call has to be modified accordingly!
# Authentication
API_USERNAME = 'ADVSE\\username'
API_PASSWORD = 'password'
ACTIVE_DIRECTORY_ENABLE = True
# API root URI
API_URL_BASE = 'https://cnv-ims-ma01.vse.sk/rest_api/api/'
# API call origin and referer
ORIGIN = API_URL_BASE
GROUP_NAME = "Monitoring"

# ==============

class ConvergeSession:
    # The class implements session.

    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json',
                        'Referer': ORIGIN,
                        'Origin': ORIGIN}
        self.session = requests.Session()

    def Login(self, username, password):
        if not ACTIVE_DIRECTORY_ENABLE:
            content = {'userName': username, 'password': password}
            response = requests.post(self.base_url + 'login/user-login', headers=self.headers, json=content, verify=False)
            if response.status_code != 200:
                raise Exception("Authentication has failed.")
            self.headers['Authorization'] = 'Bearer %s' % json.loads(response.content.decode('utf-8'))['token']
        else:
            self.session.verify = False
            self.session.auth = HttpNtlmAuth(username, password)

class Main(ConvergeSession):
    # The main script method used below

    def __init__(self, *args, **kwagrs):
        super().__init__(*args, **kwagrs)

    def GetMeterGroups(self):
        response = self.session.get(self.base_url + 'acquisition/meter-group/list', headers=self.headers, verify=False)
        if response.status_code != 200:
            raise Exception("Fatal error. %s" % response.status_code)
        return json.loads(response.content.decode('utf-8'))

    def StartQuickJob(self, group_id, request_data):
        response = self.session.post(self.base_url + 'acquisition/meter-group/%i/quick-job' % group_id, headers=self.headers, json=request_data, verify=False)
        if response.status_code != 200:
            raise Exception("Fatal error. %s" % response.status_code)

if __name__ == "__main__":
    # Create a new API sessions
    session = Main(API_URL_BASE)
    # Sign-in to the system
    session.Login(API_USERNAME, API_PASSWORD)


    # Find group by name
    group_id = next((g['id'] for g in session.GetMeterGroups() if g['name'] == GROUP_NAME), None)
    if group_id == None:
        raise Exception("Group '%s' not found." % GROUP_NAME)

    # Start QJ for group
    tz_utc = tz.gettz('utc')
    t_to = datetime.today()
    t_from = datetime.combine(t_to.date() - timedelta(days=1),datetime.min.time())
    session.StartQuickJob(group_id, {
        "automaticTimeRange":False,
        "manualTimeFrom": t_from.astimezone(tz_utc).isoformat(),
        "manualTimeUntil": t_to.astimezone(tz_utc).isoformat(),
        "maxJobDuration":"01:00:00",
        "maxSingleAttemptDuration":"00:20:00",
        "maxAttemptsMain":1,
        "maxAttemptsBackup":0,
        "retryDelay":"00:00:30",
        "priority":2,
        "actions":[{
            "action":1,  #BV
            "parameters":{}
            },
            {
            "action":2,  #LP
            "parameters":{}
            },
            {
            "action":22,  #DLP
            "parameters":{}
            }]
        })
