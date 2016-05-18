#!/bin/sh
#TITLE# DRONE wlan0 down
nohup ifdown wlan0 2>&1 &
echo "ifdown wlan0"
exit 0
