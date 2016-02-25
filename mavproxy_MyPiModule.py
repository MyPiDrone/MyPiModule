''' ------------------------------------------  '''
''' MyPiModule for MyPIDrone                    '''
''' www.MyPiDrone.com                           '''
''' https://github.com/MyPiDrone/MyPiModule     '''
''' ------------------------------------------  '''
''' Version 1.1 : Wed Feb 25 10:35:30 CET 2016  '''
''' ------------------------------------------  '''

import time
from pymavlink import mavutil
from datetime import datetime

import subprocess

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib.mp_settings import MPSetting

class MyPiModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(MyPiModule, self).__init__(mpstate, "MyPiModule", "my commands")
        self.add_command('mybat', self.cmd_mybat, "my battery information")
        self.add_command('myshut', self.cmd_myshutdown, "to shutdown")
        self.add_command('myreboot', self.cmd_myreboot, "to reboot")
        self.armed = False
        self.shutdown_auto_requested = False
        self.shutdown_auto_requested_time = 0
        self.shutdown_requested = False
        self.shutdown_requested_time = 0
        self.reboot_requested = False
        self.reboot_requested_time = 0
        self.mystate = 0
        self.myvolt = 0
        self.mythrottle = 0
        self.mycurrent = 0
        self.myremaining = 0
        self.myrc1raw = 0 ; self.myrc2raw = 0 ; self.myrc3raw = 0 ; self.myrc4raw = 0
        self.myrc5raw = 0 ; self.myrc6raw = 0 ; self.myrc7raw = 0 ; self.myrc8raw = 0
        self.wlan0_up = False
        self.video_on = True
        self.last_battery_check_time = time.time()
        self.last_rc_check_time = time.time()
        self.settings.append(MPSetting('mytimebat', int, 5, 'Battery Interval Time sec', tab='my'))
        self.settings.append(MPSetting('mytimerc', int, 5, 'RC Interval Time sec'))
        self.settings.append(MPSetting('mydebug', bool, True, 'Debug'))
        self.settings.append(MPSetting('myminvolt', int, 10000, 'Minimum battery voltage before shutdown'))
        self.settings.append(MPSetting('myminremain', int, 10, 'Minimum battery remaining before shutdown'))
        self.battery_period = mavutil.periodic_event(5)
        self.FORMAT = '%Y-%m-%d %H:%M:%S'
        self.FORMAT2 = '%Hh%Mm%Ss'
        # default to servo range of 1000 to 1700
        #self.RC1_MIN  = self.get_mav_param('RC1_MIN', 0)
        #self.RC1_MAX  = self.get_mav_param('RC1_MAX', 0)
        self.RC1_low_mark  = 1200 ; self.RC1_high_mark  = 1700
        self.RC2_low_mark  = 1200 ; self.RC2_high_mark  = 1700
        self.RC3_low_mark  = 1200 ; self.RC3_high_mark  = 1700
        self.RC4_low_mark  = 1200 ; self.RC4_high_mark  = 1700
        self.RC5_low_mark  = 1200 ; self.RC5_high_mark  = 1700
        self.RC6_low_mark  = 1200 ; self.RC6_high_mark  = 1700
        self.RC7_low_mark  = 1200 ; self.RC7_high_mark  = 1700
        self.RC8_low_mark  = 1200 ; self.RC8_high_mark  = 1700
        self.myseverity = 0
        self.mytext = "nulltext"
        # to send statustext
        self.master2 = mavutil.mavlink_connection("udp:127.0.0.1:14550", input=False, dialect="common")

    def my_write_log(self,msg):
        #OUTPUT FILE
        date = datetime.now().strftime(self.FORMAT)
        if self.settings.mydebug:
            print("%s %s" % (date,msg))
        fo = open("/var/log/mavproxy_MyPiModule.log", "a")
        fo.write("%s\n" % msg)
        fo.close()

    def my_statustext_send(self,text):
        date2 = datetime.now().strftime(self.FORMAT2)
        strutf8 = unicode("%s at %s" % (text,date2))
        self.master2.mav.statustext_send(1, str(strutf8))
        self.say(text)

    def my_subprocess(self,cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutData, stderrData) = p.communicate()
        rc = p.returncode
        msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s cmd %s sdtout %s" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,cmd,stdoutData)
        self.my_write_log(msg)
        msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s cmd %s stderr %s" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,cmd,stderrData)
        self.my_write_log(msg)

    def cmd_mybat(self, args):
        self.my_rc_check()
        if self.settings.mydebug:
           print("cmd_mybat %s" % self)
           msg = "INFO Armed: %s RC1:%s %s-%s RC2:%s %s-%s RC3:%s %s-%s RC4:%s %s-%s RC5:%s %s-%s RC6:%s %s-%s RC7:%s %s-%s RC8:%s %s-%s" % (self.armed,self.myrc1raw,self.RC1_low_mark,self.RC1_high_mark,self.myrc2raw,self.RC2_low_mark,self.RC2_high_mark,self.myrc3raw,self.RC3_low_mark,self.RC3_high_mark,self.myrc4raw,self.RC4_low_mark,self.RC4_high_mark,self.myrc5raw,self.RC5_low_mark,self.RC5_high_mark,self.myrc6raw,self.RC6_low_mark,self.RC6_high_mark,self.myrc7raw,self.RC7_low_mark,self.RC7_high_mark,self.myrc8raw,self.RC8_low_mark,self.RC8_high_mark)
           self.my_write_log(msg)
           self.my_subprocess(["uptime"])
        msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s low %s MyCurrent %s MyRemaining %s low %s MyRC8Raw %s" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.settings.myminvolt,self.mycurrent,self.myremaining,self.settings.myminremain,self.myrc8raw)
        self.my_write_log(msg)

    def cmd_myshutdown(self, args):
        if self.armed == False and self.mystate == 3:
            if self.shutdown_requested == False:
                self.my_statustext_send("Shutdown after 60 second")
                self.my_write_log("Shutdown after 60 second")
                self.shutdown_requested = True
                self.shutdown_requested_time = time.time()
            # annulation shutdown
            else:
                self.my_statustext_send("Shutdown canceled")
                self.my_write_log("Shutdown canceled")
                self.shutdown_requested = False
                self.shutdown_requested_time = 0

    def cmd_myreboot(self, args):
        if self.armed == False and self.mystate == 3:
            if self.reboot_requested == False:
                self.my_statustext_send("Reboot after 60 second")
                self.my_write_log("Reboot after 60 second")
                self.reboot_requested = True
                self.reboot_requested_time = time.time()
            # annulation reboot
            else:
                self.my_statustext_send("Reboot canceled")
                self.my_write_log("Reboot canceled")
                self.reboot_requested = False
                self.reboot_requested_time = 0

    def my_statustext_check(self):
            msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MySeverity %s MyStatusText %s" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.myseverity,self.mytext)
            self.my_write_log(msg)

    def my_battery_check(self):
       if time.time() > self.last_battery_check_time + self.settings.mytimebat:
                self.last_battery_check_time = time.time()
                # System Status STANDBY = 3
                if self.armed == False and self.mystate == 3 and (self.myvolt <= self.settings.myminvolt or self.myremaining <= self.settings.myminremain):
                    msg = "WARNING Armed: %s MyState: %s Mythrottle %s MyVolt %s<=%s MyCurrent %s MyRemaining %s<=%s : Shutdown in progress..." % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.settings.myminvolt,self.mycurrent,self.myremaining,self.settings.myminremain)
                    self.my_write_log(msg)
                    if self.shutdown_auto_requested == False:
                        self.my_statustext_send("Shutdown auto after 60 second")
                        self.my_write_log("Shutdown auto after 60 second")
                        self.shutdown_auto_requested = True
                        self.shutdown_auto_requested_time = time.time()
                elif self.myvolt <= self.settings.myminvolt or self.myremaining <= self.settings.myminremain:
                    msg = "WARNING Armed: %s MyState: %s Mythrottle %s MyVolt %s<=%s MyCurrent %s MyRemaining %s<=%s : Shutdown needed" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.settings.myminvolt,self.mycurrent,self.myremaining,self.settings.myminremain)
                    self.my_write_log(msg)
                    self.my_statustext_send("Warning voltage shutdown needed")
                else:
                    msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s>%s MyCurrent %s MyRemaining %s>%s : Good status" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.settings.myminvolt,self.mycurrent,self.myremaining,self.settings.myminremain)
                    self.my_write_log(msg)
                ######### manage : shutdown auto requested / shutdown requested / reboot requested
                if self.shutdown_auto_requested == True and self.shutdown_auto_requested_time != 0 and time.time() > self.shutdown_auto_requested_time + 60:
                    self.my_statustext_send("Shutdown auto now")
                    self.my_write_log("Shutdown auto now")
                    self.my_subprocess(["init","0"])
                if self.shutdown_auto_requested == True:
                    delta = 60 - int(time.time() - self.shutdown_auto_requested_time)
                    self.my_statustext_send("Shutdown left %ssec" % delta)
                    self.my_write_log("Shutdown left %ssec" % delta)
                if self.shutdown_requested == True and self.shutdown_requested_time != 0 and time.time() > self.shutdown_requested_time + 60:
                    self.my_statustext_send("Shutdown now")
                    self.my_write_log("Shutdown now")
                    self.my_subprocess(["init","0"])
                if self.shutdown_requested == True:
                    delta = 60 - int(time.time() - self.shutdown_requested_time)
                    self.my_statustext_send("Shutdown left %ssec" % delta)
                    self.my_write_log("Shutdown left %ssec" % delta)
                if self.reboot_requested == True and self.reboot_requested_time != 0 and time.time() > self.reboot_requested_time + 60:
                    self.my_statustext_send("Reboot now")
                    self.my_write_log("Reboot now")
                    self.my_subprocess(["init","6"])
                if self.reboot_requested == True:
                    delta = 60 - int(time.time() - self.reboot_requested_time)
                    self.my_statustext_send("Reboot left %ssec" % delta)
                    self.my_write_log("Reboot left %ssec" % delta)
                    
    def my_rc_check(self):
       if time.time() > self.last_rc_check_time + self.settings.mytimerc:
           self.last_rc_check_time = time.time()
           if self.settings.mydebug:
               msg = "INFO Armed: %s RC1:%s %s-%s RC2:%s %s-%s RC3:%s %s-%s RC4:%s %s-%s RC5:%s %s-%s RC6:%s %s-%s RC7:%s %s-%s RC8:%s %s-%s" % (self.armed,self.myrc1raw,self.RC1_low_mark,self.RC1_high_mark,self.myrc2raw,self.RC2_low_mark,self.RC2_high_mark,self.myrc3raw,self.RC3_low_mark,self.RC3_high_mark,self.myrc4raw,self.RC4_low_mark,self.RC4_high_mark,self.myrc5raw,self.RC5_low_mark,self.RC5_high_mark,self.myrc6raw,self.RC6_low_mark,self.RC6_high_mark,self.myrc7raw,self.RC7_low_mark,self.RC7_high_mark,self.myrc8raw,self.RC8_low_mark,self.RC8_high_mark)
               self.my_write_log(msg)
           ######## MANAGE WLAN0 UP DOWN
           if self.myrc8raw > 0 and self.myrc8raw < self.RC8_low_mark:
               if self.wlan0_up == True:
                   self.wlan0_up = False
                   self.my_statustext_send("ifdown wlan0 RPI2")
                   self.my_subprocess(["ifdown","wlan0"])
               msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s wlan0 is up : %s : RC8 DOWN" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw,self.wlan0_up)
           elif self.myrc8raw > self.RC8_low_mark and self.myrc8raw < self.RC8_high_mark:
               if self.wlan0_up == True:
                   self.wlan0_up = False
                   self.my_statustext_send("ifdown wlan0 RPI2")
                   self.my_subprocess(["ifdown","wlan0"])
               msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s wlan0 is up : %s : RC8 MIDDLE" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw,self.wlan0_up)
           elif self.myrc8raw > self.RC8_high_mark:
               if self.wlan0_up == False:
                   self.wlan0_up = True
                   self.my_statustext_send("ifup wlan0 RPI2")
                   self.my_subprocess(["ifup","wlan0"])
               msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s wlan0 is up : %s : RC8 UP" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw,self.wlan0_up)
           else:
               msg = "WARNING Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s wlan0 is up : %s : unknown RC8 value" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw,self.wlan0_up)
           self.my_write_log(msg)
           # RC1 ROLL
           # RC2 PITCH
           # RC3 TROTTLE
           # RC4 YAW
           ######## MANAGE VIDEO OFF TROTTLE MAX RC3 > 1700 and YAW MAX RC4 > 1700
           if self.armed == False and self.mystate == 3 and self.myrc4raw > self.RC4_high_mark and self.myrc3raw > self.RC3_high_mark:
               if self.video_on == True:
                   self.video_on = False
                   msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC4raw %s MyRC3Raw %s MyVideo on %s" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.myrc4raw,self.myrc3raw,self.video_on)
                   self.my_write_log(msg)
                   self.my_statustext_send("Video off")
                   self.my_subprocess(["killall","raspivid"])
                   self.my_subprocess(["killall","tx"])
           ######## MANAGE VIDEO ON TROTTLE MAX RC3 > 1700 and YAW MAX RC4 < 1200
           if self.armed == False and self.mystate == 3 and self.myrc4raw < self.RC4_low_mark and self.myrc3raw > self.RC3_high_mark:
               if self.video_on == False:
                   self.video_on = True
                   msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC4raw %s MyRC3Raw %s MyVideo on %s" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.myrc4raw,self.myrc3raw,self.video_on)
                   self.my_write_log(msg)
                   self.my_statustext_send("Video on")
                   self.my_subprocess(["/usr/local/bin/start_video.sh"])
           ######## MANAGE SHUTDOWN TROTTLE MAX RC3 > 1700 and PITCH MAX RC2 > 1700
           if self.armed == False and self.mystate == 3 and self.myrc2raw > self.RC2_high_mark and self.myrc3raw > self.RC3_high_mark:
               msg = "INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC2Raw %s MyRC3Raw %s : Shutdown" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.myrc2raw,self.myrc3raw)
               self.my_write_log(msg)
               if self.shutdown_requested == False:
                   self.my_statustext_send("Shutdown after 60 second")
                   self.my_write_log("Shutdown after 60 second")
                   self.shutdown_requested = True
                   self.shutdown_requested_time = time.time()
           ######## MANAGE REBOOT TROTTLE MAX RC3 > 1700 and PITCH MAX RC2 < 1200
           if self.armed == False and self.mystate == 3 and self.myrc2raw < self.RC2_low_mark and self.myrc3raw > self.RC3_high_mark:
               if self.reboot_requested == False:
                   self.my_statustext_send("Reboot after 60 second")
                   self.my_write_log("Reboot after 60 second")
                   self.reboot_requested = True
                   self.reboot_requested_time = time.time()
           # annulation shutdown
           if self.myrc3raw < self.RC3_high_mark and self.shutdown_requested == True:
               self.my_statustext_send("Shutdown canceled")
               self.my_write_log("Shutdown canceled")
               self.shutdown_requested = False
               self.shutdown_requested_time = 0
           # annulation reboot
           if self.myrc3raw < self.RC3_high_mark and self.reboot_requested == True:
               self.my_statustext_send("Reboot canceled")
               self.my_write_log("Reboot canceled")
               self.reboot_requested = False
               self.reboot_requested_time = 0

    def mavlink_packet(self, m):
        '''  handle a mavlink packet      '''
        '''  HEARTBEAT system_status      '''
        '''  0: System Status UNINIT      '''
        '''  1: System Status BOOT        '''
        '''  2: System Status CALIBRATING '''
        '''  3: System Status STANDBY     '''
        '''  4: System Status ACTIVE      '''
        '''  5: System Status CRITICAL    '''
        '''  6: System Status EMERGENCY   '''
        '''  7: System Status POWEROFF    '''
        mtype = m.get_type()
        #print("System Status %s" % mtype)
        if mtype == "VFR_HUD":
            self.armed = self.master.motors_armed()
            self.mythrottle = m.throttle
        if mtype == "SYS_STATUS":
            self.myvolt = m.voltage_battery
            self.mycurrent = m.current_battery
            self.myremaining = m.battery_remaining
            self.my_battery_check()
        if mtype == "HEARTBEAT":
            self.mystate = m.system_status
        if mtype == "RC_CHANNELS_RAW":
            self.myrc1raw = m.chan1_raw ; self.myrc2raw = m.chan2_raw ; self.myrc3raw = m.chan3_raw ; self.myrc4raw = m.chan4_raw
            self.myrc5raw = m.chan5_raw ; self.myrc6raw = m.chan6_raw ; self.myrc7raw = m.chan7_raw ; self.myrc8raw = m.chan8_raw
            self.my_rc_check()
        if mtype == "STATUSTEXT":
            self.myseverity = m.severity
            self.mytext = m.text
            self.my_statustext_check()
        if self.battery_period.trigger():
            self.my_battery_check()

def init(mpstate):
    '''initialise module'''
    return MyPiModule(mpstate)

