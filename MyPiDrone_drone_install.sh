#!/bin/sh
###########################################################
####### www.MyPiDrone.com  
#TITLE# DRONE install MAVProxy module MyPiModule
###########################################################
date=`date +'%Y-%m-%d'`
MY_MAVPROXY_DIR="/root/MyPiDrone/MAVProxy-1.4.43"
MY_DIR_MYPIDRONE="/root/MyPiDrone"
MY_DIR_MYPIMODULE="/root/MyPiDrone/MyPiModule"
cd ${MY_DIR_MYPIDRONE}
cp MyPiModule/mavproxy_MyPiModule.py  ${MY_MAVPROXY_DIR}/MAVProxy/modules/mavproxy_MyPiModule.py
#
cp MyPiModule/ArduCopter-quad.service                            /lib/systemd/system/
cp MyPiModule/myvideo.service                                    /lib/systemd/system/
cp MyPiModule/mavproxy.service                                   /lib/systemd/system/
cp MyPiModule/rc.local                                           /etc/
#
cp MyPiModule/start_MAVProxy_MyPiModule.sh                       /usr/local/bin/
cp MyPiModule/start_ArduCopter-quad.sh                           /usr/local/bin/
cp MyPiModule/start_tx_with_video_recording.sh                   /usr/local/bin/
cp MyPiModule/start_video.sh                                     /usr/local/bin/
cp MyPiModule/stop_video.sh                                      /usr/local/bin/
cp MyPiModule/start_network.sh                                   /usr/local/bin/
cp MyPiModule/stop_network.sh                                    /usr/local/bin/
cp MyPiModule/start_tx_with_video_recording_broadcast_over_ap.sh /usr/local/bin/
cp MyPiModule/show_modules.sh                                    /usr/local/bin/
cp MyPiModule/start_wlan1_mode_monitor.sh                        /usr/local/bin/
cp MyPiModule/start_wlan1_mode_managed.sh                        /usr/local/bin/
#
cd ${MY_DIR_MYPIMODULE}
ln -sf MyPiModule_build_and_git_update.sh build.sh
echo "/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors"
### load only MyPiModule and mode
/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors
