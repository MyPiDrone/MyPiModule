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
# prefer reopen mavlink connection for each statustext_send
#master = mavutil.mavlink_connection("udp:127.0.0.1:14550", input=False, dialect="common", source_system=source_system)
print("Waiting input test here %s (pipe)" % MyPipeIn)
with open(MyPipeIn, "r") as p:
   while True:
      text = p.read()
      if text != "":
         print("Input %s" % text)
         # 1=ALERT 2=CRITICAL 3=ERROR, 4=WARNING, 5=NOTICE, 6=INFO, 7=DEBUG, 8=ENUM_END
         master = mavutil.mavlink_connection("udp:127.0.0.1:14550", input=False, dialect="common", source_system=source_system)
         master.mav.statustext_send(1, "%s" % text)
         master.close()
         time.sleep(4)
      else:
         time.sleep(2)
p.close()
#master.close()

