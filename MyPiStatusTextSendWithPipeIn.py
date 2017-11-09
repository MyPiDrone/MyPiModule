#!/usr/bin/python
#TITLE# DRONE MyPiStatusTextSendWithPipeIn

import sys
import time
import os
from pymavlink import mavutil
MyPipeIn=""
try:
   MyPipeIn=sys.argv[1]
except:
   pass
if MyPipeIn == "": MyPipeIn="/tmp/MyPiStatusTextSend.pipein"
try:
   os.mkfifo(MyPipeIn)
except OSError:
   pass
source_system=255
#master2 = mavutil.mavlink_connection("udp:127.0.0.1:14550", input=False, dialect="common", source_system=source_system)
print("Waiting input test here %s (pipe)" % MyPipeIn)
with open(MyPipeIn, "r") as p:
   while True:
      text = p.read()
      if text != "":
         master2 = mavutil.mavlink_connection("udp:127.0.0.1:14550", input=False, dialect="common", source_system=source_system)
         print("Input %s" % text)
         # 1=ALERT 2=CRITICAL 3=ERROR, 4=WARNING, 5=NOTICE, 6=INFO, 7=DEBUG, 8=ENUM_END
         master2.mav.statustext_send(1, "%s" % text)
         time.sleep(8)
         master2.close()
      else:
         time.sleep(2)
f.close()
#master2.close()

