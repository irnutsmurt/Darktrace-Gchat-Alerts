import json
import requests
import logging
import os

logger = logging.getLogger('main')

def load_sent_alerts(sent_alerts_file):
    if os.path.exists(sent_alerts_file) and os.stat(sent_alerts_file).st_size > 0:
        with open(sent_alerts_file, 'r') as f:
            try:
                sent_alerts = json.load(f)
                if isinstance(sent_alerts, list):
                    return set(alert['pbid'] for alert in sent_alerts if 'pbid' in alert)
                else:
                    logger.error(f"Invalid data format in {sent_alerts_file}. Expected a list.")
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to load sent alerts from {sent_alerts_file}: {str(e)}")
    else:
        logger.error(f"{sent_alerts_file} not found. Creating a new file...")
        with open(sent_alerts_file, 'w') as f:
            f.write("[]")
    return set()

def send_alerts_to_chat(webhook_url, sent_alerts_file, parsed_alerts_file):
    # Load the set of previously sent alerts from JSON file
    sent_alerts = load_sent_alerts(sent_alerts_file)

    # Load the parsed alerts from file
    parsed_alerts = []
    if os.path.exists(parsed_alerts_file) and os.stat(parsed_alerts_file).st_size > 0:
        with open(parsed_alerts_file, 'r') as f:
            try:
                parsed_alerts = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON in {parsed_alerts_file}")
                return

    # Filter out alerts that have already been sent
    new_alerts = [alert for alert in parsed_alerts if 'pbid' in alert and alert['pbid'] not in sent_alerts]

    # Send new alerts to Google Chat and update sent alerts
    if new_alerts:
        message = ""
        for alert in new_alerts:
            url = f'https://sc-darktrace/#modelbreach/{alert["pbid"]}'  # generate the URL

            message += "____________________________________________________________________________________________________\n"
            message += f"*Alert:* {alert['name']}\n"  
            message += f"*Score:* {alert['score']}\n"
            message += f"*Source Device:* {alert['device']}\n"
            message += f"*Investigation URL:* {url}\n"
            message += f"*Category:* {alert['category']}\n"
            message += f"*Time:* {alert['time']}\n"
            message += f"*Description:* {alert['description']}\n\n"

        data = {
            "text": message
        }

        response = requests.post(webhook_url, json=data)
        if response.status_code != 200:
            logger.error(f"Failed to send alerts to Google Chat. Response status: {response.status_code}, response text: {response.text}")
        else:
            # Update the JSON file with the new alerts
            sent_alerts.update(alert['pbid'] for alert in new_alerts)  # add pbid to sent_alerts set
            with open(sent_alerts_file, 'w') as f:
                json.dump([{"pbid": pbid} for pbid in sent_alerts], f, indent=4)  # save updated sent_alerts to file
    else:
        logger.info("No new alerts to send")

    # Save the updated sent_alerts set to file
    with open(sent_alerts_file, 'w') as f:
        json.dump([{"pbid": pbid} for pbid in sent_alerts], f, indent=4)


def save_formatted_alerts(alerts, filepath):
    # Format the alerts
    formatted_alerts = ''
    for alert in alerts:
        formatted_alerts += f'{alert["time"]} - {alert["name"]}: {alert["description"]}\n'

    # Save the formatted alerts to file
    with open(filepath, 'a') as f:
        f.write(formatted_alerts)

    logger.debug(f'Formatted alerts saved to {filepath}')
	
