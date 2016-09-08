#!/bin/sh
###########################################################
####### www.MyPiDrone.com  
#TITLE# DRONE build MAVProxy module MyPiModule
###########################################################
date=`date +'%Y-%m-%d'`
MY_MAVPROXY_DIR="/root/MyPiDrone/MAVProxy-1.4.43"
MY_DIR_MYPIDRONE="/root/MyPiDrone"
MY_DIR_MYPIMODULE="/root/MyPiDrone/MyPiModule"
#MAVPROXY="${MY_MAVPROXY_DIR}/MAVProxy/mavproxy.py"
MAVPROXY="/usr/local/bin/mavproxy.py"
vi ${MY_MAVPROXY_DIR}/MAVProxy/modules/mavproxy_MyPiModule.py
cd ${MY_MAVPROXY_DIR}
python setup.py build install
[ $? -ne 0 ] && exit 1
cd ${MY_DIR_MYPIDRONE}
cp ${MY_MAVPROXY_DIR}/MAVProxy/modules/mavproxy_MyPiModule.py        MyPiModule/
#
cp /lib/systemd/system/ArduCopter-quad.service                       MyPiModule/
#cp /lib/systemd/system/myvideo.service                               MyPiModule/
cp /lib/systemd/system/mavproxy.service                              MyPiModule/
cp /etc/rc.local                                                     MyPiModule/
#
cp /var/APM/ArduCopter.stg                                           MyPiModule/
#
cp /usr/local/bin/start_MAVProxy_MyPiModule.sh                       MyPiModule/
cp /usr/local/bin/start_ArduCopter-quad.sh                           MyPiModule/
#cp /usr/local/bin/start_tx_with_video_recording.sh                   MyPiModule/
cp /usr/local/bin/start_tx_with_video_recording_and_picamera.sh      MyPiModule/
#cp /usr/local/bin/Mypicamera.py                                      MyPiModule/
#cp /usr/local/bin/manage_video.sh                                    MyPiModule/
cp /usr/local/bin/manage_network.sh                                  MyPiModule/
cp /usr/local/bin/start_tx_with_video_recording_broadcast_over_ap.sh MyPiModule/
cp /usr/local/bin/show_modules.sh                                    MyPiModule/
cp /usr/local/bin/start_wlan1_mode_monitor.sh                        MyPiModule/
cp /usr/local/bin/start_wlan1_mode_managed.sh                        MyPiModule/
#
cd ${MY_DIR_MYPIMODULE}
VERSION=`grep "self.myversion" mavproxy_MyPiModule.py|head -n 1|awk -F'"' '{print "v"$2}'`
echo "mavproxy_MyPiModule.py VERSION=$VERSION"
LIST="mav.parm mavproxy_MyPiModule.py rc.local ArduCopter-quad.service mavproxy.service README.md start_MAVProxy_MyPiModule.sh start_ArduCopter-quad.sh start_tx_with_video_recording.sh start_tx_with_video_recording_broadcast_over_ap.sh start_tx_with_video_recording_and_picamera.sh show_modules.sh start_rx.sh start_ap.sh start_rx_and_broadcast_over_ap.sh start_wlan1_mode_monitor.sh start_wlan1_mode_managed.sh download_ArduCopter-quad.sh ArduCopter.stg wifiap.service hostapd.conf dnsmasq.conf manage_network.sh MyPiModule_build_and_git_update.sh MyPiDrone_drone_install.sh MyPiDrone_gcs_install.sh telem1.lua telem2.lua"
git config --global status.showUntrackedFiles no
git add $LIST
#git commit -i $LIST
for F in $LIST
do
	DESC=`grep "^#TITLE#" $F|cut -d' ' -f2-`
	if [ "_$DESC" = "_" ]; then
		git commit $F -m "$VERSION $date"
		echo "git commit $F -m $VERSION $date RC=$?"
	else
		git commit $F -m "$VERSION $date $DESC"
		echo "git commit $F -m $VERSION $date $DESC RC=$?"
	fi
done
git pull
git push -f
#git push
cd ${MY_DIR_MYPIMODULE}
systemctl stop mavproxy
nohup /usr/local/bin/start_tx_with_video_recording_and_picamera.sh wlan1 -19 --vbr 1>>/var/log/start_tx_with_video_recording.log 2>&1 &
MSG="TX video started PID $!"
echo "TX Video is started"
echo "/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors"
### load only MyPiModule and mode
/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors 
### load all modules
###/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --show-errors
### to QtGstreamerHUD emlid over AP on ubuntu PC
###/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=udp:10.0.0.12:14550 --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors

