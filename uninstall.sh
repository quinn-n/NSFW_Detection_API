#!/bin/bash

systemctl disable --user --now nsfwdetector.service
rm ~/.config/systemd/user/nsfwdetector.service

pew rm nsfwdetector