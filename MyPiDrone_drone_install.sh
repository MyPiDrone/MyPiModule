#!/bin/sh
###########################################################
####### www.MyPiDrone.com  
#TITLE# DRONE install MAVProxy module MyPiModule
###########################################################
date=`date +'%Y-%m-%d'`
MY_DIR_MYPIMODULE="/root/MyPiDrone/MyPiModule"
MAVPROXY="/usr/local/bin/mavproxy.py"
cp ${MY_DIR_MYPIMODULE}/mavproxy_MyPiModule.py /usr/local/lib/python2.7/dist-packages/MAVProxy/modules/mavproxy_MyPiModule.py
#
cp ${MY_DIR_MYPIMODULE}/ArduCopter-quad.service                            /lib/systemd/system/
cp ${MY_DIR_MYPIMODULE}/mavproxy.service                                   /lib/systemd/system/
cp ${MY_DIR_MYPIMODULE}/rc.local                                           /etc/
#
cp ${MY_DIR_MYPIMODULE}/start_MAVProxy_MyPiModule.sh                       /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/start_ArduCopter-quad.sh                           /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/start_tx_and_recording_with_picamera_video_input.sh                /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/start_tx_and_recording_with_raspivid_video_input_on_wifiap.sh      /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/start_tx_and_recording_with_raspivid_video_input.sh                /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/manage_network.sh                                  /usr/local/bin/
#cp ${MY_DIR_MYPIMODULE}/start_tx_with_video_recording_broadcast_over_ap.sh /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/show_modules.sh                                    /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/start_wlan1_mode_monitor.sh                        /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/start_wlan1_mode_managed.sh                        /usr/local/bin/
#
systemctl deamon-reload
#
cd ${MY_DIR_MYPIMODULE}
ln -sf MyPiModule_build_and_git_update.sh build.sh
echo "/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors"
### load only MyPiModule and mode
/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors
