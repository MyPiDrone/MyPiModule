#!/bin/bash
################################################################
#### www.MyPiDrone.com
#### Video over Wifibroadcast 2.4Ghz (CH 13) or 2.3Ghz (CH -13)
################################################################

clear
echo ##################TX Script#################
echo Start this script with root authority

#WIDTH=640
#HEIGHT=480
#FPS=60
#
#WIDTH=1920
#HEIGHT=1080
#FPS=15
#
WIDTH=1280
HEIGHT=720
FPS=15
#BITRATE=2000000
BITRATE=4000000
KEYFRAMERATE=60
BLOCK_SIZE=8
FECS=4
PACKET_LENGTH=1024
#PACKET_LENGTH=512
PORT=0
# 10 minutes
#TIMEOUT=60000
# 10 minutes
#TIMEOUT=600000
# 20 minutes
TIMEOUT=1200000
# 40 minutes
#TIMEOUT=2400000

VIDDIR="/home/kevin/fpv/videos"

if [ "$1" = "-h" -o "$1" = "--help" ]; then
	WLAN=""
elif [ "_$1" = "_" ]; then
        WLAN=`/sbin/ifconfig -a |egrep -i '30.*B5.*C2.*11.*83.*22|30.*b5.*c2.*11.*62.*ea'|awk '{print $1}'`
	WLAN="wlan1"
else
        WLAN=$1
fi
if [ "_$2" = "_" ]; then
        CHANNEL="-13"
else
        CHANNEL=$2
fi
if [ "_$3" = "_" ]; then
        OPTION="--VB"
else
        OPTION=$3
fi
echo "WLAN=$WLAN CHANNEL=$CHANNEL OPTION=$OPTION"


C=`ps -ef|grep -v "grep"|grep -ci "raspivid"`
if [ $C -ne 0 ]; then
        echo "_____________________ stop raspivid _______________________________"
        killall raspivid
        echo "killall raspivid RC=$?" 
        sleep 1
fi
C=`ps -ef|grep -v "grep"|grep -v "start_tx.sh"|grep -ci "tx "`
if [ $C -ne 0 ]; then
        echo "_____________________ stop tx _______________________________"
        killall tx
        echo "killall tx RC=$?"
        sleep 1
fi

if [ "_$WLAN" != "_" ] && [ "_$CHANNEL" != "_" ];
then
	# DEBUG
        echo $WLAN choose by user to be the wireless interface TP-LINK 722N >> /var/log/ArduCopter-quad.log
	ip a 2>&1 >> /var/log/ArduCopter-quad.log
	ifconfig -a 2>&1 >> /var/log/ArduCopter-quad.log
        echo $WLAN choose by user to be the wireless interface TP-LINK 722N
	echo Stopping ifplugd
	service ifplugd stop
	killall ifplugd
        echo Setting $WLAN Channel $CHANNEL
        iwconfig $WLAN channel $CHANNEL
        echo Setting wifi adapter in MONITOR mode
        ifconfig $WLAN down && iw dev $WLAN set monitor otherbss fcsfail
        echo Setting maximum Tx Power
        iw reg set BO
        iwconfig $WLAN txpower 30
        ifconfig $WLAN up
	#iwconfig wlan0 rate 54M
	#iw dev wlan0 set bitrates legacy-2.4 54
	#iw dev wlan0 set bitrates ht-mcs-2.4 5
        echo Setting $WLAN Channel $CHANNEL
        iwconfig $WLAN channel $CHANNEL
	sleep
	iwconfig $WLAN
	# DEBUG
        echo Setting $WLAN Channel $CHANNEL >> /var/log/ArduCopter-quad.log
	ip a 2>&1 >> /var/log/ArduCopter-quad.log
	ifconfig -a 2>&1 >> /var/log/ArduCopter-quad.log
	#pour rejouer la video $OPTION = --VRT ou n importe quoi 
	if [ "$OPTION" = "--vrt" -o "_$OPTION" = "_" ]; then
		echo "-------------------------------- Liste des videos ---------------------------"
		du -hs videos
		du -hs videos/*
		echo "-----------------------------------------------------------------------------"
		sleep 3
		# lecture du lien sur la derniere video
		if [ "_$4" = "_" ]; then
			VIDEO="$VIDDIR/Video-Tarot-h264"
		else
			VIDEO="$4"
		fi
        	echo Starting HD Video conversion h264 to mp4 : avconv -stats -y -r $FPS -i $VIDEO -vcodec copy $VIDEO.mp4 ...
		avconv -stats -y -r $FPS -i $VIDEO -vcodec copy $VIDEO.mp4
        	echo Starting HD Video re-transmission for $VIDEO...
		cat $VIDEO | ./tx -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>/dev/null 2>&1
	else
        	echo Starting HD Video transmission and recording...
		VIDEO="$VIDDIR/Video-Tarot-h264-`date +%Y%h%d-%H%M`"
		# creation du lien sur la derniere video
		[ ! -d videos ] && mkdir videos
		touch $VIDEO
		echo "New Video=$VIDEO"
		echo "-------------------------------- Liste des videos ---------------------------"
		du -hs videos
		du -hs $VIDDIR/*
		echo "-----------------------------------------------------------------------------"
		sleep 3
		## pour renverser l image option --vflip
		if [ "$OPTION" = "--vr" ]; then
			ln -sf $VIDEO $VIDDIR/Video-Tarot-h264
			echo "Recording $VIDEO in progress : hit CTRL C to stop"
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o $VIDEO 
		elif [ "$OPTION" = "--vbr" ]; then
			ln -sf $VIDEO $VIDDIR/Video-Tarot-h264
			echo "Recording and broadcasting  $VIDEO in progress : hit CTRL C to stop"
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - | tee $VIDEO | ./tx -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>/dev/null 2>&1
		else
			echo "Broadcasting video (no recording) in progress : hit CTRL C to stop"
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - | ./tx -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>/dev/null 2>&1
		fi
	fi
else
        	echo Please choose the interface of your TP-LINK 722N as the first argument 
        	echo Then the wifi channel as the second argument
       		echo "Usage $0 2.3ghz channel -13 and 2.4Ghz channel 13 :"
        	echo "$0 wlan1 -13 --vb  : video with wifibroadcast (default)"
        	echo "$0 wlan1 -13 --vbr : video with wifibroadcast and recording"
        	echo "$0 wlan1 -13 --vr  : video recording"
        	echo "$0 wlan1 -13 --vrt [video_filemane] : video retransmission and consersion h264 to mp4 (default last video)"
fi

