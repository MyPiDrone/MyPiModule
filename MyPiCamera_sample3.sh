#!/bin/sh
##############################################################################################################################
####### www.MyPiDrone.com
#TITLE# DRONE MyPiCamera start MyPiCamera_sample3.py & tx (python sample with picamera)
####### www.MyPiDrone.com
##############################################################################################################################
###############################################################################
# V1 camera
#Mode   Size    Aspect Ratio    Frame rates     Video Image  FOV     Binning
#0      automatic selection
#1      1920x1080       16:9    1-30fps         x            Partial None
#2      2592x1944       4:3     1-15fps         x      x     Full    None
#3      2592x1944       4:3     0.1666-1fps     x      x     Full    None
#4      1296x972        4:3     1-42fps         x            Full    2x2
#5      1296x730        16:9    1-49fps         x            Full    2x2
#6      640x480         4:3     42.1-60fps      x            Full    2x2 plus skip
#7      640x480         4:3     60.1-90fps      x          Full    2x2 plus skip
###############################################################################
# V2 camera
# Mode Resolution Aspect Ratio Framerates Video Image FoV     Binning
# 1    1920x1080        16:9    0.1-30fps  x        Partial   None
# 2    3280x2464        4:3     0.1-15fps  x    x   Full      None
# 3    3280x2464        4:3     0.1-15fps  x    x   Full      None
# 4    1640x1232        4:3     0.1-40fps  x        Full      2x2
# 5    1640x922         16:9    0.1-40fps  x        Full      2x2
# 6    1280x720         16:9    40-90fps   x        Partial   2x2
# 7    640x480          4:3     40-90fps   x        Partial   2x2
###############################################################################
#WIDTH=1296
#HEIGHT=972
#FPS=42
WifiBroadcast_TX="/root/wifibroadcast/tx"
BITRATE=4000000
KEYFRAMERATE=60
BLOCK_SIZE=8
FECS=4
PACKET_LENGTH=1024
PORT=0
TIMEOUT=1200000
WLAN="wlan1"
CHANNEL="-19"
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
echo "-----------------------------------------------------------------------------"
ip a 
echo "-----------------------------------------------------------------------------"
ifconfig $WLAN
echo "-----------------------------------------------------------------------------"
iwconfig $WLAN
echo "-----------------------------------------------------------------------------"
if [ ! -p /tmp/MyPiCamera.h264 ]; then
	mkfifo /tmp/MyPiCamera.h264
fi
echo "$WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 2>&1 < /tmp/MyPiCamera.h264"
$WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 2>&1 < /tmp/MyPiCamera.h264
