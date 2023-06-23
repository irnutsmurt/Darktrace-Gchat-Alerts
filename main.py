from darktrace import get_raw_alerts
from utils import parse_raw_alerts, write_parsed_alerts
from google_chat import send_alerts_to_chat, load_sent_alerts
import configparser
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import json

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# setup handler for file rotation
file_handler = TimedRotatingFileHandler('debug.log', when="midnight", interval=1)
file_handler.setFormatter(formatter)
file_handler.suffix = "%m%d%Y"  # or whatever you want to keep as the filename suffix

# setup handler for console output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Set up the logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

webhook_url = config['google_chat']['webhook_url']
raw_alerts_file = config['darktrace']['raw_alerts_file']
parsed_alerts_file = config['darktrace']['parsed_alerts_file']
sent_alerts_file = config['google_chat']['sent_alerts_file']

def main():
    while True:
        print("Fetching raw alerts from Darktrace...")
        # get the list of raw alerts from Darktrace
        raw_alerts = get_raw_alerts()
        if raw_alerts is not None:
            # Load the set of previously sent alerts
            sent_alerts = load_sent_alerts(sent_alerts_file)

            # Filter out raw alerts that have already been sent
            new_raw_alerts = [alert for alert in raw_alerts if alert['pbid'] not in sent_alerts]

            if new_raw_alerts:
                print(f"{len(new_raw_alerts)} raw alerts to parse and send.")

                print("Parsing raw alerts...")
                # parse the new raw alerts and save to file
                parsed_alerts = parse_raw_alerts(new_raw_alerts, parsed_alerts_file)

                # send new alerts to Google Chat
                if parsed_alerts:
                    print("Sending new alerts to Google Chat...")
                    send_alerts_to_chat(webhook_url, sent_alerts_file, parsed_alerts_file)
                    logger.info(f"{len(parsed_alerts)} alerts sent to Google Chat")

                    # write parsed alerts to file
                    write_parsed_alerts(parsed_alerts, parsed_alerts_file)

            else:
                print("No new raw alerts to parse.")

        # wait for 1 minute before fetching new alerts
        print("Waiting for 1 minute before fetching new alerts...")
        time.sleep(60)


if __name__ == '__main__':
    main()
