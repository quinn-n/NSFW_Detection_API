#!/bin/bash

systemctl disable --user --now nsfwdetector.service
rm /usr/local/lib/systemd/system/nsfwdetector.service
systemctl --user daemon-reload

pew rm nsfwdetector