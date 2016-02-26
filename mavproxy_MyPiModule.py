''' ------------------------------------------  '''
''' MyPiModule for MyPIDrone                    '''
''' www.MyPiDrone.com                           '''
''' https://github.com/MyPiDrone/MyPiModule     '''
''' ------------------------------------------  '''
''' Version 1.2 : Wed Feb 26 10:35:30 CET 2016  '''
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
        ### battery low :
        self.shutdown_by_lowbat = False
        self.shutdown_by_lowbat_time = 0
        ### ByRadio resquested
        self.shutdown_by_radio = False
        self.shutdown_by_radio_time = 0
        self.reboot_by_radio = False
        self.reboot_by_radio_time = 0
        ### ByCmd resquested
        self.shutdown_by_cmd = False
        self.shutdown_by_cmd_time = 0
        self.reboot_by_cmd = False
        self.reboot_by_cmd_time = 0
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
        self.settings.append(MPSetting('mydelayinit', int, 30, 'Delay before shutdown or reboot'))
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

    def my_write_log(self,level,msg):
        #OUTPUT FILE
        prefix = "Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s" % (self.armed,self.mystate,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining)
        date = datetime.now().strftime(self.FORMAT)
        if self.settings.mydebug:
            print("%s %s %s %s" % (date,level,prefix,msg))
        fo = open("/var/log/mavproxy_MyPiModule.log", "a")
        fo.write("%s %s %s %s\n" % (date,level,prefix,msg))
        fo.close()

    def my_statustext_send(self,text):
        date2 = datetime.now().strftime(self.FORMAT2)
        strutf8 = unicode("%s at %s" % (text,date2))
        self.master2.mav.statustext_send(1, str(strutf8))
        self.say(text)
        self.my_write_log("INFO",text)

    def my_subprocess(self,cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutData, stderrData) = p.communicate()
        rc = p.returncode
        msg = "cmd %s sdtout %s" % (cmd,stdoutData)
        self.my_write_log("INFO",msg)
        msg = "cmd %s stderr %s" % (cmd,stderrData)
        self.my_write_log("INFO",msg)

    def cmd_mybat(self, args):
        self.my_rc_check()
        if self.settings.mydebug:
           print("cmd_mybat %s" % self)
           msg = "RC1:%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s" % (self.myrc1raw,self.myrc2raw,self.myrc3raw,self.myrc4raw,self.myrc5raw,self.myrc6raw,self.myrc7raw,self.myrc8raw)
           self.my_write_log("INFO",msg)
           self.my_subprocess(["uptime"])
        msg = "LowVolt %s LowRemain %s" % (self.settings.myminvolt,self.settings.myminremain)
        self.my_write_log("INFO",msg)

    def cmd_myshutdown(self, args):
        if self.armed == False and self.mystate == 3:
            if self.shutdown_by_cmd == False:
                self.my_statustext_send("Shutdown ByCmd left %ssec" % self.settings.mydelayinit)
                self.shutdown_by_cmd = True
                self.shutdown_by_cmd_time = time.time()
            ''' shutdown cmd cancel '''
            else:
                self.my_statustext_send("Shutdown ByCmd canceled")
                self.shutdown_by_cmd = False
                self.shutdown_by_cmd_time = 0

    def cmd_myreboot(self, args):
        if self.armed == False and self.mystate == 3:
            if self.reboot_by_cmd == False:
                self.my_statustext_send("Reboot ByCmd left %ssec" % self.settings.mydelayinit)
                self.reboot_by_cmd = True
                self.reboot_by_cmd_time = time.time()
            ''' reboot cmd cancel '''
            else:
                self.my_statustext_send("Reboot ByCmd canceled")
                self.reboot_by_cmd = False
                self.reboot_by_cmd_time = 0

    def my_manage_init(self):
        ''' manage : shutdown ByLowBat requested '''
        if self.shutdown_by_lowbat == True and self.shutdown_by_lowbat_time != 0 and time.time() > self.shutdown_by_lowbat_time + self.settings.mydelayinit:
            self.my_statustext_send("Shutdown ByLowBat now")
            self.my_subprocess(["init","0"])
        if self.shutdown_by_lowbat == True:
            delta = self.settings.mydelayinit - int(time.time() - self.shutdown_by_lowbat_time)
            self.my_statustext_send("Shutdown ByLowBat left %ssec" % delta)
        ''' manage : shutdown ByRadio requested '''
        if self.shutdown_by_radio == True and self.shutdown_by_radio_time != 0 and time.time() > self.shutdown_by_radio_time + self.settings.mydelayinit:
            self.my_statustext_send("Shutdown ByRadio now")
            self.my_subprocess(["init","0"])
        if self.shutdown_by_radio == True:
            delta = self.settings.mydelayinit - int(time.time() - self.shutdown_by_radio_time)
            self.my_statustext_send("Shutdown ByRadio left %ssec" % delta)
        ''' manage : reboot ByRadio requested '''
        if self.reboot_by_radio == True and self.reboot_by_radio_time != 0 and time.time() > self.reboot_by_radio_time + self.settings.mydelayinit:
            self.my_statustext_send("Reboot ByRadio now")
            self.my_subprocess(["init","6"])
        if self.reboot_by_radio == True:
            delta = self.settings.mydelayinit - int(time.time() - self.reboot_by_radio_time)
            self.my_statustext_send("Reboot ByRadio left %ssec" % delta)
        ''' manage : shutdown ByCmd requested '''
        if self.shutdown_by_cmd == True and self.shutdown_by_cmd_time != 0 and time.time() > self.shutdown_by_cmd_time + self.settings.mydelayinit:
            self.my_statustext_send("Shutdown ByCmd now")
            self.my_subprocess(["init","0"])
        if self.shutdown_by_cmd == True:
            delta = self.settings.mydelayinit - int(time.time() - self.shutdown_by_cmd_time)
            self.my_statustext_send("Shutdown ByCmd left %ssec" % delta)
        ''' manage : reboot ByCmd requested '''
        if self.reboot_by_cmd == True and self.reboot_by_cmd_time != 0 and time.time() > self.reboot_by_cmd_time + self.settings.mydelayinit:
            self.my_statustext_send("Reboot ByCmd now")
            self.my_subprocess(["init","6"])
        if self.reboot_by_cmd == True:
            delta = self.settings.mydelayinit - int(time.time() - self.reboot_by_cmd_time)
            self.my_statustext_send("Reboot ByCmd left %ssec" % delta)

    def my_statustext_check(self):
            msg = "MySeverity %s MyStatusText %s" % (self.myseverity,self.mytext)
            self.my_write_log("INFO",msg)

    def my_battery_check(self):
       if time.time() > self.last_battery_check_time + self.settings.mytimebat:
                self.last_battery_check_time = time.time()
                # System Status STANDBY = 3
                if self.armed == False and self.mystate == 3 and (self.myvolt <= self.settings.myminvolt or self.myremaining <= self.settings.myminremain):
                    msg = "LowVolt <=%s or LowRemain <=%s : Shutdown ByLowBat in progress..." % (self.settings.myminvolt,self.settings.myminremain)
                    self.my_write_log("WARNING",msg)
                    if self.shutdown_by_lowbat == False:
                        self.my_statustext_send("Shutdown ByLowBat after %ssec" % self.settings.mydelayinit)
                        self.shutdown_by_lowbat = True
                        self.shutdown_by_lowbat_time = time.time()
                elif self.myvolt <= self.settings.myminvolt or self.myremaining <= self.settings.myminremain:
                    msg = "LowVolt <=%s or LowRemain <=%s : Shutdown ByLowBat needed" % (self.settings.myminvolt,self.settings.myminremain)
                    self.my_write_log("WARNING",msg)
                    self.my_statustext_send("Warning voltage shutdown needed")
                else:
                    msg = "LowVolt >%s or LowRemain >%s : Good status" % (self.settings.myminvolt,self.settings.myminremain)
                    self.my_write_log("INFO",msg)
                # check init 0 or 6
                self.my_manage_init()

    def my_rc_check(self):
       if time.time() > self.last_rc_check_time + self.settings.mytimerc:
           self.last_rc_check_time = time.time()
           if self.settings.mydebug:
               print("cmd_mybat %s" % self)
               msg = "RC1:%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s" % (self.myrc1raw,self.myrc2raw,self.myrc3raw,self.myrc4raw,self.myrc5raw,self.myrc6raw,self.myrc7raw,self.myrc8raw)
               self.my_write_log("INFO",msg)
           ''' MANAGE WLAN0 UP DOWN : RC8 DOWN '''
           if self.myrc8raw > 0 and self.myrc8raw < self.RC8_low_mark:
               if self.wlan0_up == True:
                   self.wlan0_up = False
                   self.my_statustext_send("ifdown wlan0 RPI2")
                   self.my_subprocess(["ifdown","wlan0"])
               msg = "MyRC8Raw %s wlan0 is up : %s : RC8 DOWN" % (self.myrc8raw,self.wlan0_up)
               self.my_write_log("INFO",msg)
           ''' MANAGE WLAN0 UP DOWN : RC8 MIDDLE '''
           elif self.myrc8raw > self.RC8_low_mark and self.myrc8raw < self.RC8_high_mark:
               if self.wlan0_up == True:
                   self.wlan0_up = False
                   self.my_statustext_send("ifdown wlan0 RPI2")
                   self.my_subprocess(["ifdown","wlan0"])
               msg = "MyRC8Raw %s wlan0 is up : %s : RC8 MIDDLE" % (self.myrc8raw,self.wlan0_up)
               self.my_write_log("INFO",msg)
           ''' MANAGE WLAN0 UP DOWN : RC8 UP '''
           elif self.myrc8raw > self.RC8_high_mark:
               if self.wlan0_up == False:
                   self.wlan0_up = True
                   self.my_statustext_send("ifup wlan0 RPI2")
                   self.my_subprocess(["ifup","wlan0"])
               msg = "MyRC8Raw %s wlan0 is up : %s : RC8 UP" % (self.myrc8raw,self.wlan0_up)
               self.my_write_log("INFO",msg)
           else:
               msg = "MyRC8Raw %s wlan0 is up : %s : unknown RC8 value" % (self.myrc8raw,self.wlan0_up)
               self.my_write_log("WARNING",msg)
           ''' RC1 ROLL / RC2 PITCH / RC3 TROTTLE / RC4 YAW '''
           ''' MANAGE VIDEO OFF : RC7 UP '''
           if self.myrc7raw > self.RC7_high_mark:
               if self.video_on == True:
                   self.video_on = False
                   msg = "MyRC7raw %s MyVideo on %s : RC7 UP" % (self.myrc7raw,self.video_on)
                   self.my_write_log("INFO",msg)
                   self.my_statustext_send("Video off")
                   self.my_subprocess(["killall","raspivid"])
                   self.my_subprocess(["killall","tx"])
           ''' MANAGE VIDEO ON : RC7 DOWN '''
           if self.myrc7raw < self.RC7_low_mark:
               if self.video_on == False:
                   self.video_on = True
                   msg = "MyRC7raw %s MyVideo on %s : RC7 DOWN" % (self.myrc7raw,self.video_on)
                   self.my_write_log("INFO",msg)
                   self.my_statustext_send("Video on")
                   self.my_subprocess(["/usr/local/bin/start_video.sh"])
           if self.armed == False and self.mystate == 3:
               ''' MANAGE REBOOT YAM RC4 LOW and ROLL MAX RC1 '''
               if self.myrc4raw < self.RC4_low_mark and self.myrc1raw > self.RC1_high_mark:
                   if self.shutdown_by_radio == False:
                       msg = "MyRC2Raw %s MyRC3Raw %s : Shutdown ByRadio" % (self.myrc2raw,self.myrc3raw)
                       self.my_write_log("INFO",msg)
                       self.my_statustext_send("Shutdown ByRadio after %ssec" % self.settings.mydelayinit)
                       self.shutdown_by_radio = True
                       self.shutdown_by_radio_time = time.time()
                   ''' shutdown radio cancel '''
                   else:
                       self.my_statustext_send("Shutdown ByRadio canceled")
                       self.shutdown_by_radio = False
                       self.shutdown_by_radio_time = 0
               ''' MANAGE REBOOT YAM RC4 LOW and ROLL MIN RC1 '''
               if self.myrc4raw < self.RC4_low_mark and self.myrc1raw < self.RC1_low_mark:
                   if self.reboot_by_radio == False:
                       msg = "MyRC2Raw %s MyRC3Raw %s : Reboot ByRadio" % (self.myrc2raw,self.myrc3raw)
                       self.my_write_log("INFO",msg)
                       self.my_statustext_send("Reboot ByRadio after %ssec" % self.settings.mydelayinit)
                       self.reboot_by_radio = True
                       self.reboot_by_radio_time = time.time()
                   ''' rebootradio cancel '''
                   else:
                       self.my_statustext_send("Reboot ByRadio canceled")
                       self.reboot_by_radio = False
                       self.reboot_by_radio_time = 0
           ''' shutdown and reboot cancel if Armed '''
           if self.armed == True:
               if self.shutdown_by_radio == True:
                   self.my_statustext_send("Shutdown ByRadio canceled")
                   self.shutdown_by_radio = False
                   self.shutdown_by_radio_time = 0
               if self.reboot_by_radio == True:
                   self.my_statustext_send("Reboot ByRadio canceled")
                   self.reboot_by_radio = False
                   self.reboot_by_radio_time = 0
               if self.shutdown_by_lowbat == True:
                   self.my_statustext_send("Shutdown ByLowBat canceled")
                   self.shutdown_by_lowbat = False
                   self.shutdown_by_lowbat_time = 0
               if self.shutdown_by_cmd == True:
                   self.my_statustext_send("Shutdown ByCmd canceled")
                   self.shutdown_by_cmd = False
                   self.shutdown_by_cmd_time = 0
               if self.reboot_by_cmd == True:
                   self.my_statustext_send("Reboot ByCmd canceled")
                   self.reboot_by_cmd = False
                   self.reboot_by_cmd_time = 0
           # check init 0 or 6
           self.my_manage_init()

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

