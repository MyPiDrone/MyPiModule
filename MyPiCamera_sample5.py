#!/usr/bin/python
#TITLE# DRONE MyPiCamera sample add_overlay

# Test Overlay Timer - has three overlays
import picamera
import time
from PIL import Image, ImageDraw, ImageFont

# Video Resolution
VIDEO_HEIGHT = 720
VIDEO_WIDTH = 1280

#font = ImageFont.truetype("/home/pi/fonts/Roboto-Regular.ttf", 20) 
#fontBold = ImageFont.truetype("/home/pi/fonts/Roboto-Bold.ttf", 22)
font = ImageFont.truetype("calibri.ttf", 20) 
fontBold = ImageFont.truetype("calibri.ttf", 22)

textPad = Image.new('RGB', (512, 64))
textPadImage = textPad.copy()

textPad2 = Image.new('RGB', (128, 64), "#999")
textPadImage2 = textPad2.copy()

#filename = 'timestamped.h264'
filename = '/tmp/MyPiCamera.h264'

i = 0
with picamera.PiCamera() as camera:
   camera.resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)
   camera.framerate = 30
   camera.led = False
   camera.start_preview()
   camera.start_recording(filename)
#   camera.wait_recording(0.9)

# Layer 3 overlay
   overlay = camera.add_overlay(textPadImage.tobytes(), size=(512, 64), alpha = 128, layer = 3, fullscreen = False, window = (0,20,512,64))
   textPadImage = textPad.copy()
   drawTextImage = ImageDraw.Draw(textPadImage)
   drawTextImage.text((75, 18),"RECORDING" , font=fontBold, fill=("Red"))
   drawTextImage.text((275, 20), filename, font=font, fill=("Yellow"))
   overlay.update(textPadImage.tobytes())

   try:
      while True:
# Layer 4 overlay
         text = time.strftime('%H:%M:%S', time.gmtime())
         overlay1 = camera.add_overlay(textPadImage2.tobytes(), size=(128, 64), alpha = 128, layer = 4, fullscreen = False, window = (512,20,128,64))
         textPadImage2 = textPad2.copy()
         drawTextImage = ImageDraw.Draw(textPadImage2)
         drawTextImage.text((22, 20), text, font=font, fill=("black"))
         overlay1.update(textPadImage2.tobytes())
         if i == 0:
            i = 1
         else:              
            camera.remove_overlay(overlay2)
         camera.wait_recording(0.9)

# Layer 5 overlay
         text = time.strftime('%H:%M:%S', time.gmtime())
         overlay2 = camera.add_overlay(textPadImage2.tobytes(), size=(128, 64), alpha = 128, layer = 5, fullscreen = False, window = (512,20,128,64))
         textPadImage2 = textPad2.copy()
         drawTextImage = ImageDraw.Draw(textPadImage2)
         drawTextImage.text((22, 20), text, font=font, fill=("black"))
         overlay2.update(textPadImage2.tobytes())
         camera.remove_overlay(overlay1)
         camera.wait_recording(0.9)


   except KeyboardInterrupt:
      camera.remove_overlay(overlay)
      camera.remove_overlay(overlay1)
      camera.remove_overlay(overlay2)
      camera.stop_recording()
      camera.stop_preview()

      print ("Cancelled")

   finally:
      camera.remove_overlay(overlay2)
      camera.stop_recording()
      camera.stop_preview()

print("end test")
