#!/bin/sh 
#####################################################################################################
#### www.MyPiDrone.com
####-------------------------------------------------------------------------------------------------
#### manage ArduCopter-quad and Video Wifibroadcast (CH 13 = 2.4.Ghz , CH -13 = 2.3Ghz)
####-------------------------------------------------------------------------------------------------
#### Started by /etc/rc.local
#### sh -x /usr/local/bin/StartArduCopter-quad.sh --vbr >> /var/log/StartArduCopter-quad.log 2>&1
####-------------------------------------------------------------------------------------------------
#### $1 options
#### --vb  : video with wifibroadcast
#### --vbr : video with wifibroadcast and recording
#### --vr  : video recording
#### --vrt : video retransmission
####-------------------------------------------------------------------------------------------------
#### Beta test :
#### $2 option
#### --ap : video Broadcast and recording over Wifi AP
#####################################################################################################

OPT1=`echo $1|tr '[:upper:]' '[:lower:]'`
OPT2=`echo $2|tr '[:upper:]' '[:lower:]'`
OPT3=`echo $3|tr '[:upper:]' '[:lower:]'`

if [ "$OPT2" = "--ap" -o "$OPT3" = "--ap" ]; then
	CMD_START_VIDEO="./start_tx_with_video_recording_broadcast_over_ap.sh"
else
	CMD_START_VIDEO="./start_tx_with_video_recording.sh"
fi

# DEBUG
ip a 2>&1 >> /var/log/ArduCopter-quad.log
ifconfig -a 2>&1 >> /var/log/ArduCopter-quad.log

#WLAN=`/sbin/ifconfig -a |egrep -i '30.*B5.*C2.*11.*83.*22|30.*b5.*c2.*11.*62.*ea'|awk '{print $1}'`
WLAN="wlan1"

if [ "_$WLAN" = "_" ]; then
	WLAN="wlan1"
	MSG="Dynamic Select wlan interface failed : set default  $WLAN"
	echo "$MSG" ; echo "$MSG" >> /var/log/start_tx.log ; echo "$MSG" >> /var/log/ArduCopter-quad.log
else
	MSG="Dynamic Select wlan interface success : set default  $WLAN"
	echo "$MSG" ; echo "$MSG" >> /var/log/start_tx.log ; echo "$MSG" >> /var/log/ArduCopter-quad.log
fi

#### 2.4Ghz
CHANNEL="13"
#### 2.3Ghz
CHANNEL="-13"

OPTION="null"
if [ "_$OPT1" = "_" ];then 
	OPTION="null"
elif [ "$OPT1" = "--vb" ];then 
	OPTION="VB"
elif [ "$OPT1" = "--vbr" ];then 
	OPTION="VBR"
elif [ "$OPT1" = "--vr" ];then 
	OPTION="VR"
elif [ "$OPT1" = "--vrt" ];then 
	OPTION="VRT"
elif [ "$OPT1" = "--help" -o "$OPT1" = "-h" ];then 
	echo "Usage $0"
	echo "$0 --vb  [--ap] : video with wifibroadcast"
	echo "$0 --vbr [--ap] : video with wifibroadcast and recording"
	echo "$0 --vr  [--ap] : video recording"
	echo "$0 --vrt [video_filename] [--ap] : video retransmission (default last video)"
	echo "defaults : no video"
	echo "--ap : video over Wifi Access Point : default wifibroadcast"
	exit
fi

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export PATH

C=`ps -ef|grep "ArduCopter-quad"|grep -ci "ttyUSB0"`
if [ $C -ne 0 ]; then
	echo "_____________________ stop ArduCopter-quad _______________________________" >> /var/log/ArduCopter-quad.log
	killall ArduCopter-quad
	echo "killall ArduCopter-quad RC=$?" >> /var/log/ArduCopter-quad.log
	sleep 1
fi
C=`ps -ef|grep "mavproxy.py"|grep -ci "ttyUSB0"`
if [ $C -ne 0 ]; then
	echo "_____________________ stop mavproxy.py ___________________________________" >> /var/log/ArduCopter-quad.log
	killall mavproxy.py
	echo "killall mavproxy.py RC=$?" >> /var/log/ArduCopter-quad.log
	sleep 1
fi

###################################
CMD1="/usr/bin/ArduCopter-quad -A /dev/ttyAMA0 -C udp:127.0.0.1:14550"
CMD2="/usr/local/bin/mavproxy.py --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600 --daemon --show-errors --default-modules='MyPiModule'"
###################################

C1=`ps -ef|grep "ArduCopter-quad"|grep -ci "ttyUSB0"`
C2=`ps -ef|grep "mavproxy.py"|grep -ci "ttyUSB0"`
if [ $C1 -eq 0 -a $C2 -eq 0 ]; then
	echo "_____________________ start ArduCopter-quad _______________________________" >> /var/log/ArduCopter-quad.log
	#env >> /var/log/ArduCopter-quad.log
	echo "---" >> /var/log/ArduCopter-quad.log
	date >> /var/log/ArduCopter-quad.log
	###########################################################
	# ArduCopter-quad
	###########################################################
	MSG1="$CMD1 is started"
	echo "$MSG1" ; echo "$MSG1" >> /var/log/ArduCopter-quad.log
	nohup $CMD1 1> /var/log/ArduCopter-quad2.log 2>&1 &
	echo "ArduCopter-quad started PID=$!" >> /var/log/ArduCopter-quad.log
	ps -ef|grep "ArduCopter-quad"|grep -i "ttyUSB0" >> /var/log/ArduCopter-quad.log
	###########################################################
	# MAVProxy
	###########################################################
	sleep 8
	MSG2="$CMD2 is started"
	echo "$MSG2" ; echo "$MSG2" >> /var/log/ArduCopter-quad.log
	nohup $CMD2 1> /var/log/ArduCopter-quad-mavproxy.log 2>&1 &
	echo "mavproxy.py started PID=$!" >> /var/log/ArduCopter-quad.log
	ps -ef|grep "mavproxy.py"|grep -i "ttyUSB0" >> /var/log/ArduCopter-quad.log
	
else
	echo "_____________________ start ArduCopter-quad failed _________________________" >> /var/log/ArduCopter-quad.log
	date >> /var/log/ArduCopter-quad.log
	echo "$CMD1 C1=$C1 is already running : exit $0" >> /var/log/ArduCopter-quad.log
	echo "$CMD2 C2=$C2 is already running : exit $0" >> /var/log/ArduCopter-quad.log
fi


C=`ps -ef|grep -v "grep"|grep -ci "raspivid"`
if [ $C -ne 0 ]; then
	echo "_____________________ stop raspivid _______________________________" >> /var/log/ArduCopter-quad.log
	killall raspivid
	echo "killall raspivid RC=$?" >> /var/log/ArduCopter-quad.log
	sleep 1
fi
C=`ps -ef|grep -v "grep"|grep -ci "tx "`
if [ $C -ne 0 ]; then
	echo "_____________________ stop tx _______________________________" >> /var/log/ArduCopter-quad.log
	killall tx
	echo "killall tx RC=$?" >> /var/log/ArduCopter-quad.log
	sleep 1
fi
cd /home/kevin/fpv
if [ "$OPTION" = "VB" ];then 
	date > /var/log/start_tx.log
	MSG="$CMD_START_VIDEO $WLAN $CHANNEL is started"
	echo "$MSG" ; echo "$MSG" >> /var/log/start_tx.log ; echo "$MSG" >> /var/log/ArduCopter-quad.log
	nohup $CMD_START_VIDEO $WLAN $CHANNEL > /var/log/start_tx.log 2>&1 &
elif [ "$OPTION" = "VBR" ];then 
	date > /var/log/start_tx.log
	MSG="$CMD_START_VIDEO $WLAN $CHANNEL is started"
	echo "$MSG" ; echo "$MSG" >> /var/log/start_tx.log ; echo "$MSG" >> /var/log/ArduCopter-quad.log
	nohup $CMD_START_VIDEO $WLAN $CHANNEL --vbr >> /var/log/start_tx.log 2>&1 &
elif [ "$OPTION" = "VR" ];then 
	date > /var/log/start_tx.log
	MSG="$CMD_START_VIDEO $WLAN $CHANNEL video recording only is started"
	echo "$MSG" ; echo "$MSG" >> /var/log/start_tx.log ; echo "$MSG" >> /var/log/ArduCopter-quad.log
	nohup $CMD_START_VIDEO $WLAN $CHANNEL --vr >> /var/log/start_tx.log 2>&1 &
elif [ "$OPTION" = "VRT" ];then 
	date > /var/log/start_tx.log
	MSG="$CMD_START_VIDEO $WLAN $CHANNEL $2 retransmision is started"
	echo "$MSG" ; echo "$MSG" >> /var/log/start_tx.log ; echo "$MSG" >> /var/log/ArduCopter-quad.log
	nohup $CMD_START_VIDEO $WLAN $CHANNEL --vrt $2 >> /var/log/start_tx.log 2>&1 &
fi

exit 0
