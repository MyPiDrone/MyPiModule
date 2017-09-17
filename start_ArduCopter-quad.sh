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
M="/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-quad is started."                                  ; echo "$D $M"; echo "$D $M" >> /var/log/ArduCopter-quad.log
M="/opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-quad here /var/log/ArduCopter-quad.log"            ; echo "$D $M"; echo "$D $M" >> /var/log/ArduCopter-quad.log
M=`strings /opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-quad |grep -i "Init APM:Copter"|head -n 1` ; echo "$D $M"; echo "$D $M" >> /var/log/ArduCopter-quad.log
#nohup /usr/bin/ArduCopter-quad -A /dev/ttyAMA0 -C udp:127.0.0.1:14550 1>>/var/log/ArduCopter-quad.log 2>&1 &
#nohup /opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-quad -A udp:127.0.0.1:14550 -C /dev/ttyAMA0 1>>/var/log/ArduCopter-quad.log 2>&1 &
#nohup /opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-quad -A /dev/ttyAMA0 -C udp:127.0.0.1:14550 1>>/var/log/ArduCopter-quad.log 2>&1 &
nohup /opt/ardupilot/navio2/arducopter-3.4/bin/arducopter-quad -C /dev/ttyAMA0 -A udp:127.0.0.1:14550 1>>/var/log/ArduCopter-quad.log 2>&1 &
M="/usr/bin/ArduCopter-quad PID $!"                                       ; echo "$D $M"; echo "$D $M" >> /var/log/ArduCopter-quad.log
