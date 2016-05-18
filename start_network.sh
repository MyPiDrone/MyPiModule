#!/bin/sh
#TITLE# DRONE wlan0 up called by MyPiModule
#
nohup ifup wlan0 >/var/log/start_network.log 2>&1 &
echo "ifup wlan0"
exit 0
