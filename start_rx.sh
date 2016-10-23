#!/bin/bash
################################################
#### wwww.MyPiDrone.com
#TITLE# GCS TarotGroundStation Video Viewer
################################################

DISPLAY=:0

clear
echo ##################RX Script#################
echo Start this script with root authority

echo "Usage : $0 [wlan_number] [channel]"
echo "           default wlan_number wlan2 30:B5:C2:11:83:22|30:b5:c2:11:62:ea"
echo "           2.4Ghz channel 1 to 13"
echo "           2.3ghz channel -1 to -19"
echo "           channel default -19"

WifiBroadcast_RX="/root/wifibroadcast/rx"
WifiBroadcast_RX="/root/WifiBroadcast/wifibroadcast/rx"

BLOCK_SIZE=8
FECS=4
PACKET_LENGTH=1024
#PACKET_LENGTH=512
PORT=0
if [ "_$1" = "_" ]; then
	WLAN=`/sbin/ifconfig -a |egrep -i '30.*B5.*C2.*11.*83.*22|30.*b5.*c2.*11.*62.*ea'|awk '{print $1}'`
	#WLAN="wlan2"
	#WLAN="wlx60e3270f04fd"
	#WLAN="wlx30b5c21162ea"
	#WLAN="wlx24050f6dae59"
else
	WLAN=$1
fi
if [ "_$2" = "_" ]; then
	CHANNEL="-19"
	#CHANNEL="149"
	#CHANNEL="11"
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
		ip link set $WLAN down                               
       		echo Setting wifi adapter in MONITOR mode
                iw dev $WLAN set monitor otherbss fcsfail
                ip link set $WLAN up                               
       		echo Setting wifi channel $CHANNEL
                sleep 1
                iw dev $WLAN set freq 2357
                #sleep 1
                ### channel 149
                [ "$CHANNEL" = "149" ] && iw dev $WLAN set freq 5745
                ### channel -19
                [ "$CHANNEL" = "-19" ] && iw dev $WLAN set freq 2312
                ### channel 11
                [ "$CHANNEL" = "11" ] && iw dev $WLAN set freq 2462
        	iw reg set FR
        	echo Setting maximum Tx Power
        	iwconfig $WLAN txpower 30
		sleep 1
		iwconfig $WLAN
        	echo Starting HD Video reception...
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH | mplayer -fps 15 -cache 1024 -
		echo "$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN"
		#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN > /tmp/myvideo
        	$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN | gst-launch-1.0 -v fdsrc ! h264parse ! avdec_h264 ! xvimagesink sync=false
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN | gst-launch-0.10 -v fdsrc ! h264parse ! ffdec_h264 ! xvimagesink sync=false
                # to Android appli QtGstreamerHUD emlid
		#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=9000 host=10.0.0.12
	fi

else
        echo Please choose the interface of your TP-LINK 722N as the first argument 
        echo Then the wifi channel as the second argument
fi
