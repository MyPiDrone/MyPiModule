#!/usr/bin/python
#TITLE# DRONE MyPiStatusTextSend

import sys
from pymavlink import mavutil

source_system=255
text=sys.argv[1]
master2 = mavutil.mavlink_connection("udp:127.0.0.1:14550", input=False, dialect="common", source_system=source_system)
# 1=ALERT 2=CRITICAL 3=ERROR, 4=WARNING, 5=NOTICE, 6=INFO, 7=DEBUG, 8=ENUM_END
master2.mav.statustext_send(1, "%s" % text)
master2.close()

