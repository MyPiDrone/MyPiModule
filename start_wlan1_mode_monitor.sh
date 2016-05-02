#!/bin/sh
##################################################
# test
##################################################
systemctl stop myvideo
iw dev wlan1 del
iw dev
#iw phy1 interface add wlan1 type monitor
iw phy1 interface add wlan1 type monitor flags otherbss fcsfail         
iwconfig wlan1 channel -13
ifconfig wlan1 down
#iw dev wlan1 set monitor otherbss fcsfail
iw reg set BO
iw reg get
iwconfig wlan1 txpower 30
ifconfig wlan1 up
#iwconfig wlan1 channel -13
#Error for wireless request "Set Frequency" (8B04) :
#    SET failed on device wlan1 ; Invalid argument.
#ip a
#ifconfig wlan1
#iw dev 
#iwconfig wlan1|grep "^wlan1"
iwconfig wlan1
iw dev
#raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o -|/root/wifibroadcast/tx -p 0 -b 8 -r 4 -f 1024 wlan1
raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o -|/root/WifiBroadcast/wifibroadcast/tx -p 0 -b 8 -r 4 -f 1024 wlan1
