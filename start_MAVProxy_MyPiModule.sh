#!/bin/sh
#TITLE# start MAVProxy MyPiModule
# /lib/systemd/system/mavproxy.service 
# [Unit]
# Description=mavproxy
# After=ArduCopter-quad.service
#
# [Service]
# Type=forking
# ExecStart=/usr/local/bin/start_MAVProxy_MyPiModule.sh
# #Restart=always
# Restart=on-failure
# RestartSec=5s
#
# [Install]
# WantedBy=multi-user.target
# 
echo " "
echo "_______________________________________________________" >> /var/log/ArduCopter-quad-mavproxy.log
MSG="MAVProxy is started and MyPiModule,mode modules loaded."
echo $MSG ; echo $MSG >> /var/log/ArduCopter-quad-mavproxy.log
MSG="Log here /var/log/ArduCopter-quad-mavproxy.log"
echo $MSG ; echo $MSG >> /var/log/ArduCopter-quad-mavproxy.log
date >> /var/log/ArduCopter-quad-mavproxy.log
nohup /usr/bin/python /usr/local/bin/mavproxy.py --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600 --daemon --show-errors --default-modules='MyPiModule,mode' 1>>/var/log/ArduCopter-quad-mavproxy.log 2>&1 &
MSG="MAVProxy started PID $!"
echo $MSG ; echo $MSG >> /var/log/ArduCopter-quad-mavproxy.log
