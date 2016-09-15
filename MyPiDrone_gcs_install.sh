#!/bin/sh
###########################################################
####### www.MyPiDrone.com  
#TITLE# GCS install start_rx and wifiap
###########################################################
date=`date +'%Y-%m-%d'`
MY_DIR_MYPIMODULE="/root/MyPiDrone/MyPiModule"
MAVPROXY="/usr/local/bin/mavproxy.py"
#
cp ${MY_DIR_MYPIMODULE}/dnsmasq.conf                                    /etc/
cp ${MY_DIR_MYPIMODULE}/hostapd.conf                                    /etc/hostapd/
cp ${MY_DIR_MYPIMODULE}/wifiap.service                                  /lib/systemd/system/
cp ${MY_DIR_MYPIMODULE}/start_rx_and_broadcast_over_ap.sh               /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/start_rx.sh                                     /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/start_gst-launch.sh                             /usr/local/bin/
#
systemctl deamon-reload

