#!/bin/sh
##################################################
# test
##################################################
systemctl stop myvideo
ip link set wlan1 down                               
iw dev wlan1 set monitor otherbss fcsfail
ip link set wlan1 up                               
sleep 1
iw dev wlan1 set freq 2357
sleep 1
### channel -19
iw dev wlan1 set freq 2312
### channel 11
##iw dev wlan1 set freq 2462
iw reg set BO
iwconfig wlan1 txpower 30
iwconfig wlan1
iw dev
#iw reg get
#raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o -|/root/wifibroadcast/tx -p 0 -b 8 -r 4 -f 1024 wlan1
raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o -|/root/WifiBroadcast/wifibroadcast/tx -p 0 -b 8 -r 4 -f 1024 wlan1
