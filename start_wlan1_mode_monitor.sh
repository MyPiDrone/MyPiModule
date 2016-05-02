#!/bin/sh
##################################################
# test
##################################################
systemctl stop myvideo
ip link set wlan1 down                               
iw dev wlan1 set type monitor flags otherbss fcsfail
ip link set wlan1 up                                                                                                                                  
iw dev wlan1 set freq 2312
#iw dev wlan1 set freq 2347
#iw dev wlan1 set freq 2462
iw dev
iwconfig wlan1
iw dev
#raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o -|/root/wifibroadcast/tx -p 0 -b 8 -r 4 -f 1024 wlan1
raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o -|/root/WifiBroadcast/wifibroadcast/tx -p 0 -b 8 -r 4 -f 1024 wlan1
