#!/usr/bin/python
###########################################################
####### www.MyPiDrone.com
#TITLE# Mypicamera write telemetry text over video with camera.annotate_text
###########################################################
import os
import sys
import picamera
import datetime as dt

pout = sys.stdout

pipein = '/tmp/Mypicamera.pipein'
try:
    os.mkfifo(pipein)
except OSError:
    pass
pin = open(pipein, 'r')

pout.write("How are you?")
telemetry_text = "" 

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
    camera.resolution = (1296, 730)
    camera.framerate = 49
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
        msg = "%s %s" % (dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),telemetry_text)
        camera.annotate_text = msg
        camera.wait_recording(0.2)
    camera.stop_recording()
    pin.close()

