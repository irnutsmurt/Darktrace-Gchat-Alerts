import requests
import urllib3
import hmac
import hashlib
import json
import configparser
import os
import httplib2
import logging
from httplib2 import Http
import time
import pytz
from datetime import datetime, timedelta, timezone
from utils import parse_raw_alerts, write_parsed_alerts
import logging

logger = logging.getLogger('main')

config = configparser.ConfigParser()
config.read('config.ini')

private_token = config['darktrace']['private_token']
public_token = config['darktrace']['public_token']
url = config['darktrace']['url']
min_score = float(config['darktrace']['min_score'])
time_frame = int(config['darktrace']['time_frame'])

# define the http_obj
http_obj = Http()

def get_raw_alerts():
    # Calculate the start time for the API request
    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(hours=time_frame)).timestamp() * 1000

    # Calculate the signature for model breaches
    date = datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    api_request = f'/modelbreaches?starttime={start_time}&minscore={min_score}'
    signature = hmac.new(private_token.encode('ascii'),
                         (api_request + '\n' + public_token + '\n' + date).encode('ascii'),
                         hashlib.sha1).hexdigest()

    headers = {
        'DTAPI-Token': public_token,
        'DTAPI-Date': date,
        'DTAPI-Signature': signature
    }

    urllib3.disable_warnings()
    response = requests.get(url + api_request, headers=headers, verify=False)

    if response.status_code == 200:
        # save the raw alerts to a file
        with open(config['darktrace']['raw_alerts_file'], 'w') as f:
            json.dump(response.json(), f, indent=4)
        logger.info(f"{len(response.json())} raw alerts downloaded to {config['darktrace']['raw_alerts_file']}")

        return response.json()
    else:
        logger.error(f"Failed to get raw alerts from Darktrace: {response.text}")
        return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()

    main()