#!/bin/sh
#TITLE# DRONE manage start/stop video streaming and recording called by MyPiModule
# [Unit]
# Description=myvideo
# After=multi-user.target
#
# [Service]
# Type=forking
# ExecStart=/usr/local/bin/manage_video.sh start
# ExecStop=/usr/local/bin/manage_video.sh stop
# #KillMode=process
# #Restart=on-failure
#
#[Install]
# WantedBy=multi-user.target
#

case "$1" in
  start)
        nohup /usr/local/bin/start_tx_with_video_recording_and_picamera.sh wlan1 -19 --vbr 1>>/var/log/start_tx_with_video_recording.log 2>&1 &
        echo "Video is started"
        ;;
  stop)
        killall raspivid
        WifiBroadcast_TX="/root/WifiBroadcast/wifibroadcast/tx" ; killall $WifiBroadcast_TX
        WifiBroadcast_TX="/root/wifibroadcast/tx" ; killall $WifiBroadcast_TX
        echo "Video is stopped"
        ;;
  status)
        RC=0
	PID=`pgrep tx`
	if [ $? -eq 0 ]; then
		RC=0 ; echo "tx is running $PID"
        else
		RC=1 ; echo "tx is not running"
        fi
	PID=`pgrep raspivid`
	if [ $? -eq 0 ]; then
		RC=0 ; echo "raspivid is running pid $PID"
	else
		RC=1 ; echo "raspivid is not running"
	fi
        exit $RC
        ;;
  *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac

exit 0

