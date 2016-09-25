#!/bin/bash 
#####################################################################################
####### www.MyPiDrone.com
#TITLE# DRONE PiCamera Video ouput over Wifibroadcast 2.4Ghz (CH 11) or 2.3Ghz (CH -19)
#####################################################################################

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

env

VIDDIR="/root/fpv/videos"
WifiBroadcast_TX="/root/WifiBroadcast/wifibroadcast/tx"
WifiBroadcast_TX="/root/wifibroadcast/tx"
log="/var/log/start_tx.log"
pipeout='/tmp/MyPiCamera.pipeout'
mkfifo $pipeout

DATE=`date`
PREFIX="#---- $DATE"

clear
echo "$PREFIX ##################TX Script#################"
echo "$PREFIX Start this script with root authority"

BLOCK_SIZE=8
FECS=4
PACKET_LENGTH=1024
PORT=0

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
                # lecture du lien sur la derniere video
                if [ "_$4" = "_" ]; then
                        VIDEO="$VIDDIR/Video-Tarot-h264"
                else
                        VIDEO="$4"
                fi
                #echo "$PREFIX Starting HD Video conversion h264 to mp4 : avconv -stats -y -r $FPS -i $VIDEO -vcodec copy $VIDEO.mp4 ..."
                #avconv -stats -y -r $FPS -i $VIDEO -vcodec copy $VIDEO.mp4
                echo "$PREFIX Starting HD Video re-transmission for $VIDEO..."
                $WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>$log 2>&1 < $pipeout
        else
                echo "$PREFIX Starting HD Video transmission and recording..."
                VIDEO="$VIDDIR/Video-Tarot-`date +%Y-%m-%d_%H:%M`.h264"
                # creation du lien sur la derniere video
                [ ! -d $VIDDIR ] && mkdir -p $VIDDIR
                echo "$PREFIX New Video=$VIDEO"
                echo "$PREFIX -------------------------------- Liste des videos ---------------------------"
                du -hs $VIDDIR
                du -hs $VIDDIR/*
                echo "$PREFIX -----------------------------------------------------------------------------"
                if [ "$OPTION" = "--vr" ]; then
                	touch $VIDEO
                        ln -sf $VIDEO $VIDDIR/Video-Tarot-h264
                        echo "$PREFIX Recording $VIDEO in progress : hit CTRL C to stop"
                        tee $VIDEO 1>$log 2>&1 < $pipeout
                elif [ "$OPTION" = "--vbr" ]; then
                	touch $VIDEO
                        ln -sf $VIDEO $VIDDIR/Video-Tarot-h264
                        echo "$PREFIX Recording and broadcasting  $VIDEO in progress : hit CTRL C to stop"
                        tee $VIDEO < $pipeout | $WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>$log 2>&1
                else
                        echo "$PREFIX Broadcasting video (no recording) in progress : hit CTRL C to stop"
                        $WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>$log 2>&1 < $pipeout
                fi
        fi
else
                echo "Please choose the interface of your TP-LINK 722N as the first argument" 
                echo "Then the wifi channel as the second argument"
                echo "Usage $0 2.3ghz channel -19 and 2.4Ghz channel 11 :"
                echo "$0 wlan1 -19 --vb  : video with wifibroadcast (default)"
                echo "$0 wlan1 -19 --vbr : video with wifibroadcast and recording"
                echo "$0 wlan1 -19 --vr  : video recording"
                echo "$0 wlan1 -19 --vrt [video_filemane] : video retransmission and consersion h264 to mp4 (default last video)"
fi

