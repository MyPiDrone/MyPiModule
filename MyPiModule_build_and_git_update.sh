#!/bin/sh
###########################################################
####### www.MyPiDrone.com  
#TITLE# DRONE build MAVProxy module MyPiModule
###########################################################
date=`date +'%Y-%m-%d'`
MY_DIR_MYPIMODULE="/root/MyPiDrone/MyPiModule"
MAVPROXY="/usr/local/bin/mavproxy.py"
if [ ! -f /usr/local/lib/python2.7/dist-packages/MAVProxy/modules/mavproxy_MyPiModule.py ]; then
	cp ${MY_DIR_MYPIMODULE}/mavproxy_MyPiModule.py /usr/local/lib/python2.7/dist-packages/MAVProxy/modules
fi
vi /usr/local/lib/python2.7/dist-packages/MAVProxy/modules/mavproxy_MyPiModule.py
#
cp /usr/local/lib/python2.7/dist-packages/MAVProxy/modules/mavproxy_MyPiModule.py ${MY_DIR_MYPIMODULE}
#
cp /lib/systemd/system/ArduCopter-quad.service                       ${MY_DIR_MYPIMODULE}
cp /lib/systemd/system/mavproxy.service                              ${MY_DIR_MYPIMODULE}
cp /etc/rc.local                                                     ${MY_DIR_MYPIMODULE}
#
cp /var/APM/ArduCopter.stg                                           ${MY_DIR_MYPIMODULE}
#
cp /usr/local/bin/start_MAVProxy_MyPiModule.sh                       ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/start_ArduCopter-quad.sh                           ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/start_tx_and_recording_with_picamera_video_input.sh                ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/start_tx_and_recording_with_raspivid_video_input_on_wifiap.sh      ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/start_tx_and_recording_with_raspivid_video_input.sh                ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/MyPiCamera_sample.py                                               ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/MyPiCamera_sample.sh                                               ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/manage_network.sh                                  ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/show_modules.sh                                    ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/start_wlan1_mode_monitor.sh                        ${MY_DIR_MYPIMODULE}
cp /usr/local/bin/start_wlan1_mode_managed.sh                        ${MY_DIR_MYPIMODULE}
#
cd ${MY_DIR_MYPIMODULE}
VERSION=`grep "self.myversion" mavproxy_MyPiModule.py|head -n 1|awk -F'"' '{print "v"$2}'`
echo "mavproxy_MyPiModule.py VERSION=$VERSION"
LIST="mav.parm mavproxy_MyPiModule.py rc.local ArduCopter-quad.service mavproxy.service README.md start_MAVProxy_MyPiModule.sh start_ArduCopter-quad.sh show_modules.sh start_rx.sh start_ap.sh start_rx_and_broadcast_over_ap.sh start_rx_and_broadcast_over_ap_with_diversity.sh start_tx_and_recording_with_picamera_video_input.sh start_tx_and_recording_with_raspivid_video_input.sh start_tx_and_recording_with_raspivid_video_input_on_wifiap.sh start_wlan1_mode_monitor.sh start_wlan1_mode_managed.sh download_ArduCopter-quad.sh ArduCopter.stg wifiap.service hostapd.conf dnsmasq.conf manage_network.sh MyPiModule_build_and_git_update.sh MyPiDrone_drone_install.sh MyPiDrone_gcs_install.sh telem1.lua telem2.lua MyPiStatusText_sample.py MyPiCamera_sample.py MyPiCamera_sample.sh MyPiCamera_sample2.py MyPiCamera_sample2.sh MyPiCamera_sample3.py MyPiCamera_sample3.sh MyPiCamera_sample4.py MyPiCamera_sample4.sh MyPiCamera_sample5.py MyPiCamera_sample5.sh MyPiDrone1_Tarot_MyPiModule_Radio_Control_v1.1.dia MyPiDrone1_Tarot_MyPiModule_Radio_Control_v1.1.jpeg MyPiDrone1_Tarot_Data_Flow_Diagram_V1.2.dia MyPiDrone1_Tarot_Data_Flow_Diagram_V1.2.jpeg 70-persistent-net.rules 75-persistent-net-generator.rules wpa_supplicant.conf interfaces"
git config --global status.showUntrackedFiles no
#git add $LIST
#git commit -i $LIST
for F in $LIST
do
	git add $F
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
#nohup /usr/local/bin/start_tx_and_recording_with_picamera_video_input.sh wlan1 -19 --vbr 1>>/var/log/start_tx_with_video_recording.log 2>&1 &
#MSG="TX video started PID $!"
#echo $MSG
echo "/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors"
### load only MyPiModule and mode
/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors 
### load all modules
### /usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --show-errors
### to QtGstreamerHUD emlid over AP on ubuntu PC
###/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=udp:10.0.0.12:14550 --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors

