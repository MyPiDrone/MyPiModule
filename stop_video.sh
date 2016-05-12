#!/bin/sh
#TITLE# DRONE stop video streaming
echo "Video is stopped"
killall raspivid
WifiBroadcast_TX="/root/WifiBroadcast/wifibroadcast/tx"
killall $WifiBroadcast_TX
WifiBroadcast_TX="/root/wifibroadcast/tx"
killall $WifiBroadcast_TX
exit 0
