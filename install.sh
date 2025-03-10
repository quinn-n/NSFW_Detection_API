#!/bin/bash

# Install python dependencies inside pew env
pew new -a `pwd` nsfwdetector -d
pew in nsfwdetector pip install -r requirements.txt

# Create user systemd service
sudo cp nsfwdetector.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "Run 'systemctl enable --now nsfwdetector' to enable & start the service."
