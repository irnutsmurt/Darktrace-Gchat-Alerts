import json
import os
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger('main')

def parse_raw_alerts(raw_alerts, parsed_alerts_file):
    print("Parsing raw alerts...")

    alerts = []

    for alert in raw_alerts:
        time = datetime.fromtimestamp(alert['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        pbid = alert['pbid']
        score = round(alert['score'] * 100)  # convert score to percentage and round it
        name = alert['model']['now']['name']
        device = alert.get('device', {}).get('hostname', '')
        description = alert['model']['now']['description']
        category = alert['model'].get('then', {}).get('category', '')  

        alerts.append({
            'time': time,
            'pbid': pbid,
            'score': str(score) + '%',
            'name': name,
            'device': device,
            'description': description,
            'category': category
        })

    # Display the formatted alerts
    for alert in alerts:
        print(alert) # Print to console
        logger.info(alert) # Log the alert

    # Write the parsed alerts to file
    write_parsed_alerts(alerts, parsed_alerts_file)

    return alerts

def write_parsed_alerts(alerts, file_path):
    print("Writing parsed alerts to file...")

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)  # initialize with an empty list

    with open(file_path, 'w') as f:
        json.dump(alerts, f, indent=4)
