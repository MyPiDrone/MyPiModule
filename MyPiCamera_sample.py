#!/usr/bin/python
##############################################################################################################################
####### www.MyPiDrone.com
#TITLE# DRONE MyPiCamera sample write telemetry text over video with camera.annotate_text
####### www.MyPiDrone.com
####### How to used : 
#######  MyPiCamera_sample.py | tee $VIDEO | $WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>/dev/null 2>&1 &
#######  echo 'My telemetry text' > /tmp/MyPiCamera.pipein
##############################################################################################################################
import os
import sys
import picamera
import datetime as dt

pout = sys.stdout

pipein = '/tmp/MyPiCamera.pipein'
try:
    os.mkfifo(pipein)
except OSError:
    pass
pin = open(pipein, 'r')

telemetry_text = "" 

#Mode   Size    Aspect Ratio    Frame rates     FOV     Binning
#0      automatic selection
#1      1920x1080       16:9    1-30fps         Partial None
#2      2592x1944       4:3     1-15fps         Full    None
#3      2592x1944       4:3     0.1666-1fps     Full    None
#4      1296x972        4:3     1-42fps         Full    2x2
#5      1296x730        16:9    1-49fps         Full    2x2
#6      640x480         4:3     42.1-60fps      Full    2x2 plus skip
#7      640x480         4:3     60.1-90fps      Full    2x2 plus skip

with picamera.PiCamera() as camera:
    camera.sharpness = 0
    camera.contrast = 0
    camera.brightness = 50
    camera.saturation = 0
    camera.ISO = 0
    camera.video_stabilization = True
    camera.exposure_compensation = 0
    camera.exposure_mode = 'auto'
    camera.meter_mode = 'average'
    camera.awb_mode = 'auto'
    #camera.image_effect = 'negative'
    camera.image_effect = 'none'
    camera.color_effects = None
    camera.rotation = 0
    camera.hflip = False
    camera.vflip = False
    camera.crop = (0.0, 0.0, 1.0, 1.0)
    camera.resolution = (1296, 972)
    camera.framerate = 42
    #camera.start_preview()
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text_size = 20
    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    camera.start_recording(pout, format='h264', quality=23, bitrate=4000000)
    start = dt.datetime.now()
    while (dt.datetime.now() - start).seconds < 12000:
        intext = pin.read()
        intext = intext.rstrip()
        if intext != "":
             telemetry_text = (intext[:234] + '..') if len(intext) > 234 else intext
             #print "%s" % telemetry_text
        msg = "%s %s" % (dt.datetime.now().strftime('%d/%m %H:%M:%S'),telemetry_text)
        camera.annotate_text = msg
        camera.wait_recording(0.2)
    camera.stop_recording()
    pin.close()

