#!/bin/bash

# Install python dependencies inside pew env
pew new -a `pwd` nsfwdetector -d
pew in nsfwdetector pip install -r requirements.txt

# Create user systemd service
mkdir -p ~/.config/systemd/user
cp nsfwdetector.service ~/.config/systemd/user
systemctl --user daemon-reload

echo "Run `systemctl enable --user --now nsfwdetector` to enable & start the service."
