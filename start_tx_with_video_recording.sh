#!/bin/bash 
################################################################
#### www.MyPiDrone.com
#### Video over Wifibroadcast 2.4Ghz (CH 11) or 2.3Ghz (CH -19)
################################################################

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

env

VIDDIR="/root/fpv/videos"
WifiBroadcast_TX="/root/WifiBroadcast/wifibroadcast/tx"
WifiBroadcast_TX="/root/wifibroadcast/tx"

DATE=`date`
PREFIX="#---- $DATE"

clear
echo "$PREFIX ##################TX Script#################"
echo "$PREFIX Start this script with root authority"

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
FPS=60
BITRATE=2000000
BITRATE=4000000
#BITRATE=2000000
KEYFRAMERATE=60
BLOCK_SIZE=8
FECS=4
PACKET_LENGTH=1024
PORT=0
# 10 minutes
#TIMEOUT=60000
# 10 minutes
#TIMEOUT=600000
# 20 minutes
TIMEOUT=1200000
# 40 minutes
#TIMEOUT=2400000

if [ "$1" = "-h" -o "$1" = "--help" ]; then
	WLAN=""
elif [ "_$1" = "_" ]; then
        WLAN=`/sbin/ifconfig -a |egrep -i '30.*B5.*C2.*11.*83.*22|30.*b5.*c2.*11.*62.*ea'|awk '{print $1}'`
	WLAN="wlan1"
else
        WLAN=$1
fi
if [ "_$2" = "_" ]; then
        CHANNEL="-19"
        #CHANNEL="11"
else
        CHANNEL=$2
fi
if [ "_$3" = "_" ]; then
        OPTION="--VB"
else
        OPTION=$3
fi
echo "$PREFIX WLAN=$WLAN CHANNEL=$CHANNEL OPTION=$OPTION"


C=`ps -ef|grep -v "grep"|grep -ci "raspivid"`
if [ $C -ne 0 ]; then
        echo "$PREFIX _____________________ stop raspivid _______________________________"
        killall raspivid
        echo "$PREFIX killall raspivid RC=$?" 
        sleep 1
fi
C=`ps -ef|grep -v "grep"|grep -v "start_tx.sh"|grep -ci "tx "`
if [ $C -ne 0 ]; then
        echo "$PREFIX _____________________ stop $WifiBroadcast_TX _______________________________"
        killall $WifiBroadcast_TX
        echo "$PREFIX killall $WifiBroadcast_TX RC=$?"
        sleep 1
fi

if [ "_$WLAN" != "_" ] && [ "_$CHANNEL" != "_" ];
then
        echo $WLAN choose by user to be the wireless interface TP-LINK 722N
        ip link set $WLAN down
        echo Setting wifi adapter in MONITOR mode
        iw dev $WLAN set monitor otherbss fcsfail
        ip link set $WLAN up
        echo Setting wifi channel $CHANNEL
        sleep 1
        iw dev $WLAN set freq 2357
        #sleep 1
        ### channel -19
        [ "$CHANNEL" = "-19" ] && iw dev $WLAN set freq 2312
        ### channel 11
        [ "$CHANNEL" = "11" ] && iw dev $WLAN set freq 2462
        iw reg set BO
        echo Setting maximum Tx Power
        iwconfig $WLAN txpower 30
        sleep 1
        iwconfig $WLAN
	echo "$PREFIX -----------------------------------------------------------------------------"
	ip a 
	echo "$PREFIX -----------------------------------------------------------------------------"
	ifconfig $WLAN
	echo "$PREFIX -----------------------------------------------------------------------------"
	iwconfig $WLAN
	echo "$PREFIX -----------------------------------------------------------------------------"
	#pour rejouer la video $OPTION = --VRT ou n importe quoi 
	if [ "$OPTION" = "--vrt" -o "_$OPTION" = "_" ]; then
		echo "$PREFIX -------------------------------- Liste des videos ---------------------------"
		du -hs $VIDDIR
		du -hs $VIDDIR/*
		echo "$PREFIX -----------------------------------------------------------------------------"
		sleep 3
		# lecture du lien sur la derniere video
		if [ "_$4" = "_" ]; then
			VIDEO="$VIDDIR/Video-Tarot-h264"
		else
			VIDEO="$4"
		fi
        	#echo "$PREFIX Starting HD Video conversion h264 to mp4 : avconv -stats -y -r $FPS -i $VIDEO -vcodec copy $VIDEO.mp4 ..."
		#avconv -stats -y -r $FPS -i $VIDEO -vcodec copy $VIDEO.mp4
        	echo "$PREFIX Starting HD Video re-transmission for $VIDEO..."
		cat $VIDEO | $WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 
	else
        	echo "$PREFIX Starting HD Video transmission and recording..."
		VIDEO="$VIDDIR/Video-Tarot-h264-`date +%Y%h%d-%H%M`"
		# creation du lien sur la derniere video
		[ ! -d $VIDDIR ] && mkdir -p $VIDDIR
		touch $VIDEO
		echo "$PREFIX New Video=$VIDEO"
		echo "$PREFIX -------------------------------- Liste des videos ---------------------------"
		du -hs $VIDDIR
		du -hs $VIDDIR/*
		echo "$PREFIX -----------------------------------------------------------------------------"
		sleep 3
		## pour renverser l image option --vflip
		if [ "$OPTION" = "--vr" ]; then
			ln -sf $VIDEO $VIDDIR/Video-Tarot-h264
			echo "$PREFIX Recording $VIDEO in progress : hit CTRL C to stop"
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o $VIDEO 
		elif [ "$OPTION" = "--vbr" ]; then
			ln -sf $VIDEO $VIDDIR/Video-Tarot-h264
			echo "$PREFIX Recording and broadcasting  $VIDEO in progress : hit CTRL C to stop"
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - | tee $VIDEO | $WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>/dev/null 2>/var/log/myvideo.err
		else
			echo "$PREFIX Broadcasting video (no recording) in progress : hit CTRL C to stop"
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - | $WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 
		fi
	fi
else
        	echo "$PREFIX Please choose the interface of your TP-LINK 722N as the first argument" 
        	echo "$PREFIX Then the wifi channel as the second argument"
       		echo "$PREFIX Usage $0 2.3ghz channel -19 and 2.4Ghz channel 11 :"
        	echo "$PREFIX $0 wlan1 -19 --vb  : video with wifibroadcast (default)"
        	echo "$PREFIX $0 wlan1 -19 --vbr : video with wifibroadcast and recording"
        	echo "$PREFIX $0 wlan1 -19 --vr  : video recording"
        	echo "$PREFIX $0 wlan1 -19 --vrt [video_filemane] : video retransmission and consersion h264 to mp4 (default last video)"
fi

