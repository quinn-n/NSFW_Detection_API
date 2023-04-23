#!/bin/bash

systemctl disable --user --now nsfwdetector.service
rm ~/.config/systemd/user/nsfwdetector.service
systemctl --user daemon-reload

pew rm nsfwdetector