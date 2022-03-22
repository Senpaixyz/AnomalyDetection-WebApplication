import json
import numpy as np
from datetime import datetime
from flask import Flask, Response, render_template, request,jsonify
from library.sms_api import SMS
from joblib import load
import pyrebase
import time
import sys
# Firebase API
# set temporaryly some api key to py
config = {
    "apiKey": "AIzaSyBym004axtB-2cyCO3a0_F1kDaGgaz0h_w",
    "authDomain": "anomaly-detection-1bd55.firebaseapp.com",
    "projectId": "anomaly-detection-1bd55",
    "databaseURL":"https://anomaly-detection-1bd55-default-rtdb.firebaseio.com/",
    "storageBucket": "anomaly-detection-1bd55.appspot.com",
    "messagingSenderId": "164779489599",
    "appId": "1:164779489599:web:503ca5bedb4beb5cb13b8a"
};

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()
database = firebase.database()

"""
    - Load our instance of our application and severity rates
"""

HIGH_SEVERITY_INTERVAL = 10 # 10s
MODERATE_SEVERITY_INTERVAL = 20 # 20s


#System Configuration
MODEL_PATH = "model/clf.joblib"
CHECK_INTERVAL = 4
SEVERITY_PERCENTAGE_LENGTH = 3
BUFFER_LENGTH = 20
SLEEP_INTERVAL = 0.5#0.1

UNIQUE_LENGTH_THRESHOLD = 2
INTERVAL_STATUS_CHECKER = 30
INTERVAL_LOSS_CHECKER = 20
INTERVAL_TOTAL_ATTEMPT = 10



MODERATE_SEVERITY_SMS = "Moderate Severity Message here"
HIGH_SEVERITY_SMS = "High Severity Message here"

app = Flask(__name__)
moderate_severity = SMS("Moderate", MODERATE_SEVERITY_SMS)
high_severity = SMS("High", HIGH_SEVERITY_SMS)



# run_with_ngrok(application) # for remote monitoringaa


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-monitoring', methods=['GET', 'POST'])
def set_monitoring():
    if request.method == "POST":
        qtc_data = request.form.get('monitoring')
        database.child('Network-Active').set(qtc_data)
    results = {'processed': qtc_data}
    return jsonify(results)
@app.route('/fetch_data')
def fetch_data():
    def _run():
        database.child('Network-Connection').set("Failed")
        database.child('Network-Active').set("False")

        anomalyBytes = 0
        arrayBytesInstances = 0
        threshold = 0
        severity_lists = []
        current_percentage = 0.0
        severity_percentage = 0.0
        connecting_attempt = 0
        status_count = 0
        status_loss_count = 0

        check_status_interval = INTERVAL_STATUS_CHECKER
        connecting_loss_interval = INTERVAL_LOSS_CHECKER
        connecting_total_attempt = INTERVAL_TOTAL_ATTEMPT
        check_waiting_start = 0
        check_waiting_interval = 5
        buffer_length = BUFFER_LENGTH
        check_interval = CHECK_INTERVAL
        severity_percentage_length = SEVERITY_PERCENTAGE_LENGTH
        sleep_interval = SLEEP_INTERVAL

        to_predict_buffer = []
        m = load_application_model(MODEL_PATH)
        while True:
            severity_status = []
            isMonitoringOn = eval(database.child("Network-Active").get().val())
            data = database.child('Network-Traffic').get().val()
            status = database.child('Network-Connection').get().val()

            if status == "Connected":
                if isMonitoringOn:
                    if len(data) <= 0:
                        data = [[0, 0, 0]]
                    if len(to_predict_buffer) > buffer_length:
                        anomalyBytes, arrayBytesInstances = predict_bytes(
                            to_predict_buffer,
                            anomalyBytes,
                            m,
                            arrayBytesInstances
                        )
                        if threshold == check_interval - 1:
                            try:
                                current_percentage = round(anomalyBytes / arrayBytesInstances, 1)
                                if len(severity_lists) > severity_percentage_length - 1:
                                    severity_lists.pop(0)
                                severity_lists.append(current_percentage)
                                severity_percentage = round(sum(severity_lists) / severity_percentage_length, 1)
                                severity_status = check_severity_status(severity_percentage)
                                anomalyBytes = 0
                                arrayBytesInstances = 0
                                threshold = 0
                                #print("CURRENT PERCENTAGE: ", current_percentage)
                                #print("SEVERITY: ", severity_lists)
                            except ZeroDivisionError as e:
                                print("Network Inactive...")
                                anomalyBytes = 0
                                arrayBytesInstances = 0
                        else:
                            threshold += 1
                        to_predict_buffer = []
                    for packets in data:
                        average_len = packets[0]
                        average_payload = packets[1]
                        pkt_count = packets[2]
                        if len(data) > 0:
                            pkt = [average_len, average_payload]
                            to_predict_buffer.append(pkt)
                        json_data = json.dumps(
                            {
                                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'packet_length': average_len,
                                'payload_length': average_payload,
                                'packet_count': pkt_count,
                                'anomaly_rate': current_percentage,
                                'severity_rate': severity_percentage,
                                'severity_state': severity_status,
                                'status': 'Connected',
                                'monitor': 'On'
                            })

                        yield f"data:{json_data}\n\n"
                        #time.sleep(sleep_interval)

                else:
                    json_data = json.dumps(
                        {
                            'status': 'Connected',
                            'monitor': 'Off'
                        })

                    yield f"data:{json_data}\n\n"


                status_count += 1
                if status_count >= check_status_interval:
                    #print("SETTING STATUS TO FAILED!!!")
                    database.child('Network-Connection').set("Failed")
                    status_count = 0
            else:

                if check_waiting_start > check_waiting_interval:
                    status_conn = ""
                    check_waiting_start = 0
                    status_loss_count += 1
                    if connecting_attempt > connecting_total_attempt:
                        status_conn = "Stop"
                    elif status_loss_count >= connecting_loss_interval:
                        status_conn = "Failed"
                        status_loss_count = 0
                        connecting_attempt += 1
                    else:
                        status_conn = "Connecting"

                    json_data = json.dumps(
                        {
                            'status': status_conn,
                            'monitor': 'Off'
                        })

                    yield f"data:{json_data}\n\n"
                check_waiting_start += 1
            time.sleep(sleep_interval)
    return Response(_run(), mimetype='text/event-stream')

def check_severity_status(severity_level):
    """
        :severity_level: level of severity base on the packets flows
        : if severity level >= 45 and <= to 50 it must be a moderate
        : if severity level >= 51 and <= to 100 it must be a high
    """
    severity_level = int(severity_level)
    if 0.51 <= severity_level <= 1.0:
        moderate_severity.reset_interval()
        high_severity.check_status()
        if not high_severity.has_sent():
            high_severity.send_sms()
        severity_state = "High"
        tmp = "Next SMS will be Send:{0}".format(high_severity.nxtSent)
        return [severity_state, tmp]
    elif 0.45 <= severity_level <= 0.50:
        high_severity.reset_interval()
        moderate_severity.check_status()
        if not moderate_severity.has_sent():
            moderate_severity.send_sms()

        severity_state = "Moderate"
        tmp = "Next SMS will be Send:{0}".format(moderate_severity.nxtSent)
        return [severity_state, tmp]
    elif 0.10 <= severity_level <= 0.44:
        severity_state = "Low"
        tmp = ""
        return [severity_state, tmp]
    elif 0 <= severity_level <= 0.09:
        severity_state = "Normal"
        high_severity.reset_interval()
        moderate_severity.reset_interval()
        tmp = ""
        return [severity_state, tmp]

def load_application_model(path):
    try:
        m = load(path)
        return m
    except FileNotFoundError:
        print("Model File not Found!")
        sys.exit()

def predict_bytes(packets, anomalyBytes,m, arrayBytesInstances):
    data = packets
    try:
        # unique = np.unique(data,axis=0)
        unique = np.unique(data, axis=0)
        c = m.predict(data)
        #print("DATA: ", data)
        # print("UNIQUE: ", unique)
        if len(unique) <= 2:
            anomalyBytes += 1
        arrayBytesInstances += 1
        #print("UNIQUE LENGTH: ", anomalyBytes, " TOTAL LENGTH: ", arrayBytesInstances)
        return anomalyBytes, arrayBytesInstances
    except ValueError as e:
        print("Input to model values contains valid network packets.... :) ")


if __name__ == '__main__':

    app.run(debug=True)
    # application.run(debug=True, threaded=True)
    # application.run()


