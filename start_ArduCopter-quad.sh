#!/bin/sh
#TITLE# DRONE start ArduCopter-quad
# /lib/systemd/system/ArduCopter-quad.service
# [Unit]
# Description=ArduCopter-quad
# After=rsyslog.service
#
# [Service]
# Type=forking
# ExecStart=/usr/local/bin/start_ArduCopter-quad.sh
# # Nerver use Restart option with ArduCopter-quad
# #Restart=always
# #Restart=on-failure
# #RestartSec=1s
#
# [Install]
# WantedBy=multi-user.target
#
D=`date`
M="/usr/bin/ArduCopter-quad is started."                                  ; echo "$D $M"; echo "$D $M" >> /var/log/ArduCopter-quad.log
M="/usr/bin/ArduCopter-quad here /var/log/ArduCopter-quad.log"            ; echo "$D $M"; echo "$D $M" >> /var/log/ArduCopter-quad.log
M=`strings /usr/bin/ArduCopter-quad |grep -i "Init APM:Copter"|head -n 1` ; echo "$D $M"; echo "$D $M" >> /var/log/ArduCopter-quad.log
nohup /usr/bin/ArduCopter-quad -A /dev/ttyAMA0 -C udp:127.0.0.1:14550 1>>/var/log/ArduCopter-quad.log 2>&1 &
M="/usr/bin/ArduCopter-quad PID $!"                                       ; echo "$D $M"; echo "$D $M" >> /var/log/ArduCopter-quad.log
