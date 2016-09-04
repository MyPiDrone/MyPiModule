###########################################################
####### www.MyPiDrone.com
#TITLE# Mypicamera write telemetry text over video with camera.annotate_text
###########################################################
import os
import picamera
import datetime as dt

pipeout = '/tmp/Mypicamera.pipeout'
pipein = '/tmp/Mypicamera.pipein'

try:
    os.mkfifo(pipeout)
except OSError:
    pass
try:
    os.mkfifo(pipein)
except OSError:
    pass

pout = open(pipeout, 'w')
pin = open(pipein, 'r')

pout.write("How are you?")
telemetry_text = "" 

with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.framerate = 24
    camera.start_preview()
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text_size = 20
    camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    camera.start_recording(pout, format='h264', quality=23)
    start = dt.datetime.now()
    while (dt.datetime.now() - start).seconds < 12000:
        intext = pin.read()
        intext = intext.rstrip()
        if intext != "":
             telemetry_text = (intext[:234] + '..') if len(intext) > 234 else intext
             print "%s" % telemetry_text
        msg = "%s %s" % (dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),telemetry_text)
        camera.annotate_text = msg
        camera.wait_recording(0.2)
    camera.stop_recording()
    pout.close()
    pin.close()

