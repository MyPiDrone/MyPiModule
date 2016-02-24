''' MyPiModule for MyPIDrone '''
''' Version 1.0              '''

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
        self.armed = False
        self.mystate = 0
        self.myvolt = 0
        self.throttle = 0
        self.mycurrent = 0
        self.myremaining = 0
        self.myrc1raw = 0
        self.myrc2raw = 0
        self.myrc3raw = 0
        self.myrc4raw = 0
        self.myrc5raw = 0
        self.myrc6raw = 0
        self.myrc7raw = 0
        self.myrc8raw = 0
        self.wlan0_up = False
        self.last_battery_check_time = time.time()
        self.last_rc_check_time = time.time()
        self.settings.append(MPSetting('mytimebat', int, 10, 'Battery Interval Time sec', tab='my'))
        self.settings.append(MPSetting('mytimerc', int, 10, 'RC Interval Time sec'))
        self.battery_period = mavutil.periodic_event(5)
        self.FORMAT = '%Y-%m-%d %H:%M:%S'
        self.FORMAT2 = '%Hh%Mm%Ss'
        # default to servo range of 1000 to 1700
        #self.RC1_low_mark  = self.get_mav_param('RC1_low_mark', 0)
        #self.RC1_high_mark  = self.get_mav_param('RC1_high_mark', 0)
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
        fo = open("/var/log/mavproxy_MyPiModule.log", "a")
        fo.write("%s\n" % msg)
        fo.close()
	
    def my_battery_check(self):
       date = datetime.now().strftime(self.FORMAT)
       date2 = datetime.now().strftime(self.FORMAT2)
       if time.time() > self.last_battery_check_time + self.settings.mytimebat:
                self.last_battery_check_time = time.time()
                # System Status STANDBY = 3
                if self.armed == False and self.mystate == 3 and (self.myvolt <= 10000 or self.myremaining <= 10):
                    #OUTPUT FILE
                    fo = open("/var/log/mavproxy_MyPiModule.log", "a")
                    msg = "%s WARNING Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s : Shutdown in progress..." % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw)
                    print("%s" % msg)
                    fo.write("%s\n" % msg)
                    fo.close()
                    self.say("Shutdown after 60sec.")
                    strutf8 = unicode("Shutdown after 60sec at %s" % date2, "utf-8")
                    self.master2.mav.statustext_send(1, str(strutf8))
                    time.sleep(60)
                    p = subprocess.Popen(["init", "0"], stdout=subprocess.PIPE)
                    #p = subprocess.Popen(["uptime"], stdout=subprocess.PIPE)
                    output, err = p.communicate()
                    print("Shutdown RPI2 output %s" % output)
                elif self.myvolt <= 10000 or self.myremaining <= 10:
                    #OUTPUT FILE
                    fo = open("/var/log/mavproxy_MyPiModule.log", "a")
                    msg = "%s WARNING Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s : Shutdown needed" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw)
                    print("%s" % msg)
                    fo.write("%s\n" % msg)
                    fo.close()
                    strutf8 = unicode("Warning voltage shutdown needed at %s" % date2, "utf-8")
                    self.master2.mav.statustext_send(1, str(strutf8))
                else:
                    #OUTPUT FILE
                    fo = open("/var/log/mavproxy_MyPiModule.log", "a")
                    msg = "%s INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s : Good Status" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw)
                    print("%s" % msg)
                    fo.write("%s\n" % msg)
                    fo.close()

    def my_rc_check(self):
       if time.time() > self.last_rc_check_time + self.settings.mytimerc:
           self.last_rc_check_time = time.time()
           # default to servo range of 1000 to 1700
           #self.RC1_low_mark  = self.get_mav_param('RC1_low_mark', 0)
           #self.RC1_high_mark  = self.get_mav_param('RC1_high_mark', 0)
           date = datetime.now().strftime(self.FORMAT)
           date2 = datetime.now().strftime(self.FORMAT2)
           msg = "%s INFO Armed: %s RC1:%s %s-%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s" % (date,self.armed,self.myrc1raw,self.RC1_low_mark,self.RC1_high_mark,self.myrc2raw,self.myrc3raw,self.myrc4raw,self.myrc5raw,self.myrc6raw,self.myrc7raw,self.myrc8raw)
           fo = open("/var/log/mavproxy_MyPiModule.log", "a")
           print("%s" % msg)
           fo.write("%s\n" % msg)
           ######## MANAGE WLAN0 UP DOWN
           if self.myrc8raw > 0 and self.myrc8raw < self.RC8_low_mark:
               if self.wlan0_up == True:
                   self.say("ifdown wlan0")
                   p = subprocess.Popen(["ifdown", "wlan0"], stdout=subprocess.PIPE)
                   output, err = p.communicate()
                   print("ifdown wlan0 RPI2 output %s" % output)
                   self.wlan0_up = False
                   strutf8 = unicode("ifdown wlan0 RPI2 at %s" % date2, "utf-8")
                   self.master2.mav.statustext_send(1, str(strutf8))
               msg = "%s INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s wlan0 is up : %s : DOWN 1200" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw,self.wlan0_up)
           elif self.myrc8raw > self.RC8_low_mark and self.myrc8raw < self.RC8_high_mark:
               if self.wlan0_up == True:
                   self.say("ifdown wlan0")
                   p = subprocess.Popen(["ifdown", "wlan0"], stdout=subprocess.PIPE)
                   output, err = p.communicate()
                   print("ifdown wlan0 RPI2 output %s" % output)
                   self.wlan0_up = False
                   strutf8 = unicode("ifdown wlan0 RPI2 at %s" % date2, "utf-8")
                   self.master2.mav.statustext_send(1, str(strutf8))
               msg = "%s INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s wlan0 is up : %s : MIDDLE 1200-1700" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw,self.wlan0_up)
           elif self.myrc8raw > self.RC8_high_mark:
               if self.wlan0_up == False:
                   self.say("ifup wlan0")
                   p = subprocess.Popen(["ifup", "wlan0"], stdout=subprocess.PIPE)
                   output, err = p.communicate()
                   print("ifup wlan0 RPI2 output %s" % output)
                   self.wlan0_up = True
                   strutf8 = unicode("ifup wlan0 RPI2 at %s" % date2, "utf-8")
                   self.master2.mav.statustext_send(1, str(strutf8))
               msg = "%s INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s wlan0 is up : %s : UP 1700" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw,self.wlan0_up)
           else:
               msg = "%s WARNING Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s wlan0 is up : %s : unknown RC value" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw,self.wlan0_up)
           print("%s" % msg)
           fo.write("%s\n" % msg)
           fo.close()
           # RC1 ROLL
           # RC2 PITCH
           # RC3 TROTTLE
           # RC4 YAW
           ######## MANAGE SHUTDOWN TROTTLE MAX RC3 > 1700 and PITCH MAX RC2 > 1700
           if self.armed == False and self.mystate == 3 and self.myrc2raw > self.RC2_high_mark and self.myrc3raw > self.RC3_high_mark:
               msg = "%s INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC2Raw %s MyRC3Raw %s : Shutdown" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc2raw,self.myrc3raw)
               print("%s" % msg)
               fo = open("/var/log/mavproxy_MyPiModule.log", "a")
               fo.write("%s\n" % msg)
               fo.close()
               self.say("Shutdown in progress...")
               strutf8 = unicode("Shutdown in progress at %s" % date2, "utf-8")
               self.master2.mav.statustext_send(1, str(strutf8))
               #time.sleep(60)
               p = subprocess.Popen(["init","0"], stdout=subprocess.PIPE)
               #p = subprocess.Popen(["uptime"], stdout=subprocess.PIPE)
               output, err = p.communicate()
               print("Shutdown RPI2 output %s" % output)

    def my_statustext_check(self):
            date = datetime.now().strftime(self.FORMAT)
            date2 = datetime.now().strftime(self.FORMAT2)
            msg = "%s INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MySeverity %s MyStatusText %s" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myseverity,self.mytext)
            print("%s" % msg)
            fo = open("/var/log/mavproxy_MyPiModule.log", "a")
            fo.write("%s\n" % msg)
            fo.close()

    def cmd_mybat(self, args):
        date = datetime.now().strftime(self.FORMAT)
        date2 = datetime.now().strftime(self.FORMAT2)
        #OUTPUT FILE
        print("cmd_mybat %s" % self)
        msg = "%s INFO Armed: %s MyState: %s Mythrottle %s MyVolt %s MyCurrent %s MyRemaining %s MyRC8Raw %s" % (date,self.armed,self.mystate,self.throttle,self.myvolt,self.mycurrent,self.myremaining,self.myrc8raw)
        print("%s" % msg)
        self.my_write_log(msg)
        self.my_rc_check()

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
            self.throttle = m.throttle
        if mtype == "SYS_STATUS":
            self.myvolt = m.voltage_battery
            self.mycurrent = m.current_battery
            self.myremaining = m.battery_remaining
            self.my_battery_check()
        if mtype == "HEARTBEAT":
            self.mystate = m.system_status
        if mtype == "RC_CHANNELS_RAW":
            self.myrc1raw = m.chan1_raw
            self.myrc2raw = m.chan2_raw
            self.myrc3raw = m.chan3_raw
            self.myrc4raw = m.chan4_raw
            self.myrc5raw = m.chan5_raw
            self.myrc6raw = m.chan6_raw
            self.myrc7raw = m.chan7_raw
            self.myrc8raw = m.chan8_raw
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

