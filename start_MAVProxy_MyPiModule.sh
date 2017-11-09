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
#-----------------------------
# TODO
# apt-get install python-psutil
# apt-get install python-picamera python-picamera-docs
# pip install MAVProxy --upgrade
#-----------------------------
#
echo " "
echo "_______________________________________________________" >> /var/log/mavproxy_MyPiModule.log
MSG="MAVProxy is started and MyPiModule,mode modules loaded."
echo $MSG ; echo $MSG >> /var/log/mavproxy_MyPiModule.log
MSG="Log here /var/log/mavproxy_MyPiModule.log"
echo $MSG ; echo $MSG >> /var/log/mavproxy_MyPiModule.log
C=`ps -ef|grep -v grep|grep -c MyPiStatusTextSendWithPipeIn.py`
if [ $C -eq 0 ]; then
	nohup /usr/bin/python /usr/local/bin/MyPiStatusTextSendWithPipeIn.py /tmp/MyPiStatusTextSend.pipein /var/log/MyPiStatusTextSendWithPipeIn.log 2>&1 &
	sleep 1
fi
date >> /var/log/mavproxy_MyPiModule.log
nohup /usr/bin/python /usr/local/bin/mavproxy.py --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600 --daemon --show-errors --default-modules='MyPiModule,mode' 1>>/var/log/mavproxy_MyPiModule.log 2>&1 &
MSG="MAVProxy started PID $!"
echo $MSG ; echo $MSG >> /var/log/mavproxy_MyPiModule.log
