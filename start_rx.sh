#!/bin/bash
################################################
#### wwww.MyPiDrone.com
################################################

clear
echo ##################RX Script#################
echo Start this script with root authority

echo "Usage : $0 [wlan_number] [channel]"
echo "           default wlan_number wlan1 30:B5:C2:11:83:22|30:b5:c2:11:62:ea"
echo "           2.4Ghz channel 1 to 13"
echo "           2.3ghz channel -1 to -19"
echo "           channel default -13"

BLOCK_SIZE=8
FECS=4
PACKET_LENGTH=1024
#PACKET_LENGTH=512
PORT=0
if [ "_$1" = "_" ]; then
	WLAN=`/sbin/ifconfig -a |egrep -i '30.*B5.*C2.*11.*83.*22|30.*b5.*c2.*11.*62.*ea'|awk '{print $1}'`
	#WLAN="wlan1"
	#WLAN="wlx60e3270f04fd"
else
	WLAN=$1
fi
if [ "_$2" = "_" ]; then
	CHANNEL="-13"
else
	CHANNEL=$2
fi
echo "WLAN=$WLAN CHANNEL=$CHANNEL"

if [ "_$WLAN" != "_" ] && [ "_$CHANNEL" != "_" ];
then
	if [ "_$3" != "_" ]; then
        	cat /tmp/Video-Tarot | gst-launch-1.0 -v fdsrc ! h264parse ! avdec_h264 ! xvimagesink sync=false
	
	else
        	echo $WLAN choose by user to be the wireless interface TP-LINK 722N
       		echo Setting wifi channel $CHANNEL
        	iwconfig $WLAN channel $CHANNEL
       		echo Setting wifi adapter in MONITOR mode
      		ifconfig $WLAN down && iw dev $WLAN set monitor otherbss fcsfail
        	echo Setting maximum Tx Power
        	iw reg set BO
        	iwconfig $WLAN txpower 30
        	ifconfig $WLAN up
        	echo Setting Channel $CHANNEL
        	iwconfig $WLAN channel $CHANNEL
		sleep 1
		iwconfig $WLAN
        	echo Starting HD Video reception...
        	#./rx -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN
        	#./rx -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH | mplayer -fps 15 -cache 1024 -
        	./rx -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN | gst-launch-1.0 -v fdsrc ! h264parse ! avdec_h264 ! xvimagesink sync=false
	fi

else
        echo Please choose the interface of your TP-LINK 722N as the first argument 
        echo Then the wifi channel as the second argument
fi
