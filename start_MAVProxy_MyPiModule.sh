#!/bin/sh
#TITLE# DRONE start MAVProxy MyPiModule
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
echo "_______________________________________________________" >> /var/log/mavproxy_MyPiModule.log
MSG="MAVProxy is started and MyPiModule,mode modules loaded."
echo $MSG ; echo $MSG >> /var/log/mavproxy_MyPiModule.log
MSG="Log here /var/log/mavproxy_MyPiModule.log"
echo $MSG ; echo $MSG >> /var/log/mavproxy_MyPiModule.log
date >> /var/log/mavproxy_MyPiModule.log
nohup /usr/bin/python /usr/local/bin/mavproxy.py --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600 --daemon --show-errors --default-modules='MyPiModule,mode' 1>>/var/log/mavproxy_MyPiModule.log 2>&1 &
MSG="MAVProxy started PID $!"
echo $MSG ; echo $MSG >> /var/log/mavproxy_MyPiModule.log
sleep 5
nohup /usr/local/bin/start_tx_and_recording_with_picamera_video_input.sh wlan1 -19 --vbr 1>>/var/log/start_tx_with_video_recording.log 2>&1 &
MSG="TX video started PID $!"
echo $MSG ; echo $MSG >> /var/log/mavproxy_MyPiModule.log

