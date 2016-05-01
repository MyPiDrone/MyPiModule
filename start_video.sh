#!/bin/sh
# /lib/systemd/system/myvideo.service                                                                                                                                                             
# [Unit]
# Description=myvideo
# After=multi-user.target
#
# [Service]
# Type=forking
# ExecStart=/usr/local/bin/start_video.sh
# ExecStop=/usr/local/bin/stop_video.sh
# #KillMode=process
# #Restart=on-failure
#
#[Install]
# WantedBy=multi-user.target
#
nohup /usr/local/bin/start_tx_with_video_recording.sh wlan1 -13 --vbr 1>/var/log/start_tx_with_video_recording.log 2>&1 &
echo "Video is started"
exit 0
