#!/bin/bash
################################################
#### wwww.MyPiDrone.com
#TITLE# GCS TarotGroundStation video streaming over AP
################################################

clear
echo ##################RX Script#################
echo Start this script with root authority

echo "Usage : $0 [wlan_number] [channel]"
echo "           default wlan_number wlan2 30:B5:C2:11:83:22|30:b5:c2:11:62:ea"
echo "           2.4Ghz channel 1 to 13"
echo "           2.3ghz channel -1 to -19"
echo "           channel default -19"

## mandatory to run cvlc with root user
strings /usr/bin/vlc|egrep "getppid|geteuid"
C=`strings /usr/bin/vlc|grep -c getppid`
if [ $C -eq 1 ]; then
	echo "VLC getppid already set"
else
	cp /usr/bin/vlc /usr/bin/vlc.ori
	sed -i 's/geteuid/getppid/' /usr/bin/vlc
fi
strings /usr/bin/vlc|egrep "getppid|geteuid"

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
else
	WLAN=$1
fi
if [ "_$2" = "_" ]; then
	CHANNEL="-19"
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
                ### channel -19
                [ "$CHANNEL" = "-19" ] && iw dev $WLAN set freq 2312
                ### channel 11
                [ "$CHANNEL" = "11" ] && iw dev $WLAN set freq 2462
                iw reg set BO
                echo Setting maximum Tx Power
                iwconfig $WLAN txpower 30
                sleep 1
                iwconfig $WLAN
        	echo Starting HD Video reception...
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH | mplayer -fps 15 -cache 1024 -
		echo "$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN"
		#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN > /tmp/myvideo
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN | gst-launch-1.0 -v fdsrc ! h264parse ! avdec_h264 ! xvimagesink sync=false
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN | gst-launch-0.10 -v fdsrc ! h264parse ! ffdec_h264 ! xvimagesink sync=false
		# to Android Tower
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN |gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=9000 host=10.0.0.12
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN |gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=9000 host=192.168.1.60
		#to qrroundcontrol port 5000 or 5600?
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN |gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5600 host=127.0.0.1
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN |gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5000 host=10.0.0.12
		# vlc http
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN |cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:5000}' :demux=h264
		# vlc rtsp
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN |cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:5000/}' :demux=h264
		# socat with https://github.com/Consti10/myMediaCodecPlayer-for-FPV
                mkfifo /tmp/mypipe 
		gst-launch-1.0 -v fdsrc ! h264parse ! avdec_h264 ! xvimagesink sync=false < /tmp/mypipe &
		$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN |tee -a /tmp/mypipe |socat -b 1024 - UDP4-SENDTO:10.0.0.18:5000
	fi

else
        echo Please choose the interface of your TP-LINK 722N as the first argument 
        echo Then the wifi channel as the second argument
fi
