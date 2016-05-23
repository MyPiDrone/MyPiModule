#TITLE# DRONE MAVProxy module MyPiModule to control RPI2i/NAVIO+ or RPI3/NAVIO2 
''' ----------------------------------------------------------------------------------- '''
''' MyPiDrone Project Kev&Phil : Copter QUAD Project 1 and Project 2 :                  '''
'''        Project 1 : TAROT 650 Copter QUAD with Raspberry PI2 & Navio+ controler      '''
'''        Project 2 : TAROT 280 Copter QUAD with Raspberry PI3 & Navio2 controler      '''
'''                    raspian Kernel 4.4.y                                             '''
''' www.MyPiDrone.com MyPiDrone kev&phil Project                                        '''
''' https://github.com/MyPiDrone/MyPiModule                                             '''
''' ----------------------------------------------------------------------------------- '''
''' Version 2.2 : May 18 2016                                                            '''
''' ----------------------------------------------------------------------------------- '''
''' README here: https://github.com/MyPiDrone/MyPiModule/blob/master/README.md          '''
''' ----------------------------------------------------------------------------------- '''

import time
from pymavlink import mavutil
from datetime import datetime

import subprocess

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib.mp_settings import MPSetting

class MyPiModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(MyPiModule, self).__init__(mpstate, "MyPiModule", "my commands")
        # my cmd
        self.add_command('mybat', self.cmd_mybat, "my battery information")
        self.add_command('myshut', self.cmd_myshutdown, "to shutdown")
        self.add_command('myreboot', self.cmd_myreboot, "to reboot")
        self.add_command('myrtl', self.cmd_myrtl, "change flight mode to tTL")
        self.add_command('mystabilize', self.cmd_mystabilize, "change flight mode to STABILIZE")
        # my settings
        self.settings.append(MPSetting('mytimebat', int, 5, 'Battery Interval Time sec', tab='my'))
        self.settings.append(MPSetting('mytimerc', int, 4, 'RC Interval Time sec'))
        self.settings.append(MPSetting('mydebug', bool, False, 'Debug'))
        self.settings.append(MPSetting('myminvolt', int, 10000, 'Minimum battery voltage before shutdown'))
        self.settings.append(MPSetting('myminremain', int, 10, 'Minimum battery remaining before shutdown'))
        self.settings.append(MPSetting('mydelayinit', int, 30, 'Delay before shutdown or reboot'))
        self.settings.append(MPSetting('myrcvideo', int, 6, 'Radio channel to change video on/off'))
        self.settings.append(MPSetting('myrcwlan', int, 8, 'Radio channel to change wlan on/off'))
        self.settings.append(MPSetting('myrcyaw', int, 4, 'Radio channel to reboot/shutdown'))
        self.settings.append(MPSetting('myrcroll', int, 1, 'Radio channel to reboot/shutdown'))
        self.settings.append(MPSetting('mywlan', str, "wlan0", 'Wlan interface name'))
        self.settings.append(MPSetting('mylog', str, "/var/log/mavproxy_MyPiModule.log", 'output filename log'))
        self.settings.append(MPSetting('mylogverbose', bool, False, 'Verbose log'))
        self.myversion = "2.2"
        self.myinit = False
        # stats
        self.VFR_HUD = 0
        self.SYS_STATUS = 0
        self.HEARTBEAT = 0
        self.RC_CHANNELS_RAW = 0
        self.battery_period_trigger = 0
        self.start_time = time.time()
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
        # default values
        self.armed = False
        self.myflags = "null"
        self.mystate = 0
        self.mystatename = ["UNINIT","BOOT","CALIBRATING","STANDBY","ACTIVE","CRITICAL","EMERGENCY","POWEROFF"]
        self.myvolt = 0
        self.mythrottle = 0
        self.mycurrent = 0
        self.myremaining = 0
        self.myrcraw = [0,0,0,0,0,0,0,0,0]
        self.wlan_up = False
        self.wlan_ip = "null"
        self.video_on = True
        self.rtl_on = False
        self.stabilize_on = False
        self.last_battery_check_time = time.time()
        self.last_rc_check_time = time.time()
        self.battery_period = mavutil.periodic_event(5)
        self.FORMAT = '%Y-%m-%d %H:%M:%S'
        #self.FORMAT2 = '%Hh%Mm%Ss'
        self.mycountermessage = 0
        # default to servo range of 990 to 2010
        self.RC_MIN = [0,990,990,990,990,990,990,990,990] 
        self.RC_TRIM = [0,1500,1500,1500,1500,1500,1500,1500,1500] 
        self.RC_MAX = [0,2010,2010,2010,2010,2010,2010,2010,2010] 
        self.RC_low_mark = [0,1245,1245,1245,1245,1245,1245,1245,1245] 
        self.RC_high_mark = [0,1755,1755,1755,1755,1755,1755,1755,1755]
        self.myseverity = 0
        self.mytext = "nulltext"
        # to send statustext
        #print("self.settings.source_system=%s" % self.settings.source_system)

    def my_write_log(self,level,msg):
        #OUTPUT FILE
        prefix = "Armed=%s MyState=%s NetUP=%s VideoON=%s MyThrottle=%s MyVolt=%s MyCurrent=%s MyRemaining=%s" % (self.armed,self.mystatename[self.mystate],self.wlan_up,self.video_on,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining)
        date = datetime.now().strftime(self.FORMAT)
        if self.settings.mydebug:
            print("%s %s %s %s" % (date,level,prefix,msg))
        if self.settings.mylogverbose or level == "WARNING" or level == "ERROR":
            fo = open(self.settings.mylog, "a")
            fo.write("%s %s %s %s\n" % (date,level,prefix,msg))
            fo.close()

    def my_network_status(self):
            p = subprocess.Popen(["/usr/local/bin/manage_network.sh","status",self.settings.mywlan], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdoutData, stderrData) = p.communicate()
            rc = p.returncode
            if (rc == 0):
                self.wlan_ip = stdoutData
                self.wlan_up = True
            else:
                self.wlan_ip = "null" 
                self.wlan_up = False 

    def my_video_status(self):
            p = subprocess.Popen(["/usr/local/bin/manage_video.sh","status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdoutData, stderrData) = p.communicate()
            rc = p.returncode
            if (rc == 0): self.video_on = True
            else: self.video_on = False

    def my_mode_status(self):
            if self.status.flightmode == "RTL": self.rtl_on = True
            else: self.rtl_on = False
            if self.status.flightmode == "STABILIZE": self.stabilize_on = True
            else: self.stabilize_on = False

    def my_init_var(self):
        if self.myinit == False:
            self.myinit = True
            self.my_statustext_send("MyPiModule %s" % self.myversion)
            ####################################################
            # reclaim params + version + frame type
            ####################################################
            self.master.param_fetch_all()
            ####################################################
            # init var rtl_on and stabilize_on
            ####################################################
            self.my_mode_status()
            self.my_statustext_send("mode %s" % self.status.flightmode)
            ####################################################
            # init var wlan_ip
            ####################################################
            self.my_network_status()
            if (self.wlan_up == True): self.my_statustext_send("%s ip %s" % (self.settings.mywlan,self.wlan_ip))
            else: self.my_statustext_send("%s ip missing" % self.settings.mywlan)
            ####################################################
            # video status
            ####################################################
            self.my_video_status()
            if (self.video_on == True): self.my_statustext_send("VIDEO ON")
            else: self.my_statustext_send("VIDEO OFF")

    def my_statustext_send(self,text):
        self.mycountermessage += 1
        self.master2 = mavutil.mavlink_connection("udp:127.0.0.1:14550", input=False, dialect="common", source_system=self.settings.source_system)
        #---------------------------------------------------
        #date2 = datetime.now().strftime(self.FORMAT2)
        #strutf8 = unicode("%s %s" % (date2,text))
        #strutf8 = unicode(" %02d %s" % (date2,text))
        #self.master2.mav.statustext_send(1, str(strutf8))
        #---------------------------------------------------
        #strutf8 = unicode("%s %s" % (self.mycountermessage,text))
        #self.master2.mav.statustext_send(1, str(strutf8))
        # 1=ALERT 2=CRITICAL 3=ERROR, 4=WARNING, 5=NOTICE, 6=INFO, 7=DEBUG, 8=ENUM_END
        self.master2.mav.statustext_send(1, " %02d %s" % (self.mycountermessage,text))
        self.master2.close()
        self.say(text)
        self.my_write_log("INFO",text)
        print ("INFO %02d %s" % (self.mycountermessage,text))

    def my_subprocess(self,cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutData, stderrData) = p.communicate()
        #rc = p.returncode
        msg = "cmd %s sdtout %s" % (cmd,stdoutData)
        self.my_write_log("INFO",msg)
        if self.settings.mydebug == False:
            print("INFO %s" % msg)
        msg = "cmd %s stderr %s" % (cmd,stderrData)
        self.my_write_log("INFO",msg)
        if self.settings.mydebug == False:
            print("INFO %s" % msg)

    def mymode(self,mode):
        print ("INFO request mode %s : current flightmode %s altitude %s" % (mode,self.status.flightmode,self.status.altitude))
        if mode == "RTL" or mode == "STABILIZE":
          mode_mapping = self.master.mode_mapping()
          modenum = mode_mapping[mode]
          if mode == "RTL":
            self.stabilize_on = False
	    if self.status.flightmode != mode:
              self.rtl_on = False
              print ("INFO request change mode to RTL modenum %s : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude))
              self.mpstate.functions.process_stdin("mode RTL")
              self.master.set_mode(modenum)
	      if self.status.flightmode != mode:
                print ("INFO change mode to RTL modenum %s not yet done : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude))
                self.my_statustext_send("mode %s RTL no yet" % self.status.flightmode)
              else:
                print ("INFO after change mode to RTL modenum %s : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude))
                self.my_statustext_send("mode %s" % self.status.flightmode)
            else:
              if self.rtl_on == False:
                print ("INFO change mode to RTL modenum %s already done : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude))
                self.my_statustext_send("mode %s" % self.status.flightmode)
                self.rtl_on = True
          if mode == "STABILIZE":
            self.rtl_on = False
	    if self.status.flightmode != mode:
              self.stabilize_on = False
              print ("INFO request change mode to STABILIZE modenum %s : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude))
              ###self.mpstate.functions.process_stdin("mode STABILIZE")
              self.master.set_mode(modenum)
	      if self.status.flightmode != mode:
                print ("INFO change mode to STABILIZE modenum %s not yet done : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude))
                self.my_statustext_send("mode %s STABILIZE not yet" % self.status.flightmode)
              else:
                print ("INFO after change mode to STABILIZE modenum %s : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude))
                self.my_statustext_send("mode %s" % self.status.flightmode)
            else:
              if self.stabilize_on == False:
                print ("INFO change mode to RTL modenum %s already done : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude))
                self.my_statustext_send("mode %s" % self.status.flightmode)
                self.stabilize_on = True
        else:
          print ("WARNING mode %s not supported : current flightmode %s altitude %s" % (mode,self.status.flightmode,self.status.altitude))
          self.my_statustext_send("mode %s not supported" % mode)

    def cmd_myrtl(self, args):
        self.mymode("RTL")

    def cmd_mystabilize(self, args):
        self.mymode("STABILIZE")

    def cmd_mybat(self, args):
        self.my_rc_check()
        if self.settings.mydebug:
           print("cmd_mybat %s" % self)
        self.my_network_status()
        msg = "LowVolt %s LowRemain %s" % (self.settings.myminvolt,self.settings.myminremain)
        self.my_write_log("INFO",msg)
        if self.settings.mydebug == False:
            prefix = "Armed=%s MyState=%s NetUP=%s VideoON=%s MyThrottle=%s MyVolt=%s MyCurrent=%s MyRemaining=%s" % (self.armed,self.mystatename[self.mystate],self.wlan_up,self.video_on,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining)
            print ("INFO %s %s" % (prefix,msg))
        msg = "RC1:%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s" % (self.myrcraw[1],self.myrcraw[2],self.myrcraw[3],self.myrcraw[4],self.myrcraw[5],self.myrcraw[6],self.myrcraw[7],self.myrcraw[8])
        self.my_write_log("INFO",msg)
        print ("INFO %s" % (msg))
        # stats
        current_time = time.time()
        elapse_time = int(current_time - self.start_time) + 1
        rate_VFR_HUD = int(self.VFR_HUD / elapse_time)
        rate_SYS_STATUS = int(self.SYS_STATUS / elapse_time)
        rate_HEARTBEAT = int(self.HEARTBEAT / elapse_time)
        rate_RC_CHANNELS_RAW = int(self.RC_CHANNELS_RAW / elapse_time)
        rate_battery_period_trigger = int(self.battery_period_trigger / elapse_time)
        msg = "INFO elapse_time %ssec rate_VFR_HUD %s=%s/sec rate_SYS_STATUS %s=%s/sec rate_HEARTBEAT %s=%s/sec rate_RC_CHANNELS_RAW %s=%s/sec rate_battery_period_trigger %s=%s/sec" % (elapse_time,self.VFR_HUD,rate_VFR_HUD,self.SYS_STATUS,rate_SYS_STATUS,self.HEARTBEAT,rate_HEARTBEAT,self.RC_CHANNELS_RAW,rate_RC_CHANNELS_RAW,self.battery_period_trigger,rate_battery_period_trigger)
        self.my_write_log("INFO",msg)
        print ("INFO %s" % (msg))
       
    def cmd_myshutdown(self, args):
        if self.armed == False and self.mystate == 3:
            if self.shutdown_by_cmd == False:
                self.my_statustext_send("Shutdown ByCmd %ssec" % self.settings.mydelayinit)
                self.shutdown_by_cmd = True
                self.shutdown_by_cmd_time = time.time()
            else:
                ''' shutdown cmd cancel '''
                self.my_statustext_send("Shutdown ByCmd canceled")
                self.shutdown_by_cmd = False
                self.shutdown_by_cmd_time = 0

    def cmd_myreboot(self, args):
        if self.armed == False and self.mystate == 3:
            if self.reboot_by_cmd == False:
                self.my_statustext_send("Reboot ByCmd %ssec" % self.settings.mydelayinit)
                self.reboot_by_cmd = True
                self.reboot_by_cmd_time = time.time()
            else:
                ''' reboot cmd cancel '''
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
            if delta <= 10:
                self.my_statustext_send("Shutdown ByLowBat %ssec" % delta)
        ''' manage : shutdown ByRadio requested '''
        if self.shutdown_by_radio == True and self.shutdown_by_radio_time != 0 and time.time() > self.shutdown_by_radio_time + self.settings.mydelayinit:
            self.my_statustext_send("Shutdown ByRadio now")
            self.my_subprocess(["init","0"])
        if self.shutdown_by_radio == True:
            delta = self.settings.mydelayinit - int(time.time() - self.shutdown_by_radio_time)
            if delta <= 10:
                self.my_statustext_send("Shutdown ByRadio %ssec" % delta)
        ''' manage : reboot ByRadio requested '''
        if self.reboot_by_radio == True and self.reboot_by_radio_time != 0 and time.time() > self.reboot_by_radio_time + self.settings.mydelayinit:
            self.my_statustext_send("Reboot ByRadio now")
            self.my_subprocess(["init","6"])
        if self.reboot_by_radio == True:
            delta = self.settings.mydelayinit - int(time.time() - self.reboot_by_radio_time)
            if delta <= 10:
                self.my_statustext_send("Reboot ByRadio %ssec" % delta)
        ''' manage : shutdown ByCmd requested '''
        if self.shutdown_by_cmd == True and self.shutdown_by_cmd_time != 0 and time.time() > self.shutdown_by_cmd_time + self.settings.mydelayinit:
            self.my_statustext_send("Shutdown ByCmd now")
            self.my_subprocess(["init","0"])
        if self.shutdown_by_cmd == True:
            delta = self.settings.mydelayinit - int(time.time() - self.shutdown_by_cmd_time)
            if delta <= 10:
                self.my_statustext_send("Shutdown ByCmd %ssec" % delta)
        ''' manage : reboot ByCmd requested '''
        if self.reboot_by_cmd == True and self.reboot_by_cmd_time != 0 and time.time() > self.reboot_by_cmd_time + self.settings.mydelayinit:
            self.my_statustext_send("Reboot ByCmd now")
            self.my_subprocess(["init","6"])
        if self.reboot_by_cmd == True:
            delta = self.settings.mydelayinit - int(time.time() - self.reboot_by_cmd_time)
            if delta <= 10:
                self.my_statustext_send("Reboot ByCmd %ssec" % delta)

    def my_statustext_check(self):
            msg = "MySeverity %s MyStatusText %s" % (self.myseverity,self.mytext)
            self.my_write_log("INFO",msg)

    def my_battery_check(self):
       if time.time() > self.last_battery_check_time + self.settings.mytimebat:
                self.last_battery_check_time = time.time()
                # System Status STANDBY = 3
                #if self.armed == False and self.mystate == 3 and (self.myvolt <= self.settings.myminvolt or self.myremaining <= self.settings.myminremain):
                if self.armed == False and self.mystate == 3 and (self.myvolt <= self.settings.myminvolt):
                    msg = "LowVolt <=%s or LowRemain <=%s : Shutdown ByLowBat in progress..." % (self.settings.myminvolt,self.settings.myminremain)
                    self.my_write_log("WARNING",msg)
                    if self.shutdown_by_lowbat == False:
                        self.my_statustext_send("Shutdown ByLowBat %ssec" % self.settings.mydelayinit)
                        self.shutdown_by_lowbat = True
                        self.shutdown_by_lowbat_time = time.time()
                elif self.myvolt <= self.settings.myminvolt or self.myremaining <= self.settings.myminremain:
                    msg = "LowVolt <=%s or LowRemain <=%s : Shutdown ByLowBat needed" % (self.settings.myminvolt,self.settings.myminremain)
                    self.my_write_log("WARNING",msg)
                    self.my_statustext_send("Shutdown ByLowBat needed")
                else:
                    msg = "LowVolt >%s or LowRemain >%s : Good status" % (self.settings.myminvolt,self.settings.myminremain)
                    self.my_write_log("INFO",msg)
                # check init 0 or 6
                self.my_manage_init()

    def my_rc_check(self):
       if time.time() > self.last_rc_check_time + self.settings.mytimerc:
           self.last_rc_check_time = time.time()
           if self.settings.mydebug:
               msg = "RC1:%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s" % (self.myrcraw[1],self.myrcraw[2],self.myrcraw[3],self.myrcraw[4],self.myrcraw[5],self.myrcraw[6],self.myrcraw[7],self.myrcraw[8])
               self.my_write_log("INFO",msg)
           if self.myrcraw[self.settings.myrcwlan] < self.RC_low_mark[self.settings.myrcwlan] and self.myrcraw[self.settings.myrcwlan] > (self.RC_low_mark[self.settings.myrcwlan]-100):
               ''' MANAGE mode STABILIZE : RC8 LOW range RC_low_mark-100 to RC_low_mark '''
               self.mymode("STABILIZE")
           elif self.myrcraw[self.settings.myrcwlan] > 0 and self.myrcraw[self.settings.myrcwlan] < self.RC_low_mark[self.settings.myrcwlan]:
               ''' MANAGE WLAN0 UP : RC8 LOW '''
               if self.wlan_up == True:
                   self.wlan_up = False
                   self.wlan_ip = "null"
                   self.my_statustext_send("%s down" % self.settings.mywlan)
                   self.my_subprocess(["/usr/local/bin/manage_network.sh","stop",self.settings.mywlan])
               msg = "MyRC%sRaw %s LOW : %s is up : %s" % (self.settings.myrcwlan,self.myrcraw[self.settings.myrcwlan],self.settings.mywlan,self.wlan_up)
               self.my_write_log("INFO",msg)
           elif self.myrcraw[self.settings.myrcwlan] > self.RC_low_mark[self.settings.myrcwlan] and self.myrcraw[self.settings.myrcwlan] < self.RC_high_mark[self.settings.myrcwlan]:
               ''' MANAGE WLAN0 DOWN : RC8 MIDDLE '''
               if self.wlan_up == True:
                   self.wlan_up = False
                   self.wlan_ip = "null"
                   self.my_statustext_send("%s down" % self.settings.mywlan)
                   self.my_subprocess(["/usr/local/bin/manage_network.sh","stop",self.settings.mywlan])
               msg = "MyRC%sRaw %s MIDDLE : %s is up : %s" % (self.settings.myrcwlan,self.myrcraw[self.settings.myrcwlan],self.settings.mywlan,self.wlan_up)
               self.my_write_log("INFO",msg)
           elif self.myrcraw[self.settings.myrcwlan] > self.RC_high_mark[self.settings.myrcwlan] and self.myrcraw[self.settings.myrcwlan] < (self.RC_high_mark[self.settings.myrcwlan]+100) :
               ''' MANAGE mode RTL : RC8 HIGH range RC_high_mark to RC_high_mark+100 '''
               self.mymode("RTL")
           elif self.myrcraw[self.settings.myrcwlan] > self.RC_high_mark[self.settings.myrcwlan]:
               ''' MANAGE WLAN0 UP : RC8 HIGH '''
               if self.wlan_up == False:
                   self.wlan_up = True
                   self.my_subprocess(["/usr/local/bin/manage_network.sh","start",self.settings.mywlan])
               if self.wlan_ip == "null":
                   self.my_network_status()
                   if (self.self.wlan_up == True): self.my_statustext_send("%s ip %s" % (self.settings.mywlan,self.wlan_ip))
                   else: self.my_statustext_send("%s ip missing" % self.settings.mywlan)
               msg = "MyRC%sRaw %s LOW : %s is up : %s" % (self.settings.myrcwlan,self.myrcraw[self.settings.myrcwlan],self.settings.mywlan,self.wlan_up)
               self.my_write_log("INFO",msg)
           else:
               msg = "RC1:%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s unknown RC value" % (self.myrcraw[1],self.myrcraw[2],self.myrcraw[3],self.myrcraw[4],self.myrcraw[5],self.myrcraw[6],self.myrcraw[7],self.myrcraw[8])
               self.my_write_log("WARNING",msg)
           ''' RC1 ROLL / RC2 PITCH / RC3 TROTTLE / RC4 YAW '''
           ''' MANAGE VIDEO OFF : RC6 HIGH '''
           if self.myrcraw[self.settings.myrcvideo] > self.RC_high_mark[self.settings.myrcvideo]:
               if self.video_on == True:
                   self.video_on = False
                   msg = "MyRC%sraw %s HIGH : MyVideo on %s" % (self.settings.myrcvideo,self.myrcraw[self.settings.myrcvideo],self.video_on)
                   self.my_write_log("INFO",msg)
                   self.my_statustext_send("Video off")
                   self.my_subprocess(["/usr/local/bin/manage_video.sh","stop"])
           ''' MANAGE VIDEO ON : RC6 LOW '''
           if self.myrcraw[self.settings.myrcvideo] > 0 and self.myrcraw[self.settings.myrcvideo] < self.RC_low_mark[self.settings.myrcvideo]:
               if self.video_on == False:
                   self.video_on = True
                   msg = "MyRC%sraw %s LOW : MyVideo on %s" % (self.settings.myrcvideo,self.myrcraw[self.settings.myrcvideo],self.video_on)
                   self.my_write_log("INFO",msg)
                   self.my_statustext_send("Video on")
                   self.my_subprocess(["/usr/local/bin/manage_video.sh","start"])
           if self.armed == False and self.mystate == 3:
               ''' MANAGE REBOOT YAW RC4 LOW and ROLL MAX RC1 '''
               if self.myrcraw[self.settings.myrcyaw] > 0 and self.myrcraw[self.settings.myrcyaw] < self.RC_low_mark[self.settings.myrcyaw] and self.myrcraw[self.settings.myrcroll] > self.RC_high_mark[self.settings.myrcroll]:
                   if self.shutdown_by_radio == False:
                       msg = "MyRC%sRaw %s MyRC%sRaw %s : Shutdown ByRadio" % (self.settings.myrcyaw,self.myrcraw[self.settings.myrcyaw],self.settings.myrcroll,self.myrcraw[self.settings.myrcroll])
                       self.my_write_log("INFO",msg)
                       self.my_statustext_send("Shutdown ByRadio %ssec" % self.settings.mydelayinit)
                       self.shutdown_by_radio = True
                       self.shutdown_by_radio_time = time.time()
                   else:
                       ''' shutdown radio cancel '''
                       self.my_statustext_send("Shutdown ByRadio canceled")
                       self.shutdown_by_radio = False
                       self.shutdown_by_radio_time = 0
               ''' MANAGE REBOOT YAW RC4 LOW and ROLL MIN RC1 '''
               if self.myrcraw[self.settings.myrcyaw] > 0 and self.myrcraw[self.settings.myrcyaw] < self.RC_low_mark[self.settings.myrcyaw] and self.myrcraw[self.settings.myrcroll] > 0 and self.myrcraw[self.settings.myrcroll] < self.RC_low_mark[self.settings.myrcroll]:
                   if self.reboot_by_radio == False:
                       msg = "MyRC%sRaw %s MyRC%sRaw %s : Reboot ByRadio" % (self.settings.myrcyaw,self.myrcraw[self.settings.myrcyaw],self.settings.myrcroll,self.myrcraw[self.settings.myrcroll])
                       self.my_write_log("INFO",msg)
                       self.my_statustext_send("Reboot ByRadio %ssec" % self.settings.mydelayinit)
                       self.reboot_by_radio = True
                       self.reboot_by_radio_time = time.time()
                   else:
                       ''' rebootradio cancel '''
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
            self.VFR_HUD += 1
            self.armed = self.master.motors_armed()
            self.mythrottle = m.throttle
        if mtype == "SYS_STATUS":
            self.SYS_STATUS += 1
            self.myvolt = m.voltage_battery
            self.mycurrent = m.current_battery
            self.myremaining = m.battery_remaining
            self.my_battery_check()
        if mtype == "HEARTBEAT":
            self.HEARTBEAT += 1
            self.mystate = m.system_status
            if (self.myinit == False and self.HEARTBEAT == 15):
                print ("INFO HEARTBEAT sequence %s : init var network, video, mode" % self.HEARTBEAT)
                self.my_init_var()
            seq = self.HEARTBEAT % 30
            if (seq == 0):
                self.my_network_status()
                self.my_video_status()
                self.my_mode_status()
                print ("INFO HEARTBEAT sequence %s : recheck status : network %s, video %s, mode RTL %s, mode STABILIZE: %s" % (self.HEARTBEAT,self.wlan_up,self.video_on,self.rtl_on,self.stabilize_on))
                if (self.wlan_up == True): NS = "N*"
                else: NS = "N_"
                if (self.video_on == True): VO = "V*"
                else: VO="V_"
                if (self.rtl_on == True): MR = "R*"
                else: MR = "R_"
                if (self.stabilize_on == True): MS = "S*"
                else: MS = "S_"
                flags="%s%s%s%s" % (NS,VO,MR,MS)
                if (flags != self.myflags):
                    self.myflags = flags    
                    self.my_statustext_send("%s" % self.myflags)
                    print ("MIN  : %s" % self.RC_MIN)
                    print ("TRIM : %s" % self.RC_TRIM)
                    print ("MAX  : %s" % self.RC_MAX)
                    print ("low  : %s" % self.RC_low_mark)
                    print ("high : %s" % self.RC_high_mark)
        if mtype == "RC_CHANNELS_RAW":
            self.RC_CHANNELS_RAW += 1
            self.myrcraw[1] = m.chan1_raw ; self.myrcraw[2] = m.chan2_raw ; self.myrcraw[3] = m.chan3_raw ; self.myrcraw[4] = m.chan4_raw
            self.myrcraw[5] = m.chan5_raw ; self.myrcraw[6] = m.chan6_raw ; self.myrcraw[7] = m.chan7_raw ; self.myrcraw[8] = m.chan8_raw
            self.my_rc_check()
        if mtype == "STATUSTEXT":
            self.myseverity = m.severity
            self.mytext = m.text
            self.my_statustext_check()
        if mtype == "PARAM_VALUE":
            print("PARAM_VALUE %s %s" % (m.param_id,m.param_value))
            for i in range(1,8):
                print ("%s" % i)
                if (m.param_id == "RC%s_TRIM" % i): self.RC_TRIM[i]=m.param_value
                if (m.param_id == "RC%s_MIN" % i): self.RC_MIN[i] = m.param_value
                if (m.param_id == "RC%s_MAX" % i): self.RC_MAX[i]=m.param_value
                self.RC_low_mark[i] = ((self.RC_TRIM[i] - self.RC_MIN[i]) // 2) + self.RC_MIN[i]
                self.RC_high_mark[i] = self.RC_MAX[i] - ((self.RC_MAX[i] - self.RC_TRIM[i]) // 2)
#not used
#      if self.battery_period.trigger():
#           self.battery_period_trigger += 1
#           self.my_battery_check()
#
#    def idle_task(self):
#        '''handle missing parameters'''
#        myvehicle_name = self.vehicle_name
#        #print ("self.vehicle_name=%s" % self.vehicle_name)

def init(mpstate):
    '''initialise module'''
    return MyPiModule(mpstate)

