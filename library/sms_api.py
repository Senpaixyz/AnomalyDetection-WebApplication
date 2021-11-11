import os
import time

API_TOKEN = ""
API_KEY = ""


class SMS(object):

    def __init__(self, severity, interval):
        self.severityType = severity
        self.setDefaultInterval = interval
        self.currentTime = 0.0
        self.nxtSent = 0.0
        self.hasSent = False

    def __del__(self):
        print("DELETING... ", self.severityType)
        self.reset_time()

    def check_status(self):
        self.currentTime = time.time()
        curr_time_str = str(time.ctime(self.currentTime))
        nxt_time_str = str(time.ctime(self.nxtSent))
        if curr_time_str.lower() == nxt_time_str.lower():
            self.reset_interval()

    def has_sent(self):
        if self.hasSent:
            return True
        return False

    def send_sms(self):
        # send message
        self.set_interval()
        print("Sent sms to  ", self.severityType, " severity.")
        self.hasSent = True

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
