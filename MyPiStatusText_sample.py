#!/usr/bin/python
#TITLE# DRONE MyPiCamera sample statustext_send

##import os, sys, math, time, psutil
#import numpy as np
##import subprocess
##import picamera
from pymavlink import mavutil
##from datetime import datetime
##from threading import Thread
##from MAVProxy.modules.lib import mp_module
##from MAVProxy.modules.lib.mp_settings import MPSetting

source_system=255
text=" Status text send"
mycountermessage=2
master2 = mavutil.mavlink_connection("udp:127.0.0.1:14550", input=False, dialect="common", source_system=source_system)
# 1=ALERT 2=CRITICAL 3=ERROR, 4=WARNING, 5=NOTICE, 6=INFO, 7=DEBUG, 8=ENUM_END
master2.mav.statustext_send(1, " %02d %s" % (mycountermessage,text))
master2.close()

