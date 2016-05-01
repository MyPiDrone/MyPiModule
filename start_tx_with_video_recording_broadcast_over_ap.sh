#!/bin/bash
################################################################
#### www.MyPiDrone.com
#### Video Broadcast over Wifi AP : beta test
################################################################

clear
echo ##################TX Script#################
echo Start this script with root authority

WIDTH=640
HEIGHT=480
FPS=15
#
#WIDTH=1920
#HEIGHT=1080
#FPS=30
#
#WIDTH=1280
#HEIGHT=720
#FPS=15
#BITRATE=2000000
BITRATE=4000000
KEYFRAMERATE=60
# 10 minutes
#TIMEOUT=60000
# 10 minutes
#TIMEOUT=600000
# 20 minutes
TIMEOUT=1200000
# 40 minutes
#TIMEOUT=2400000

VIDDIR="/root/fpv/videos"

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

if [ "$1" != "" ] && [ "$2" != "" ];
then
	# DEBUG
        #echo $1 choose by user to be the wireless interface TP-LINK 722N >> /var/log/ArduCopter-quad.log
	#Initial wifi interface configuration
	#/sbin/ifconfig $1 up 10.1.1.1 netmask 255.255.255.0
	#sleep 2
	#ip a >> /var/log/ArduCopter-quad.log
	#/sbin/ifconfig -a >> /var/log/ArduCopter-quad.log
	#Enable NAT
	#iptables --flush
	#iptables --table nat --flush
	#iptables --delete-chain
	#iptables --table nat --delete-chain
	#iptables --table nat --append POSTROUTING --out-interface wlan0 -j MASQUERADE
	#iptables --append FORWARD --in-interface wlan1 -j ACCEPT
	#sysctl -w net.ipv4.ip_forward=1
	#service dnsmasq start
	#service hostapd start
	#pour rejouer la video $3 = --VRT ou n importe quoi 
	if [ "$3" = "--vrt" -o "_$3" = "_" ]; then
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
		cat $VIDEO|gst-launch-1.0 -v fdsrc !  h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5000 host=10.0.0.12
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
		if [ "$3" = "--vr" ]; then
			ln -sf $VIDEO $VIDDIR/Video-Tarot-h264
			echo "Recording $VIDEO in progress : hit CTRL C to stop"
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o $VIDEO 
		elif [ "$3" = "--vbr" ]; then
			ln -sf $VIDEO $VIDDIR/Video-Tarot-h264
			echo "Recording and broadcasting  $VIDEO in progress : hit CTRL C to stop"
			#raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - | tee $VIDEO | socat - udp-datagram:10.1.1.255:5000,broadcast
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - |tee $VIDEO|gst-launch-1.0 -v fdsrc !  h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5000 host=10.0.0.12
		else
			echo "Broadcasting video (no recording) in progress : hit CTRL C to stop"
			#raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - |socat - udp-datagram:10.1.1.12:5000,broadcast
			#raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - |gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=10.1.1.1 port=5000 
			# pour tower droidplanner tower 3.2.1 beta 1 : test ok
			#raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - |gst-launch-1.0 -v fdsrc !  h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5000 host=10.1.1.255
			raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - |gst-launch-1.0 -v fdsrc !  h264parse ! rtph264pay config-interval=10 pt=96 ! udpsink port=5000 host=10.0.0.12
			#### chmod pour le user kevin : cvlc ne fonctionne qu'avec un user non  root
			#### plus besoin de faire ceci avec la methode getppid : chmod 777 /dev/vchiq
			## nouvelle methode :
                        ## mandatory to run cvlc with root user
                        strings /usr/bin/vlc|egrep "getppid|geteuid"
                        C=`strings /usr/bin/vlc|grep -c getppid`
                        if [ $C -eq 1 ]; then
                               echo "VLC getppid already set"
                        else
                               cp /usr/bin/vlc /usr/bin/vlc.ori
                               sed -i 's/geteuid/getppid/' /usr/bin/vlc
                               strings /usr/bin/vlc|egrep "getppid|geteuid"
                        fi
			#raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - |cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:5000}' :demux=h264
			#raspivid -ih -t $TIMEOUT -w $WIDTH -h $HEIGHT -fps $FPS -b $BITRATE -n -g $KEYFRAMERATE -pf high -o - |cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:5000/}' :demux=h264
		fi
	fi
else
        	echo Please choose the interface of your TP-LINK 722N as the first argument 
        	echo Then the wifi channel as the second argument
       		echo "Usage $0"
        	echo "$0 wlan1 10.1.1.255:5000 --vb   : video with wifibroadcast (default)"
        	echo "$0 wlan1 10.1.1.255:5000 --vbr  : video with wifibroadcast and recording"
        	echo "$0 wlan1 10.1.1.255:5000 --vr   : video recording"
        	echo "$0 wlan1 10.1.1.255:5000 --vrt  [video_filemane] : video retransmission and consersion h264 to mp4 (default last video)"
fi

