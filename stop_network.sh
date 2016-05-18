#!/bin/sh
#TITLE# DRONE wlan0 down called by MyPiModule
#
nohup ifdown wlan0 2>&1 &
echo "ifdown wlan0"
exit 0
