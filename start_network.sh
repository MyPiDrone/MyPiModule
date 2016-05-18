#!/bin/sh
#TITLE# DRONE wlan0 up
nohup ifup wlan0 2>&1 &
echo "ifup wlan0"
exit 0
