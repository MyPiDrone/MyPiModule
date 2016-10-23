#!/bin/bash
################################################
#### wwww.MyPiDrone.com
#TITLE# GCS TarotGroundStation video streaming over AP
################################################

clear
echo ##################RX Script#################
echo Start this script with root authority

echo "Usage : $0 [channel] [wlan_number1] [wlan_number2]"
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
PORT=0
if [ "_$1" = "_" ]; then
	CHANNEL="-19"
	#CHANNEL="11"
else
	CHANNEL=$1
fi
if [ "_$2" = "_" -o "_$3" = "_" ]; then
	#WLAN1=`/sbin/ifconfig -a |egrep -i '30.*B5.*C2.*11.*83.*22|30.*b5.*c2.*11.*62.*ea'|awk '{print $1}'`
	#WLAN1="wlan2"
	WLAN1="wlx60e3270f04fd"
	WLAN2="wlx30b5c21162ea"
else
	WLAN1=$2
	WLAN2=$3
fi
echo "WLAN1=$WLAN1 WLAN2=$WLAN2 CHANNEL=$CHANNEL"

if [ "_$WLAN1" != "_" -a "_$WLAN2" != "_" -a "_$CHANNEL" != "_" ];
then
	if [ "_$4" != "_" ]; then
        	cat /tmp/Video-Tarot | gst-launch-1.0 -v fdsrc ! h264parse ! avdec_h264 ! xvimagesink sync=false
	
	else
                echo $WLAN1 $WLAN2 choose by user to be the wireless interface TP-LINK 722N
                ip link set $WLAN1 down
                ip link set $WLAN2 down
                echo Setting wifi adapter in MONITOR mode
                iw dev $WLAN1 set monitor otherbss fcsfail
                iw dev $WLAN2 set monitor otherbss fcsfail
                ip link set $WLAN1 up
                ip link set $WLAN2 up
                echo Setting wifi channel $CHANNEL
                sleep 1
                iw dev $WLAN1 set freq 2357
                iw dev $WLAN2 set freq 2357
                #sleep 1
                ### channel -19
                [ "$CHANNEL" = "-19" ] && iw dev $WLAN1 set freq 2312
                [ "$CHANNEL" = "-19" ] && iw dev $WLAN2 set freq 2312
                ### channel 11
                [ "$CHANNEL" = "11" ] && iw dev $WLAN1 set freq 2462
                [ "$CHANNEL" = "11" ] && iw dev $WLAN2 set freq 2462
                iw reg set FR
                echo Setting maximum Tx Power
                iwconfig $WLAN1 txpower 30
                iwconfig $WLAN2 txpower 30
                sleep 1
                iwconfig $WLAN1
                iwconfig $WLAN2
        	echo Starting HD Video reception...
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN1
        	#$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH | mplayer -fps 15 -cache 1024 -
		echo "$WifiBroadcast_RX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN1 $WLAN2"
		# vlc rtsp
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN1 $WLAN2 |cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:5000/}' :demux=h264
		# socat with https://github.com/Consti10/myMediaCodecPlayer-for-FPV
                mkfifo /tmp/mypipe1 
                mkfifo /tmp/mypipe2 
		gst-launch-1.0 -v fdsrc ! h264parse ! avdec_h264 ! xvimagesink sync=false < /tmp/mypipe1 &
		socat -b 1024 - UDP4-SENDTO:10.0.0.18:5000 < /tmp/mypipe2 &
		$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN1 $WLAN2 |tee -a /tmp/mypipe1|tee -a /tmp/mypipe2 |socat -b 1024 - UDP4-SENDTO:10.0.0.12:5000
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN1 $WLAN2 |tee -a /tmp/mypipe1 |socat -b 1024 - UDP4-SENDTO:10.0.0.12:5000
                # tower test
		#$WifiBroadcast_RX  -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN1 $WLAN2 |tee -a /tmp/mypipe1 |gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5000 host=10.0.0.18
	fi

else
        echo Please choose the interface of your TP-LINK 722N as the first argument 
        echo Then the wifi channel as the second argument
fi
