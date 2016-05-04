#!/bin/sh
##################################################
#TITLE# sample start wifi managed
##################################################
#iw event -t
systemctl stop myvideo
#iw dev wlan1 del
#iw phy1 interface add wlan1 type managed
ip link set wlan1 down
iw dev wlan1 set type managed
ip link set wlan1 up
### channel -19
iw dev wlan1 set freq 2312
### channel 11
##iw dev wlan1 set freq 2462
iw reg set BO
iwconfig wlan1 txpower 30
iwconfig wlan1
iw dev
iw dev wlan1 scan |egrep "SSID|primary channel|freq:"
iwconfig wlan1
iw dev
wpa_supplicant -i wlan1 -c /boot/wpa_supplicant.conf
