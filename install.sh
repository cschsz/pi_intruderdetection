#!/bin/bash
sudo cp -n pid.ini /usr/local/etc
sudo mkdir /usr/local/bin/pid
sudo cp *.py /usr/local/bin/pid
sudo chmod +x /usr/local/bin/pid/pid.py
sudo reboot
