#!/bin/bash

systemctl disable --user --now nsfwdetector.service
sudo rm /etc/systemd/system/nsfwdetector.service
systemctl daemon-reload

pew rm nsfwdetector