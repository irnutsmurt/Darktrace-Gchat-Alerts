**Prerequisites**

1. Ubuntu 20.04 or later.
2. Python 3 and pip installed. If not installed, you can install it using the following commands:

```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Steps**

1. First, open a terminal and navigate to the `/opt` directory:

```bash
cd /opt
```

2. Here, create a new directory for the script files:

```bash
sudo mkdir darktrace_alerts
cd darktrace_alerts
```

3. Now, upload the Python scripts and config.ini file to this directory. The files needed are:

- The Python script that pulls data from the Darktrace API.
- The Python script that sends the alert data to Google Chat.
- The config.ini file.

4. Update the config.ini file with the required parameters:

```ini
[google_chat]
webhook_url = <your_google_chat_webhook_url>
formatted_alerts_file = formatted_alerts.json
sent_alerts_file = sent_alerts.json

[darktrace]
private_token = <your_darktrace_private_token>
public_token = <your_darktrace_public_token>
url = <your_darktrace_api_url>
min_score = 0.70
time_frame = 1
raw_alerts_file = raw_alerts.json
parsed_alerts_file = parsed_alerts.csv
```

Replace `<your_google_chat_webhook_url>`, `<your_darktrace_private_token>`, `<your_darktrace_public_token>`, and `<your_darktrace_api_url>` with your actual values.

5. After updating the configuration, run the provided Bash script to setup the systemd service:

```bash
bash setup_darktrace_service.sh
```

This will:

- Create a new user called `dtalerts` with no login permissions.
- Set the proper permissions for the scripts and config file.
- Set up a systemd service called `dtgchatalerts.service` that runs the Python script every minute.

6. Once the script is finished, you can start the service with the following command:

```bash
sudo systemctl start dtgchatalerts
```

7. To make the service run at startup, enable it:

```bash
sudo systemctl enable dtgchatalerts
```

Now, the service should be pulling data from the Darktrace API every minute and sending any new alerts to Google Chat.

8. You can check the status of the service with:

```bash
sudo systemctl status dtgchatalerts
```

And check its logs with:

```bash
journalctl -u dtgchatalerts.service
```

That's it! Your service should now be set up and running.

Note: Be sure to change file names and paths according to your setup and script names.
