import time
import requests, urllib


API_TOKEN = "f828b11e93e3def79dbd33ebb5689195"
SENDER_NAME = "SEMAPHORE"
MOBILE_NO = "09380258562"
MODERATE_SEVERITY_SMS = "Moderate Severity Message here"
HIGH_SEVERITY_SMS = "High Severity Message here"
SMS_DEBUG = True



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
        if float(self.currentTime) >= float(self.nxtSent):
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
        isSMS_DEBUG = eval(SMS_DEBUG)
        if isSMS_DEBUG:
            print("Sms debugging is on...")
            print("-------SMS INFO--------")
            print("API TOKEN: ", API_TOKEN)
            print("SENDER NAME: ", SENDER_NAME)
            print("MESSAGE: ", message)
            print("SEVERITY TYPE: ", self.severityType)
            print("DEVICE NO: ", deviceNo)
        else:
            print("Sms debugging is off...")
            params = (
                ('apikey', API_TOKEN),
                ('sendername', SENDER_NAME),
                ('message', message),
                ('number', deviceNo)
            )
            path = 'https://semaphore.co/api/v4/messages?' + urllib.parse.urlencode(params)
            requests.post(path)
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
