#!/bin/sh
##################################################
#TITLE# sample start wifi monitor
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
#raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o -|/root/WifiBroadcast/wifibroadcast/tx -p 0 -b 8 -r 4 -f 1024 wlan1
###gst-launch-1.0 uvch264src initial-bitrate=1000000 average-bitrate=1000000 iframe-period=1000 device=/dev/video0 name=src auto-start=true src.vidsrc ! video/x-h264,width=1920,height=1080,framerate=24/1 ! h264parse ! rtph264pay ! udpsink host=10.0.0.1 port=5000
#raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o - | gst-launch-1.0 -v fdsrc !  h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5000 host=10.0.0.1
raspivid -ih -t 1200000 -w 1280 -h 720 -fps 60 -b 4000000 -n -g 60 -pf high -o - | gst-launch-1.0 -v fdsrc !  h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5600 host=192.168.1.16

