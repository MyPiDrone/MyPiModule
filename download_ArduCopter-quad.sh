#!/bin/sh
#TITLE# DRONE Download ArduCopter-quad from http://firmware.ardupilot.org/Copter
# https://community.emlid.com/t/apm-3-3-rc9-beta-testing/764/22
ls -al /opt/apm/bin/ArduCopter-quad*.elf

wget http://firmware.ardupilot.org/Copter/stable/navio-quad/ArduCopter.elf --output-document=/opt/apm/bin/ArduCopter-quad-navio-V3.3.3.elf

#V3.4-dev
#http://firmware.ardupilot.org/Copter/2016-05/2016-05-09-10:05/navio-quad/ArduCopter.elf
#http://firmware.ardupilot.org/Copter/2016-05/2016-05-09-10:05/navio2-quad/ArduCopter.elf

wget http://firmware.ardupilot.org/Copter/latest/navio-quad/ArduCopter.elf --output-document=/opt/apm/bin/ArduCopter-quad-navio-V3.4-dev.elf
wget http://firmware.ardupilot.org/Copter/latest/navio2-quad/ArduCopter.elf --output-document=/opt/apm/bin/ArduCopter-quad-navio2-V3.4-dev.elf

chmod +x /opt/apm/bin/ArduCopter-quad*.elf
ls -lrt /opt/apm/bin/ArduCopter-quad*.elf

#cp -p /opt/apm/bin/ArduCopter-quad-navio-V3.3.3.elf /opt/apm/bin/ArduCopter2
cp -p /opt/apm/bin/ArduCopter-quad-navio-navio2-V3.4-dev.elf /opt/apm/bin/ArduCopter2
