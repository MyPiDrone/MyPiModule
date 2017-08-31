#!/usr/bin/python
##############################################################################################################################
####### www.MyPiDrone.com
#TITLE# DRONE MyPiCamera sample write telemetry text over video with camera.annotate_text
####### www.MyPiDrone.com
####### How to used : 
#######  MyPiCamera_sample.py | tee $VIDEO | $WifiBroadcast_TX -p $PORT -b $BLOCK_SIZE -r $FECS -f $PACKET_LENGTH $WLAN 1>/dev/null 2>&1 &
#######  echo 'My telemetry text' > /tmp/MyPiCamera.pipein
####### Sample start exec MyPiCamera_sample.sh
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
# image_effect  'none' 'negative' 'solarize' 'sketch' 'denoise' 'emboss' 'oilpaint' 'hatch' 'gpen' 'pastel' 'watercolor' 'film' 'blur' 'saturation' 'colorswap' 'washedout' 'posterise' 'colorpoint' 'colorbalance' 'cartoon' 'deinterlace1' 'deinterlace2'

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
    camera.resolution = (1640, 922)
    camera.framerate = 40
    camera.start_preview()
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text_size = 20
    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    camera.start_recording(pout, format='h264', quality=0, intra_period=60, bitrate=4000000, profile='baseline')
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

