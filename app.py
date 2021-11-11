import json
import random
import time
import numpy as np
import pandas as pd
from scapy.all import *
from scapy.sendrecv import sniff
from datetime import datetime
from flask import Flask, Response, render_template
from flask_ngrok import run_with_ngrok
from library.FlowRecoder import get_data, gen_json
from library.sms_api import SMS

application = Flask(__name__)
moderate_severity = SMS("Moderate Severity", 20)
high_severity = SMS("High Severity", 10)

# run_with_ngrok(application)


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/chart-data')
def chart_data():
    def _run():
        to_predict_buffer = []
        anomalyBytes = 0
        arrayBytesInstances = 0
        threshold = 0
        check_interval = 4
        severity_lists = []
        current_percentage = 0.0
        severity_percentage = 0.0
        severity_percentage_length = 3
        while True:
            captured_buffer = []
            severity_status = []
            for pkt in sniff(iface=conf.iface, count=2):
                captured_buffer.append(pkt)
            data = get_data(captured_buffer)
            data = gen_json(data)
            print("DATA: ", data)
            if len(data) <= 0:
                data = [[0, 0, 0]]
                print("NO PACKET TO TRACE ", data)
            if len(to_predict_buffer) > 20:
                anomalyBytes, arrayBytesInstances = predict_bytes(
                                                                    to_predict_buffer,
                                                                    anomalyBytes,
                                                                    arrayBytesInstances
                                                                )
                if threshold == check_interval-1:
                    try:
                        current_percentage = round(anomalyBytes / arrayBytesInstances, 1)
                        if len(severity_lists) > severity_percentage_length-1:
                            severity_lists.pop(0)
                        severity_lists.append(current_percentage)
                        severity_percentage = round(sum(severity_lists)/severity_percentage_length, 1)
                        severity_status = check_severity_status(severity_percentage)
                        anomalyBytes = 0
                        arrayBytesInstances = 0
                        threshold = 0
                        print("CURRENT PERCENTAGE: ", current_percentage)
                        print("SEVERITY: ", severity_lists)
                    except ZeroDivisionError as e:
                        print("Theres no current packet transmission...")
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
                    })

                yield f"data:{json_data}\n\n"
                time.sleep(0.2)

    return Response(_run(), mimetype='text/event-stream')


def check_severity_status(severity_level):
    """
        :severity_level: level of severity base on the packets flows
        : if severity level >= 45 and <= to 50 it must be a moderate
        : if severity level >= 51 and <= to 100 it must be a high
    """
    severity_level = int(severity_level)
    if 51 <= severity_level <= 100:
        moderate_severity.reset_interval()
        if not high_severity.has_sent():
            high_severity.send_sms()
        severity_state = "High"
        tmp = "Next SMS will be Send:{0}".format(high_severity.nxtSent)
        return [severity_state, tmp]
    elif 45 <= severity_level <= 50:
        high_severity.reset_interval()
        if not moderate_severity.has_sent():
            moderate_severity.send_sms()
        severity_state = "Moderate"
        tmp = "Next SMS will be Send:{0}".format(moderate_severity.nxtSent)
        return [severity_state, tmp]
    elif 10 <= severity_level <= 44:
        severity_state = "Low"
        tmp = ""
        return [severity_state, tmp]
    elif 0 <= severity_level <= 9:
        severity_state = "Normal"
        print("SEVERITY: ", severity_state)
        high_severity.reset_interval()
        moderate_severity.reset_interval()
        tmp = ""
        return [severity_state, tmp]


def predict_bytes(packets,anomalyBytes, arrayBytesInstances):
    data = packets
    try:
        # unique = np.unique(data,axis=0)
        unique = np.unique(data, axis=0)
        print("DATA: ", data)
        #print("UNIQUE: ", unique)
        if len(unique) <= 2:
            anomalyBytes += 1
        arrayBytesInstances += 1
        print("UNIQUE LENGTH: ", anomalyBytes, " TOTAL LENGTH: ", arrayBytesInstances)
        return anomalyBytes, arrayBytesInstances
    except ValueError as e:
        print("Array values contains I dunno.... :) ")


if __name__ == '__main__':
    application.run(host='0.0.0.0', port='3000', debug=True)
    # application.run(debug=True, threaded=True)
    # application.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
