import os
import time
from dotenv import load_dotenv
import sys, requests, urllib
from datetime import datetime

"""
    - Load the environment variables first
"""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, '.env')
if not os.path.exists(dotenv_path):
    raise Exception("ENV FILE NOT FOUND")
    sys.exit(1)
else:
    load_dotenv(dotenv_path)

API_TOKEN = os.environ.get('SMS_API_TOKEN')
SENDER_NAME = os.environ.get('SMS_SENDER_NAME')
MOBILE_NO = os.environ.get('MOBILE_NO')
MODERATE_SEVERITY_SMS = os.environ.get('MODERATE_SEVERITY_SMS')
HIGH_SEVERITY_SMS = os.environ.get('HIGH_SEVERITY_SMS')
SMS_DEBUG = os.environ.get('SMS_DEBUG')

class SMS(object):

    def __init__(self, severity, interval):
        self.severityType = severity
        self.setDefaultInterval = interval
        self.currentTime = 0.0
        self.nxtSent = 0.0
        self.hasSent = False

    def __del__(self):
        print("RESETTING... ", self.severityType)
        self.reset_time()

    def check_status(self):
        self.currentTime = time.time()
        #curr_time_str = str(time.ctime(self.currentTime))
        #nxt_time_str = str(time.ctime(self.nxtSent))
        if float(self.currentTime) >= float(self.nextSent):
            self.reset_interval()

    def has_sent(self):
        if self.hasSent:
            return True
        return False

    def send_sms(self):
        # send message
        print("Sent sms to  ", self.severityType, " severity.")
        self.set_interval()
        self.requests_sms()
        self.hasSent = True

    def requests_sms(self):
        print('Sending Message...')
        message = HIGH_SEVERITY_SMS if self.severityType == "High" else MODERATE_SEVERITY_SMS
        deviceNo = MOBILE_NO
        if bool(SMS_DEBUG):
            print("Sms debugging is on...")
            print("-------SMS INFO--------")
            print("API TOKEN: ", API_TOKEN)
            print("SENDER NAME: ", SENDER_NAME)
            print("MESSAGE: ", message)
            print("SEVERITY TYPE: ", self.severityType)
            print("DEVICE NO: ", deviceNo)
        else:
            print("Sms debugging is off...")
        # params = (
        #     ('apikey', API_TOKEN),
        #     ('sendername', SENDER_NAME),
        #     ('message', message),
        #     ('number', deviceNo)
        # )
        # path = 'https://semaphore.co/api/v4/messages?' + urllib.parse.urlencode(params)
        # requests.post(path)
        print('Message Sent!')

    def set_interval(self):
        currTime = time.time()
        self.nxtSent = currTime + self.setDefaultInterval
        print(" NEXT SMS WILL BE SEND : ", time.ctime(self.nxtSent), " AT ", self.severityType)

    def reset_interval(self):
        self.hasSent = False
        self.currentTime = 0.0
        self.nxtSent = 0.0
    def reset_time(self):
        pass