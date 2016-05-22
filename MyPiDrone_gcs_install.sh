#!/bin/sh
###########################################################
####### www.MyPiDrone.com  
#TITLE# GCS install start_rx and wifiap
###########################################################
date=`date +'%Y-%m-%d'`
MY_DIR_MYPIDRONE="/root/MyPiDrone"
cd ${MY_DIR_MYPIDRONE}
#
cp MyPiModule/dnsmasq.conf                                    /etc/
cp MyPiModule/hostapd.conf                                    /etc/hostapd/
cp MyPiModule/wifiap.service                                  /lib/systemd/system/
cp MyPiModule/start_rx_and_broadcast_over_ap.sh               /usr/local/bin/
cp MyPiModule/start_rx.sh                                     /usr/local/bin/
cp MyPiModule/start_gst-launch.sh                             /usr/local/bin/
#
systemctl deamon-reload

