#!/bin/sh
###########################################################
####### www.MyPiDrone.com  
#TITLE# DRONE install MAVProxy module MyPiModule
#--------------------------------------------------------
# from zeroconf on hdmi console
# login pi mdp raspberry
# sudo su -
# passwd root to change root password
# passwd pi  to change pi password
# raspi-config
# extend filesystem and reboot
# set hostname navio
# set wifi country FR
# set timezone GMT+1
# enable ssh
# set keyboard FR
# set langage 
# set picamera enable
# reboot
#----------------------------------------------------------------------------------------------------
# country BO: DFS-UNSET (2302 - 2742 @ 40), (N/A, 30), (N/A) (4910 - 6110 @ 160), (N/A, 30), (N/A)
# to use 2302 wifi broadcast
# change country=BO in file /boot/wpa_supplicant.conf
# reboot
#-------------------------------------------------------
# change  /etc/ssh/sshd_config
# PermitRootLogin yes
# systemctl restart ssh
#--------------------------------------------------------
# emlidtool ardupilot
# set copter etc.
# emlidtool info
# emlidtool rcio check
# emlidtool rcio update
#-------------------------------------------------------
# cd /root
# git clone  https://github.com/emlid/Navio2.git
#--------------------------------------------------------
# change /etc/default/arducopter
# TELEM1="-A udp:127.0.0.1:14550"
# TELEM2="-C /dev/ttyAMA0"
# systemctl daemon-reload
# systemctl restart arducopter
# execute mavproxy.py to check connection with arducopter
#--------------------------------------------------------
# cd /root
# hg clone https://bitbucket.org/befi/wifibroadcast
# cd wifibroadcast
# make
#--------------------------------------------------------
# mkdir /root/MyPiDrone
# cd /root/MyPiDrone
# git clone https://github.com/MyPiDrone/MyPiModule.git
# add cd /root/MyPiDrone/MyPiModule in /root/.bashrc
#--------------------------------------------------------
# ln -s  MyPiModule_build_and_git_update.sh build.sh
# vi wpa_supplicant.conf
# cp wpa_supplicant.conf /boot
#--------------------------------------------------------
# apt-get install locate
# updatedb
#--------------------------------------------------------
# disable 2.4ghz Wifi RPI3 intwifi0 interface and use only 5.8ghZ usb dongle CSL
# cp blacklist-brcmfmac.conf /etc/modprobe.d/
#--------------------------------------------------------
# cp 70-persistent-net.rules /lib/udev/rules.d/
# cp /etc/network/interfaces /etc/network/interfaces.old
# cp interfaces /etc/network/interfaces
# reboot
#--------------------------------------------------------
# pip install psutil picamera
###########################################################
date=`date +'%Y-%m-%d'`
MY_DIR_MYPIMODULE="/root/MyPiDrone/MyPiModule"
MAVPROXY="/usr/local/bin/mavproxy.py"
cp ${MY_DIR_MYPIMODULE}/mavproxy_MyPiModule.py /usr/local/lib/python2.7/dist-packages/MAVProxy/modules/mavproxy_MyPiModule.py
#
#OBSOLTETE#cp ${MY_DIR_MYPIMODULE}/ArduCopter-quad.service                            /lib/systemd/system/
#OBSOLTETE#cp ${MY_DIR_MYPIMODULE}/rc.local                                           /etc/
#
cp ${MY_DIR_MYPIMODULE}/mavproxy.service                                   /lib/systemd/system/
cp ${MY_DIR_MYPIMODULE}/start_MAVProxy_MyPiModule.sh                       /usr/local/bin/
#
#OBSOLTETE#cp ${MY_DIR_MYPIMODULE}/start_ArduCopter-quad.sh                           /usr/local/bin/
#
#
#--------------------------------------------
# used by  mavproxy_MyPiModule.py
#--------------------------------------------
cp ${MY_DIR_MYPIMODULE}/start_tx_and_recording_with_picamera_video_input.sh                /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/manage_network.sh                                  /usr/local/bin/
cp ${MY_DIR_MYPIMODULE}/MyPiStatusTextSendWithPipeIn.py                            /usr/local/bin/
#
#NOT_USED#cp ${MY_DIR_MYPIMODULE}/start_tx_and_recording_with_raspivid_video_input_on_wifiap.sh      /usr/local/bin/
#NOT_USED#cp ${MY_DIR_MYPIMODULE}/start_tx_and_recording_with_raspivid_video_input.sh                /usr/local/bin/
#NOT_USED#cp ${MY_DIR_MYPIMODULE}/start_tx_with_video_recording_broadcast_over_ap.sh /usr/local/bin/
#
cp ${MY_DIR_MYPIMODULE}/show_modules.sh                                    /usr/local/bin/
#NOT_USED#cp ${MY_DIR_MYPIMODULE}/start_wlan1_mode_monitor.sh                        /usr/local/bin/
#NOT_USED#cp ${MY_DIR_MYPIMODULE}/start_wlan1_mode_managed.sh                        /usr/local/bin/
#
systemctl daemon-reload
systemctl enable mavproxy
#
cd ${MY_DIR_MYPIMODULE}
ln -sf MyPiModule_build_and_git_update.sh build.sh
pip install psutil
pip install picamera
C=`ps -ef|grep -v grep|grep -c MyPiStatusTextSendWithPipeIn.py`
if [ $C -eq 0 ]; then
        nohup /usr/bin/python /usr/local/bin/MyPiStatusTextSendWithPipeIn.py /tmp/MyPiStatusTextSend.pipein > /var/log/MyPiStatusTextSendWithPipeIn.log 2>&1 &
	sleep 1
fi
echo "/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors"
### load only MyPiModule and mode
/usr/bin/python $MAVPROXY --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors
##THE END##
