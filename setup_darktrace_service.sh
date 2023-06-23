#!/bin/bash

# Create the service account if it doesn't exist
if ! id -u dtalerts > /dev/null 2>&1; then
    sudo useradd -r -s /bin/false dtalerts
fi

# Get the full path of the current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create systemd service
echo "[Unit]
Description=Darktrace Google Chat Alert Service

[Service]
User=dtalerts
ExecStart=/usr/bin/python3 $DIR/main.py
WorkingDirectory=$DIR
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/dtgchatalerts.service > /dev/null

# Change ownership and permissions of files
sudo chown dtalerts:root $DIR/*
sudo chmod 600 $DIR/config.ini
sudo chmod 644 $DIR/*.py

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable dtgchatalerts.service

echo "Done. You can now start the service with: sudo systemctl start dtgchatalerts"
