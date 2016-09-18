#TITLE# DRONE MAVProxy module MyPiModule to control RPI2i/NAVIO+ or RPI3/NAVIO2 
''' ----------------------------------------------------------------------------------- '''
''' MyPiDrone Project Kev&Phil : Copter QUAD Project 1 and Project 2 :                  '''
'''        Project 1 : TAROT 650 Copter QUAD with Raspberry PI2 & Navio+ controler      '''
'''        Project 2 : TAROT 280 Copter QUAD with Raspberry PI3 & Navio2 controler      '''
'''                    raspian Kernel 4.4.y                                             '''
''' www.MyPiDrone.com MyPiDrone kev&phil Project                                        '''
''' https://github.com/MyPiDrone/MyPiModule                                             '''
''' ----------------------------------------------------------------------------------- '''
''' Version 2.3 : September 4 2016                                                      '''
''' MyPiModule new version : Overlaying telemetry text on video before Wifibroadcasting '''
''' ----------------------------------------------------------------------------------- '''
''' README here: https://github.com/MyPiDrone/MyPiModule/blob/master/README.md          '''
''' ----------------------------------------------------------------------------------- '''

import os, sys, math, time
import picamera
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
        self.settings.append(MPSetting('mytimebat', int, 5, 'Battery refresh Interval Time sec', tab='my'))
        self.settings.append(MPSetting('mytimeTText', int, 1, 'Telemetry text refresh Interval Time sec'))
        self.settings.append(MPSetting('mytimerc', int, 4, 'RC refresh Interval Time sec'))
        self.settings.append(MPSetting('myseqinit', int, 15, 'Time sec before init var and start polling'))
        self.settings.append(MPSetting('myseqpoll', int, 10, 'Time sec between poll status Network, Video, mode'))
        self.settings.append(MPSetting('mydebug', bool, False, 'Debug'))
        self.settings.append(MPSetting('myminvolt', int, 10000, 'Minimum battery voltage before shutdown'))
        self.settings.append(MPSetting('myminremain', int, 10, 'Minimum battery remaining before shutdown'))
        self.settings.append(MPSetting('mydelayinit', int, 30, 'Delay before shutdown or reboot'))
        self.settings.append(MPSetting('myrcvideo', int, 6, 'Radio channel to change video on/off'))
        self.settings.append(MPSetting('myrcnet', int, 8, 'Radio channel to change network on/off'))
        self.settings.append(MPSetting('myrcyaw', int, 4, 'Radio channel to reboot/shutdown'))
        self.settings.append(MPSetting('myrcroll', int, 1, 'Radio channel to reboot/shutdown'))
        self.settings.append(MPSetting('myinterfaceadmin', str, "wlan0", 'Network admin interface name'))
        self.settings.append(MPSetting('myinterfacetx', str, "wlan1", 'Wifibroadcast interface name'))
        self.settings.append(MPSetting('mychanneltx', str, "-19", 'Channel wifibroadcast interface name'))
        self.settings.append(MPSetting('mylog', str, "/var/log/mavproxy_MyPiModule.log", 'output filename log'))
        self.settings.append(MPSetting('myvideopath', str, "/root/fpv/videos", 'output video directory'))
        self.settings.append(MPSetting('mypipeout', str, "/tmp/MyPiCamera.pipeout", 'Named pipe for tx'))
        self.settings.append(MPSetting('mylogverbose', bool, False, 'Verbose log'))
        self.myversion = "2.3"
        self.myinit = False
        self.mylogverbose = self.settings.mylogverbose
        self.mydebug = self.settings.mydebug
        # stats
        self.GPS_RAW = 0
        self.GPS_RAW_INT = 0
        self.ATTITUDE = 0
        self.VFR_HUD = 0
        self.SYS_STATUS = 0
        self.HEARTBEAT = 0
        self.RC_CHANNELS_RAW = 0
        self.RADIO = 0
        self.PARAM_VALUE = 0
        self.STATUSTEXT = 0
        self.OTHER = 0
        self.battery_period_trigger = 0
        self.my_start_time = time.time()
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
        self.mystate = 0
        self.mystatename = ["UNINIT","BOOT","CALIBRATING","STANDBY","ACTIVE","CRITICAL","EMERGENCY","POWEROFF"]
        self.myvolt = 0
        self.mythrottle = 0
        self.mygroundspeed = 0
        self.mycurrent = 0
        self.myremaining = 0
        self.myrcraw = [0,0,0,0,0,0,0,0,0]
        #
        self.net_up_request = False
        self.net_up_request_time = time.time()
        self.net_up_request_retry = 20
        self.net_up = False
        self.net_up_prev = False
        self.net_ip_current = "null"
        #
        self.video_on_request = False
        self.video_on_request_time = time.time()
        self.video_on_request_retry = 20
        self.video_on = True
        self.video_on_prev = True
        #
        self.rtl_on_request = False
        self.rtl_on_request_time = time.time()
        self.rtl_on_request_retry = 20
        self.rtl_on = False
        self.rtl_on_prev = False
        #
        self.stabilize_on_request = False
        self.stabilize_on_request_time = time.time()
        self.stabilize_on_request_retry = 20
        self.stabilize_on = False
        self.stabilize_on_prev = False
        #
        self.last_battery_check_time = time.time()
        self.last_TText_check_time = time.time()
        self.last_rc_check_time = time.time()
        self.last_seq_time = time.time()
        self.last_init_time = time.time()
        self.battery_period = mavutil.periodic_event(5)
        self.FORMAT = '%Y-%m-%d %H:%M:%S'
        #self.FORMAT2 = '%Hh%Mm%Ss'
        self.mycountermessage = 0
        # default to servo range of 990 to 2010
        self.RC_MIN = [0,990,990,990,990,990,990,990,990,0,0,0,0,0,0,0,0,0] 
        self.RC_TRIM = [0,1500,1500,1500,1500,1500,1500,1500,1500,0,0,0,0,0,0,0,0,0] 
        self.RC_MAX = [0,2010,2010,2010,2010,2010,2010,2010,2010,0,0,0,0,0,0,0,0,0] 
        self.RC_low_mark = [0,1245,1245,1245,1245,1245,1245,1245,1245,0,0,0,0,0,0,0,0,0] 
        self.RC_high_mark = [0,1755,1755,1755,1755,1755,1755,1755,1755,0,0,0,0,0,0,0,0,0]
        self.myparamcount = 0
        self.myparamcount_prev = 0
        self.myseverity = 0
        self.mytext = "nulltext"
        ##########################################################################################################
        # pipe with tx start with this script :
        # /usr/local/bin/start_tx_and_recording_with_picamera_video_input.sh wlan1 -19 --vbr
        # convert to mp4 sample :
        # avconv -stats -y -r 49 -i Video-Tarot-2016-09-08_21:15.h264 -vcodec copy  Video-Tarot-2016-09-08_21:15.mp4
        ##########################################################################################################
        try:
            os.mkfifo(self.settings.mypipeout)
        except OSError:
            pass
        with open("/var/log/start_tx_with_video_recording.log","wb") as out, open("/var/log/start_tx_with_video_recording.log","wb") as err:
           subprocess.Popen(["/usr/local/bin/start_tx_and_recording_with_picamera_video_input.sh",self.settings.myinterfacetx,self.settings.mychanneltx,"--vbr"],stdout=out,stderr=err)
        print ("/usr/local/bin/start_tx_and_recording_with_picamera_video_input.sh %s %s --vbr is starting : waiting %s opening..." % (self.settings.myinterfacetx,self.settings.mychanneltx,self.settings.mypipeout))
        self.outpipe = open(self.settings.mypipeout, 'w')
        ###############################################################################
        # V1 camera
        #Mode   Size    Aspect Ratio    Frame rates     Video Image  FOV     Binning
        #0      automatic selection
        #1      1920x1080       16:9    1-30fps         x            Partial None
        #2      2592x1944       4:3     1-15fps         x      x     Full    None
        #3      2592x1944       4:3     0.1666-1fps     x      x     Full    None
        #4      1296x972        4:3     1-42fps         x            Full    2x2
        #5      1296x730        16:9    1-49fps         x            Full    2x2
        #6      640x480         4:3     42.1-60fps      x            Full    2x2 plus skip
        #7      640x480         4:3     60.1-90fps      x          Full    2x2 plus skip
        ###############################################################################
        # V2 camera
        # Mode Resolution Aspect Ratio Framerates Video Image FoV     Binning
        # 1    1920x1080        16:9    0.1-30fps  x        Partial   None 
        # 2    3280x2464        4:3     0.1-15fps  x    x   Full      None 
        # 3    3280x2464        4:3     0.1-15fps  x    x   Full      None 
        # 4    1640x1232        4:3     0.1-40fps  x        Full      2x2 
        # 5    1640x922         16:9    0.1-40fps  x        Full      2x2 
        # 6    1280x720         16:9    40-90fps   x        Partial   2x2 
        # 7    640x480          4:3     40-90fps   x        Partial   2x2 
        ###############################################################################
        # image_effect  'none' 'negative' 'solarize' 'sketch' 'denoise' 'emboss' 'oilpaint' 'hatch' 'gpen' 'pastel' 'watercolor' 'film' 'blur' 'saturation' 'colorswap' 'washedout' 'posterise' 'colorpoint' 'colorbalance' 'cartoon' 'deinterlace1' 'deinterlace2'
        ###############################################################################
        self.camera=picamera.PiCamera()
        self.camera.sharpness = 0
        self.camera.contrast = 0
        self.camera.brightness = 50
        self.camera.saturation = 0
        self.camera.ISO = 0
        self.camera.video_stabilization = True
        self.camera.exposure_compensation = 0
        self.camera.exposure_mode = 'auto'
        self.camera.meter_mode = 'average'
        self.camera.awb_mode = 'auto'
        self.camera.image_effect = 'watercolor'
        self.camera.color_effects = None
        self.camera.rotation = 0
        self.camera.hflip = False
        self.camera.vflip = False
        self.camera.crop = (0.0, 0.0, 1.0, 1.0)
        #
        #self.camera.resolution = (640,480)
        #self.camera.framerate = 30
        #self.camera.annotate_text_size = 16
        #
        self.camera.resolution = (1296, 972)
        self.camera.framerate = 15
        self.camera.annotate_text_size = 32 
        #
        self.my_camera_led = True
        self.camera.led = True
        #self.camera.start_preview()
        self.camera.annotate_background = picamera.Color('black')
        self.camera.annotate_text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.my_start_camera()
        self.snapshottime = datetime.now().strftime('%Y-%m-%d:%H:%M')
        self.current_telemetry_text = "Welcome PiCamera"
        self.current_intext = "" 
        ###########################################
        # Start re-used code mavproxy_console.py
        ###########################################
        self.myTText_gps = ""
        self.myTText_heading = ""
        self.myTText_Roll = ""
        self.myTText_Pitch = ""
        self.myTText_Attitude="   |-----+-----|   "
        self.myTText_Radio = ""
        self.myTText_FlightTime = ""
        self.in_air = False
        self.start_time = 0.0
        self.total_time = 0.0
        self.all_total_time = 0.0
        ###########################################
        # End re-used code mavproxy_console.py
        ###########################################

    def my_write_log(self,level,msg):
        #OUTPUT FILE
        prefix = "Armed=%s State=%s Mode=%s NetUP=%s VideoON=%s MyRTL=%s Stabilize=%s Throttle=%s Volt=%s Current=%s Remaining=%s Altitude=%s" % (self.armed,self.mystatename[self.mystate],self.status.flightmode,self.net_up,self.video_on,self.rtl_on,self.stabilize_on,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining,self.status.altitude)
        date = datetime.now().strftime(self.FORMAT)
        if self.mydebug:
            print("%s %s %s %s" % (date,level,prefix,msg))
        if self.mylogverbose or level == "WARNING" or level == "ERROR":
            fo = open(self.settings.mylog, "a")
            fo.write("%s %s %s %s\n" % (date,level,prefix,msg))
            fo.close()

    def my_start_camera(self):
        #self.camera.start_recording(self.outpipe, format='h264', quality=23, bitrate=3000000, intra_period=60 , resize=(640, 480))
        self.camera.start_recording(self.outpipe, format='h264', quality=23, bitrate=3000000, intra_period=60)

    def my_telemetry_text(self):
        if (time.time() > self.last_TText_check_time + self.settings.mytimeTText):
            self.last_TText_check_time = time.time()
            ############################################
            # LED flashing
            ############################################
            if self.video_on == True:
                if self.my_camera_led == True:
                    self.camera.led = False
                    self.my_camera_led = False 
                else:
                    self.camera.led = True
                    self.my_camera_led = True
            ##################################################################################
            # overlay telemetry text with camera.annotate_text image 255 chars max
            ##################################################################################
            mytime = datetime.now().strftime('%H:%M:%S')
            if self.shutdown_by_lowbat == True or self.mystate == 5 or self.mystate == 6:
                color='red'
                level='E'
            elif self.shutdown_by_cmd == True or self.shutdown_by_radio == True:
                color='orange'
                level='S'
            elif self.reboot_by_cmd == True or self.reboot_by_radio == True:
                color='grey'
                level='R'
            elif self.armed == True:
                color='black'
                level='A'
            else:
                color='darkblue'
                level='_'
            intext = "{0:1} {1:8} {2:8} {3:8} {4:12} Vid{5:3}\nAsk={6:8} ({7}V,{8}A,{9}%) {10} {11} {12} GPSSpeed={13} Thr={14} {15} {16} ALt={17}m                                                  {18} ..........".format(level,["Disarmed","Armed"][self.armed == True],self.mystatename[self.mystate],self.status.flightmode,["Down",self.net_ip_current][self.net_up == True],["OFF","ON"][self.video_on == True],["RTL","STABILIZE"][self.stabilize_on == True],math.ceil(self.myvolt/100)/10,math.ceil(self.mycurrent)/100,self.myremaining,self.myTText_FlightTime,self.myTText_gps,self.myTText_heading,math.ceil(self.mygroundspeed*10)/10,self.mythrottle,self.myTText_Roll,self.myTText_Pitch,self.status.altitude,self.myTText_Attitude)
            if self.mydebug and self.current_intext != intext:
                self.current_intext = intext            
                print("%s %s" % (mytime,intext))
            myintext = "{0:8} {1}".format(mytime,intext)
            # max 255
            new_telemetry_text = (myintext[:254] + '!') if len(myintext) > 254 else myintext
            # new telemetry text
            if self.current_telemetry_text != new_telemetry_text:
               self.camera.annotate_background = picamera.Color(color)
               self.camera.annotate_text = "%s" % (new_telemetry_text)
               self.current_telemetry_text = new_telemetry_text
            ##################################
            # snapshot each minute
            ##################################
            if mytime != self.snapshottime:
                self.snapshottime = mytime
                mydate = datetime.now().strftime('%Y-%m-%d_%H:%M')
                jpgname=self.settings.myvideopath + "/Photo-Tarot-" + mydate + ".jpg"
                #print("jpgname=%s" % jpgname)
                self.camera.capture(jpgname, use_video_port=True)

    def my_network_status(self):
            p = subprocess.Popen(["/usr/local/bin/manage_network.sh","status",self.settings.myinterfaceadmin], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdoutData, stderrData) = p.communicate()
            rc = p.returncode
            if rc == 0:
                self.net_ip_current = stdoutData.rstrip()
                self.net_up = True
            else:
                self.net_ip_current = "null" 
                self.net_up = False 

    def my_video_status(self):
            self.video_on = False
            try:
               self.camera._check_recording_stopped()
            except:
               self.video_on = True

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
            # init var rtl_on and stabilize_on
            ####################################################
            self.my_mode_status()
            self.my_statustext_send("mode %s" % self.status.flightmode)
            ####################################################
            # init var net_ip
            ####################################################
            self.my_network_status()
            if self.net_up == True: self.my_statustext_send("%s up %s" % (self.settings.myinterfaceadmin,self.net_ip_current))
            else: self.my_statustext_send("%s down" % self.settings.myinterfaceadmin)
            ####################################################
            # video status
            ####################################################
            self.my_video_status()
            if self.video_on == True: self.my_statustext_send("VIDEO ON")
            else: self.my_statustext_send("VIDEO OFF")
            # to send statustext
            #print("self.settings.source_system=%s" % self.settings.source_system)

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
        if self.mydebug == False:
            print("INFO %s" % msg)
        msg = "cmd %s stderr %s" % (cmd,stderrData)
        self.my_write_log("INFO",msg)
        if self.mydebug == False:
            print("INFO %s" % msg)

    def mymode(self,mode):
        msg = "INFO request mode %s : current flightmode %s altitude %s" % (mode,self.status.flightmode,self.status.altitude)
        self.my_write_log("INFO",msg)
        if mode == "RTL" or mode == "STABILIZE":
          mode_mapping = self.master.mode_mapping()
          modenum = mode_mapping[mode]
          if mode == "RTL":
	    if self.status.flightmode != mode:
              self.rtl_on = False
              msg = "INFO request change mode to RTL modenum %s : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude)
              self.my_write_log("INFO",msg)
              self.mpstate.functions.process_stdin("mode RTL")
              ##self.master.set_mode(modenum)
            else:
              if self.rtl_on == False:
                  msg = "INFO change mode to RTL modenum %s already done : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude)
                  self.my_write_log("INFO",msg)
                  self.my_statustext_send("mode %s" % self.status.flightmode)
                  self.rtl_on = True
          if mode == "STABILIZE":
	    if self.status.flightmode != mode:
              self.stabilize_on = False
              msg = "INFO request change mode to STABILIZE modenum %s : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude)
              self.my_write_log("INFO",msg)
              self.mpstate.functions.process_stdin("mode STABILIZE")
              ##self.master.set_mode(modenum)
            else:
              if self.stabilize_on == False:
                  msg = "INFO change mode to RTL modenum %s already done : current flightmode %s altitude %s" % (modenum,self.status.flightmode,self.status.altitude)
                  self.my_write_log("INFO",msg)
                  self.my_statustext_send("mode %s" % self.status.flightmode)
                  self.stabilize_on = True
        else:
            msg = "WARNING mode %s not supported : current flightmode %s altitude %s" % (mode,self.status.flightmode,self.status.altitude)
            self.my_write_log("INFO",msg)
            self.my_statustext_send("mode %s not supported" % mode)

    def cmd_myrtl(self, args):
        self.mymode("RTL")

    def cmd_mystabilize(self, args):
        self.mymode("STABILIZE")

    def cmd_mybat(self, args):
        self.my_rc_check()
        self.my_network_status()
        self.my_video_status()
        self.my_mode_status()
        if self.mydebug:
           print("cmd_mybat %s" % self)
        self.my_network_status()
        msg = "LowVolt %s LowRemain %s" % (self.settings.myminvolt,self.settings.myminremain)
        self.my_write_log("INFO",msg)
        print ("Params : %s" % self.myparamcount)
        print ("MIN    : %s" % self.RC_MIN)
        print ("TRIM   : %s" % self.RC_TRIM)
        print ("MAX    : %s" % self.RC_MAX)
        print ("low    : %s" % self.RC_low_mark)
        print ("high   : %s" % self.RC_high_mark)
        if self.mydebug == False:
            prefix = "Armed=%s State=%s Mode=%s NetUP=%s VideoON=%s MyRTL=%s Stabilize=%s Throttle=%s Volt=%s Current=%s Remaining=%s" % (self.armed,self.mystatename[self.mystate],self.status.flightmode,self.net_up,self.video_on,self.rtl_on,self.stabilize_on,self.mythrottle,self.myvolt,self.mycurrent,self.myremaining)
            print ("INFO %s %s" % (prefix,msg))
        msg = "RC1:%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s" % (self.myrcraw[1],self.myrcraw[2],self.myrcraw[3],self.myrcraw[4],self.myrcraw[5],self.myrcraw[6],self.myrcraw[7],self.myrcraw[8])
        self.my_write_log("INFO",msg)
        print ("INFO %s" % (msg))
        # stats
        current_time = time.time()
        elapse_time = int(current_time - self.my_start_time) + 1
        rate_VFR_HUD = int(self.VFR_HUD / elapse_time)
        rate_GPS_RAW = int(self.GPS_RAW / elapse_time)
        rate_GPS_RAW_INT = int(self.GPS_RAW_INT / elapse_time)
        rate_ATTITUDE = int(self.ATTITUDE / elapse_time)
        rate_SYS_STATUS = int(self.SYS_STATUS / elapse_time)
        rate_HEARTBEAT = int(self.HEARTBEAT / elapse_time)
        rate_RC_CHANNELS_RAW = int(self.RC_CHANNELS_RAW / elapse_time)
        rate_RADIO = int(self.RADIO / elapse_time)
        rate_PARAM_VALUE = int(self.PARAM_VALUE / elapse_time)
        rate_STATUSTEXT = int(self.STATUSTEXT / elapse_time)
        rate_OTHER = int(self.OTHER / elapse_time)
        rate_battery_period_trigger = int(self.battery_period_trigger / elapse_time)
        msg = "INFO elapse_time %ssec rate_VFR_HUD %s=%s/sec rate_GPS_RAW %s=%s/sec rate_GPS_RAW_INT %s=%s/sec rate_ATTITUDE %s=%s/sec rate_SYS_STATUS %s=%s/sec rate_HEARTBEAT %s=%s/sec rate_RC_CHANNELS_RAW %s=%s/sec rate_RADIO %s=%s/sec rate_PARAM_VALUE %s=%s/sec rate_STATUSTEXT %s=%s/sec rate_OTHER %s=%s/sec rate_battery_period_trigger %s=%s/sec" % (elapse_time,self.VFR_HUD,rate_VFR_HUD,self.GPS_RAW,rate_GPS_RAW,self.GPS_RAW_INT,rate_GPS_RAW_INT,self.ATTITUDE,rate_ATTITUDE,self.SYS_STATUS,rate_SYS_STATUS,self.HEARTBEAT,rate_HEARTBEAT,self.RC_CHANNELS_RAW,rate_RC_CHANNELS_RAW,self.RADIO,rate_RADIO,self.PARAM_VALUE,rate_PARAM_VALUE,self.STATUSTEXT,rate_STATUSTEXT,self.OTHER,rate_OTHER,self.battery_period_trigger,rate_battery_period_trigger)
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
           if self.mydebug:
               msg = "RC1:%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s" % (self.myrcraw[1],self.myrcraw[2],self.myrcraw[3],self.myrcraw[4],self.myrcraw[5],self.myrcraw[6],self.myrcraw[7],self.myrcraw[8])
               self.my_write_log("INFO",msg)
           if self.myrcraw[self.settings.myrcnet] < self.RC_low_mark[self.settings.myrcnet] and self.myrcraw[self.settings.myrcnet] > (self.RC_low_mark[self.settings.myrcnet]-150):
               ''' MANAGE mode STABILIZE : RC8 LOW range RC_low_mark-150 to RC_low_mark '''
               self.my_mode_status()
               if self.stabilize_on == False:
                   if (self.stabilize_on_request == False or (self.stabilize_on == False and self.stabilize_on_request == True and (time.time() > self.stabilize_on_request_time + self.stabilize_on_request_retry))):
                       if self.stabilize_on_request == True: self.my_statustext_send("Mode STABILIZE retry")
                       self.stabilize_on_request = True
                       self.stabilize_on_request_time = time.time()
                       self.mymode("STABILIZE")
                       msg = "MyRC%sRaw %s LOW range RC_low_mark-150 to RC_low_mark : request on %s : current on %s" % (self.settings.myrcnet,self.myrcraw[self.settings.myrcnet],self.stabilize_on_request,self.stabilize_on)
                       self.my_write_log("INFO",msg)
               else:
                   if self.stabilize_on_prev != self.stabilize_on: self.my_statustext_send("Mode STABILIZE")
                   self.stabilize_on_prev = self.stabilize_on
           elif self.myrcraw[self.settings.myrcnet] > 0 and self.myrcraw[self.settings.myrcnet] < self.RC_low_mark[self.settings.myrcnet]:
               ''' MANAGE WLAN0 UP : RC8 LOW '''
               self.my_network_status()
               if self.net_up == True:
                   self.net_up_request = False
                   self.net_up = False
                   self.net_up_prev = self.net_up
                   self.net_ip_current = "null"
                   self.my_statustext_send("%s down" % self.settings.myinterfaceadmin)
                   self.my_subprocess(["/usr/local/bin/manage_network.sh","stop",self.settings.myinterfaceadmin])
               msg = "MyRC%sRaw %s LOW : request DOWN : interface %s is up : %s" % (self.settings.myrcnet,self.myrcraw[self.settings.myrcnet],self.settings.myinterfaceadmin,self.net_up)
               self.my_write_log("INFO",msg)
           elif self.myrcraw[self.settings.myrcnet] > self.RC_low_mark[self.settings.myrcnet] and self.myrcraw[self.settings.myrcnet] < self.RC_high_mark[self.settings.myrcnet]:
               ''' MANAGE WLAN0 DOWN : RC8 MIDDLE '''
               self.my_network_status()
               if self.net_up == True:
                   self.net_up_request = False
                   self.net_up = False
                   self.net_up_prev = self.net_up
                   self.net_ip_current = "null"
                   self.my_statustext_send("%s down" % self.settings.myinterfaceadmin)
                   self.my_subprocess(["/usr/local/bin/manage_network.sh","stop",self.settings.myinterfaceadmin])
               msg = "MyRC%sRaw %s MIDDLE : request DOWN : interface %s is up : %s" % (self.settings.myrcnet,self.myrcraw[self.settings.myrcnet],self.settings.myinterfaceadmin,self.net_up)
               self.my_write_log("INFO",msg)
           elif self.myrcraw[self.settings.myrcnet] > self.RC_high_mark[self.settings.myrcnet] and self.myrcraw[self.settings.myrcnet] < (self.RC_high_mark[self.settings.myrcnet]+150) :
               ''' MANAGE mode RTL : RC8 HIGH range RC_high_mark to RC_high_mark+150 '''
               self.my_mode_status()
               if self.rtl_on == False:
                   if (self.rtl_on_request == False or (self.rtl_on == False and self.rtl_on_request == True and (time.time() > self.rtl_on_request_time + self.rtl_on_request_retry))):
                       if self.rtl_on_request == True: self.my_statustext_send("Mode RTL retry")
                       self.rtl_on_request = True
                       self.rtl_on_request_time = time.time()
                       self.mymode("RTL")
                       msg = "MyRC%sRaw %s HIGH range RC_high_mark to RC_high_mark+150 : request on %s : current on %s" % (self.settings.myrcnet,self.myrcraw[self.settings.myrcnet],self.rtl_on_request,self.rtl_on)
                       self.my_write_log("INFO",msg)
               else:
                   if self.rtl_on_prev != self.rtl_on: self.my_statustext_send("Mode RTL")
                   self.rtl_on_prev = self.rtl_on
           elif self.myrcraw[self.settings.myrcnet] > self.RC_high_mark[self.settings.myrcnet]:
               ''' MANAGE WLAN0 UP : RC8 HIGH '''
               self.my_network_status()
               if self.net_up == False:
                   if (self.net_up_request == False or (self.net_up == False and self.net_up_request == True and (time.time() > self.net_up_request_time + self.net_up_request_retry))):
                       if self.net_up_request == True: self.my_statustext_send("Net up retry")
                       self.net_up_request = True
                       self.net_up_request_time = time.time()
                       self.my_subprocess(["/usr/local/bin/manage_network.sh","start",self.settings.myinterfaceadmin])
                       msg = "MyRC%sRaw %s HIGH : interface %s : request up %s : current up %s" % (self.settings.myrcnet,self.myrcraw[self.settings.myrcnet],self.settings.myinterfaceadmin,self.net_up_request,self.net_up)
                       self.my_write_log("INFO",msg)
               else:
                   if self.net_up_prev != self.net_up: self.my_statustext_send("%s up %s" % (self.settings.myinterfaceadmin,self.net_ip_current))
                   self.net_up_prev = self.net_up
               msg = "MyRC%sRaw %s LOW : interface %s : request up %s : current up %s" % (self.settings.myrcnet,self.myrcraw[self.settings.myrcnet],self.settings.myinterfaceadmin,self.net_up_request,self.net_up)
               self.my_write_log("INFO",msg)
           else:
               msg = "RC1:%s RC2:%s RC3:%s RC4:%s RC5:%s RC6:%s RC7:%s RC8:%s unknown RC value" % (self.myrcraw[1],self.myrcraw[2],self.myrcraw[3],self.myrcraw[4],self.myrcraw[5],self.myrcraw[6],self.myrcraw[7],self.myrcraw[8])
               self.my_write_log("WARNING",msg)
           ''' RC1 ROLL / RC2 PITCH / RC3 TROTTLE / RC4 YAW '''
           ''' MANAGE VIDEO OFF : RC6 HIGH '''
           if self.myrcraw[self.settings.myrcvideo] > self.RC_high_mark[self.settings.myrcvideo]:
               self.my_video_status()
               if self.video_on == True:
                   self.video_on = False
                   self.video_on_prev = self.video_on
                   self.video_on_request = False
                   msg = "MyRC%sraw %s HIGH : MyVideo on %s" % (self.settings.myrcvideo,self.myrcraw[self.settings.myrcvideo],self.video_on)
                   self.my_write_log("INFO",msg)
                   self.my_statustext_send("Video off")
                   self.camera.led = False
                   self.camera.wait_recording(2)
                   self.my_telemetry_text()
                   self.camera.wait_recording(1)
                   self.camera.stop_recording()
           ''' MANAGE VIDEO ON : RC6 LOW '''
           if self.myrcraw[self.settings.myrcvideo] > 0 and self.myrcraw[self.settings.myrcvideo] < self.RC_low_mark[self.settings.myrcvideo]:
               self.my_video_status()
               if self.video_on == False:
                   if (self.video_on_request == False or (self.video_on == False and self.video_on_request == True and (time.time() > self.video_on_request_time + self.video_on_request_retry))):
                       if self.video_on_request == True: self.my_statustext_send("Video ON retry")
                       self.video_on_request = True
                       self.video_on_request_time = time.time()
                       self.camera.led = True
                       self.my_start_camera()
                       msg = "MyRC%sRaw %s LOW : request up %s : current up %s" % (self.settings.myrcvideo,self.myrcraw[self.settings.myrcvideo],self.video_on_request,self.video_on)
                       self.my_write_log("INFO",msg)
               else:
                   if self.video_on_prev != self.video_on: self.my_statustext_send("Video ON")
                   self.video_on_prev = self.video_on
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

    #  VFR_HUD 7/sec GPS_RAW 0=0/sec GPS_RAW_INT 4/sec ATTITUDE 3/sec SYS_STATUS 7/sec HEARTBEAT 0/sec RC_CHANNELS_RAW 3/sec PARAM_VALUE 9/sec STATUSTEXT 0/sec OTHER 83/sec battery_period_trigger 0=0/sec
    def mavlink_packet(self, msg):
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
        mtype = msg.get_type()
        #print("System Status %s" % mtype)
        if mtype == "VFR_HUD":
            self.VFR_HUD += 1
            self.armed = self.master.motors_armed()
            self.mythrottle = msg.throttle
            self.mygroundspeed = msg.groundspeed
            if self.armed == True: self.mylogverbose = True
            else: self.mylogverbose = self.settings.mylogverbose
            self.mydebug = self.settings.mydebug
            self.my_telemetry_text()
            ###########################################
            # Start re-used code mavproxy_console.py
            ###########################################
            t = time.localtime(msg._timestamp)
            flying = False
            if self.mpstate.vehicle_type == 'copter':
                flying = self.master.motors_armed()
            else:
                flying = msg.groundspeed > 3
            if flying and not self.in_air:
                self.in_air = True
                self.start_time = time.mktime(t)
            elif flying and self.in_air:
                self.total_time = time.mktime(t) - self.start_time
                current_all_total_time = self.all_total_time + self.total_time
                self.myTText_FlightTime="FlightTime=%u:%02u/%u:%02u" % (int(self.total_time)/60, int(self.total_time)%60,int(current_all_total_time)/60, int(current_all_total_time)%60)
            elif not flying and self.in_air:
                self.in_air = False
                self.total_time = time.mktime(t) - self.start_time
                self.all_total_time = self.all_total_time + self.total_time
                self.myTText_FlightTime="FlightTime=%u:%02u/%u:%02u" % (int(self.total_time)/60, int(self.total_time)%60,int(self.all_total_time)/60, int(self.all_total_time)%60)
            else:
                self.myTText_FlightTime="FlightTime=%u:%02u/%u:%02u" % (int(self.total_time)/60, int(self.total_time)%60,int(self.all_total_time)/60, int(self.all_total_time)%60)
            ###########################################
            # End re-used code mavproxy_console.py
            ###########################################
        elif mtype == "SYS_STATUS":
            self.SYS_STATUS += 1
            self.myvolt = msg.voltage_battery
            self.mycurrent = msg.current_battery
            self.myremaining = msg.battery_remaining
            self.my_battery_check()
        ###########################################
        # Start re-used code mavproxy_console.py
        ###########################################
        elif mtype == 'ATTITUDE':
            self.ATTITUDE += 1
            Roll=math.degrees(msg.roll)
            Pitch=math.degrees(msg.pitch)
            self.myTText_Roll="Roll=%u" % Roll
            self.myTText_Pitch="Pitch=%u" % Pitch
            if Roll > 5 and Roll < 10:
                self.myTText_Attitude="   |```---+---___|%u" % Roll
            elif Roll > 10:
                self.myTText_Attitude="   |``````+______|%u" % Roll 
            elif Roll < -5 and Roll > -10:
                self.myTText_Attitude= "%u|___---+---```|   " % Roll 
            elif Roll < -10:
                self.myTText_Attitude= "%u|______+``````²|   " % Roll 
	    else:
                self.myTText_Attitude="   |------+------|   " % Roll 
        elif mtype in [ 'GPS_RAW', 'GPS_RAW_INT' ]:
            if mtype == "GPS_RAW":
                self.GPS_RAW += 1
                num_sats1 = self.master.field('GPS_STATUS', 'satellites_visible', 0)
            else:
                self.GPS_RAW_INT += 1
                num_sats1 = msg.satellites_visible
            num_sats2 = self.master.field('GPS2_RAW', 'satellites_visible', -1)
            if num_sats2 == -1:
                sats_string = "%u" % num_sats1
            else:
                sats_string = "%u/%u" % (num_sats1, num_sats2)
            if ((msg.fix_type >= 3 and self.master.mavlink10()) or
                (msg.fix_type == 2 and not self.master.mavlink10())):
                if (msg.fix_type >= 4):
                    fix_type = "%u" % msg.fix_type
                else:
                    fix_type = ""
                self.myTText_gps="GPS=OK%s(%s)" % (fix_type, sats_string)
            else:
                self.myTText_gps="GPS=%u(%s)!" % (msg.fix_type, sats_string)
            if self.master.mavlink10():
                gps_heading = int(self.mpstate.status.msgs['GPS_RAW_INT'].cog * 0.01)
            else:
                gps_heading = self.mpstate.status.msgs['GPS_RAW'].hdg
            self.myTText_heading="Hdg=%s/%u" % (self.master.field('VFR_HUD', 'heading', '-'), gps_heading)
        ###########################################
        # End re-used code mavproxy_console.py
        ###########################################
        elif mtype == "RC_CHANNELS_RAW":
            self.RC_CHANNELS_RAW += 1
            self.myrcraw[1] = msg.chan1_raw ; self.myrcraw[2] = msg.chan2_raw ; self.myrcraw[3] = msg.chan3_raw ; self.myrcraw[4] = msg.chan4_raw
            self.myrcraw[5] = msg.chan5_raw ; self.myrcraw[6] = msg.chan6_raw ; self.myrcraw[7] = msg.chan7_raw ; self.myrcraw[8] = msg.chan8_raw
            self.my_rc_check()
        elif mtype == "HEARTBEAT":
            self.HEARTBEAT += 1
            self.mystate = msg.system_status
            if (self.myinit == False and (time.time() > self.last_init_time + self.settings.myseqinit)):
                self.last_init_time = time.time()
                self.last_seq_time = time.time()
                self.my_init_var()
                self.net_up_prev = self.net_up
                self.video_on_prev = self.video_on
                self.rtl_on_prev = self.rtl_on
                self.stabilize_on_prev = self.stabilize_on
                ####################################################
                # reclaim params + version + frame type
                ####################################################
                self.master.param_fetch_all()
                msg = "INFO HEARTBEAT sequence %s : reclaim params and init var network, video, mode" % self.HEARTBEAT
                self.my_write_log("INFO",msg)
            if self.myinit == True:
                if (time.time() > self.last_seq_time + self.settings.myseqpoll):
                    self.last_seq_time = time.time()
                    self.my_network_status()
                    self.my_video_status()
                    self.my_mode_status()
                    msg = "INFO HEARTBEAT sequence %s : recheck status : network %s>%s, video %s>%s, mode RTL %s>%s, mode STABILIZE: %s>%s params: %s" % (self.HEARTBEAT,self.net_up_prev,self.net_up,self.video_on_prev,self.video_on,self.rtl_on_prev,self.rtl_on,self.stabilize_on_prev,self.stabilize_on,self.myparamcount)
                    self.my_write_log("INFO",msg)
                    if self.net_up != self.net_up_prev:
                        if self.net_up == True: self.my_statustext_send("%s up. %s" % (self.settings.myinterfaceadmin,self.net_ip_current))
                        else: self.my_statustext_send("%s down." % self.settings.myinterfaceadmin)
                        self.net_up_prev = self.net_up
                    if self.video_on != self.video_on_prev:
                        if self.video_on == True: self.my_statustext_send("Video on.")
                        else: self.my_statustext_send("Video off.")
                        self.video_on_prev = self.video_on
                    if self.rtl_on != self.rtl_on_prev:
                        if self.rtl_on == True: self.my_statustext_send("Mode RTL.")
                        self.rtl_on_prev = self.rtl_on
                    if self.stabilize_on != self.stabilize_on_prev:
                        self.stabilize_on_prev = self.stabilize_on
                        if self.stabilize_on == True: self.my_statustext_send("Mode STABILIZE.")
                    if self.myparamcount != self.myparamcount_prev:
                        self.myparamcount_prev = self.myparamcount
                        self.my_statustext_send("%s params" % self.myparamcount)
                    if self.mydebug:
                        print ("MIN  : %s" % self.RC_MIN)
                        print ("TRIM : %s" % self.RC_TRIM)
                        print ("MAX  : %s" % self.RC_MAX)
                        print ("low  : %s" % self.RC_low_mark)
                        print ("high : %s" % self.RC_high_mark)
        ###########################################
        # Start re-used code mavproxy_console.py
        ###########################################
        elif mtype in ['RADIO', 'RADIO_STATUS']:
            self.RADIO += 1
            #if msg.rssi < msg.noise+10 or msg.remrssi < msg.remnoise+10:
            #    self.myTText_Radio="Radio %u/%u %u/%u" % (msg.rssi, msg.noise, msg.remrssi, msg.remnoise)
            #else:
            #    self.myTText_Radio="Radio %u/%u %u/%u!" % (msg.rssi, msg.noise, msg.remrssi, msg.remnoise)
            #self.myTText_Radio="Radio=%u" % (msg.rssi)
        ###########################################
        # End re-used code mavproxy_console.py
        ###########################################
        elif mtype == "STATUSTEXT":
            self.STATUSTEXT += 1
            self.myseverity = msg.severity
            self.mytext = msg.text
            self.my_statustext_check()
        elif mtype == "PARAM_VALUE":
            self.PARAM_VALUE += 1
            #print("PARAM_VALUE %s %s" % (msg.param_id,msg.param_value))
            self.myparamcount = msg.param_count
            for i in range(1,17):
                if (msg.param_id == "RC%s_TRIM" % i): self.RC_TRIM[i] = msg.param_value
                if (msg.param_id == "RC%s_MIN" % i):  self.RC_MIN[i] = msg.param_value
                if (msg.param_id == "RC%s_MAX" % i):  self.RC_MAX[i] = msg.param_value
                self.RC_low_mark[i] = ((self.RC_TRIM[i] - self.RC_MIN[i]) // 2) + self.RC_MIN[i]
                self.RC_high_mark[i] = self.RC_MAX[i] - ((self.RC_MAX[i] - self.RC_TRIM[i]) // 2)
        else:
            ######################################
            # AHRS
            # AHRS2
            # AHRS3
            # EKF_STATUS_REPORT
            # GLOBAL_POSITION_INT
            # HWSTATUS
            # MEMINFO
            # MISSION_CURRENT
            # MOUNT_STATUS
            # NAV_CONTROLLER_OUTPUT
            # POWER_STATUS
            # RAW_IMU
            # SCALED_PRESSURE
            # SENSOR_OFFSETS
            # SERVO_OUTPUT_RAW
            # SYSTEM_TIME
            # VIBRATION
            ######################################
            self.OTHER += 1
           # print("OTHER type %s" % mtype)
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

