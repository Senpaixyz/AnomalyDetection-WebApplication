from dotenv import load_dotenv
import os
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

HOST = os.environ.get('FLASK_RUN_HOST')
PORT = os.environ.get('FLASK_RUN_PORT')
DEBUG = os.environ.get('FLASK_DEBUG')


HIGH_SEVERITY_INTERVAL = int(os.environ.get('HIGH_SEVERITY_INTERVAL'))
MODERATE_SEVERITY_INTERVAL = int(os.environ.get('MODERATE_SEVERITY_INTERVAL'))

BUFFER_LENGTH = int(os.environ.get('BUFFER_LENGTH'))
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL'))
SEVERITY_PERCENTAGE_LENGTH = float(os.environ.get('SEVERITY_PERCENTAGE_LENGTH'))
SLEEP_INTERVAL = float(os.environ.get('SLEEP_INTERVAL'))


API_TOKEN = os.environ.get('SMS_API_TOKEN')
SENDER_NAME = os.environ.get('SMS_SENDER_NAME')
MOBILE_NO = os.environ.get('MOBILE_NO')
MODERATE_SEVERITY_SMS = os.environ.get('MODERATE_SEVERITY_SMS')
HIGH_SEVERITY_SMS = os.environ.get('HIGH_SEVERITY_SMS')
SMS_DEBUG = os.environ.get('SMS_DEBUG')
