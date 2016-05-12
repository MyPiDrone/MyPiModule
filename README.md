###########################################################################################
#TITLE# DRONE MyPiDrone Project Kev&Phil : Copter QUAD Project 1 and Project 2
- Project 1 : TAROT 650 Copter QUAD with Raspberry PI2 & Navio+ controler
- Project 2 : TAROT 280 Copter QUAD with Raspberry PI3 & Navio2 controler
- raspian Kernel 4.4.y 
- www.MyPiDrone.com MyPiDrone kev&phil Project
- https://github.com/MyPiDrone/MyPiModule 
- Version 2.0 : May 1 2016 
- https://github.com/MyPiDrone/MyPiModule/blob/master/mavproxy_MyPiModule.py
- README here: https://github.com/MyPiDrone/MyPiModule/blob/master/README.md
###########################################################################################

 Changelog :

      version 2.1 :

        - add myrtl function to set RTL mode (Return To Launch)
        - add mystabilize function to set STABILIZE mode
        - set RTL mode when RC8 range HIGH_MARK to HIGH_MARK+100
        - set STABILIZE mode when RC8 range LOW_MARK-100 to LOW_MARK
        - support raspian Kernel 4.4.y emlid img for RIP2/RPI3 NAVIO+/NAVIO2

###########################################################################################

        - build.sh                                            DRONE : to install MyPiModule
        - mavproxy_MyPiModule.py                              DRONE : module MAVProxy
        - rc.local                                            DRONE : exec StartArduCopter-quad.sh
        - ArduCopter-quad.service                             DRONE : systemd call /usr/local/bin/start_ArduCopter-quad.sh
        - myvideo.service                                     DRONE : systemd call /usr/local/bin/start_video.sh /usr/local/bin/stop_video.sh
        - mavproxy.service                                    DRONE : systemd call /usr/local/bin/start_MAVProxy_MyPiModule.sh
        - wifiap.service                                      GCS   : systemd call /usr/local/bin/start_MAVProxy_MyPiModule.sh
        - start_video.sh                                      DRONE : fork /usr/local/bin/start_tx_with_video_recording.sh
        - stop_video.sh                                       DRONE : kill raspivid and tx
        - start_tx_with_video_recording.sh                    DRONE : start Video Wifibroadcast
        - start_tx_with_video_recording_broadcast_over_ap.sh  DRONE : start Video Broadcast over Wifi AP : Beta test
        - start_ap.sh                                         GCS   : start Wifi AP on GCS
        - start_rx.sh                                         GCS   : view Video on GCS
        - start_rx_and_broadcast_over_ap.sh                   GCS   : rx and streamin video over AP to Android QtGStreamerHUD emlid
        - hostapd.conf                                        GCS   : Wifi Access Point configuration
        - dsnmasq.conf                                        GCS   : dsnmasq configuration
        - show_modules.sh                                     DRONE : tools show params modules

###########################################################################################


The Raspberry PI2 consumes between 1A and 2A according to the WiFi is enabled or not and MAVproxy module (MyPiModule) 
will therefore help preserve the battery and control various functions of RPI2 (AP Wifi, Video Wifibroadcast, shutdown, reboot)
 from the radio (Taranis x9d opentx in our project)

The main functions of MyPiModule (MAVProxy module):

* my_battery_check function:

    - Preserve the minimum battery voltage if the drone is in STANDBY mode and if the engines are not armed.
      Under these conditions with a weak battery module executes the stop Raspberry PI 2 (init 0)

* my_rc_check function:

    - Run a shutdown of RPI2 from the radio:
        - Conditions: STANDBY + DISARMED
        - On the radio: LOW YAW (RC4) and ROLL HIGH (RC1)
    - Perform a reboot of RPI2 from the radio:
        - Conditions: STANDBY + DISARMED
        - On the radio: LOW YAW (RC4) and ROLL LOW (RC1)
    - enable / disable the wireless network from the radio wlan0:
        - RC8 LOW : wlan0 DOWN and SINGLE MODE OFF
        - RC8 range LOW_MARK-100 to LOW_MARK : set mode STABILIZE *NEW*
        - RC8 MIDDLE : SINGLE MODE ON
        - RC8 range HIGH_MARK to HIGH_MARK+100 : set mode RTL
        - RC8 HIGH : ifup wlan0 
    - enable / disable the video on wifibroadcast wlan1 from the radio:
        - RC6 LOW (also used to tilt the camera left): Video wifibroadcast ON
        - RC6 HIGH (also used to tilt the camera to right): Video wifibroadcast OFF

==> Logs: /var/log/mavproxy_MyPiModule.log


* Parameters for functions and telemetry:
  (Change in /.mavinit.scr or /root/.mavinit.scr if necessary).

    - mydelayinit: : 30 seconds delay to reboot or shutdown to allow cancel.
    - myminremain : 10% (low battery remaining mark).
    - myminvolt : 10V (battery low voltage mark).
    - mytimebat : 5sec interval data mesurement of the battery voltage.
    - mytimerc : 5sec interval data mesurement of the radio channels.
    - myrcvideo : channel to control video on / off, default 6.
    - myrcwlan0 : channel to control the AP wifi on / off, default 8.
    - myrcyaw and myrcroll : the two channels to control the shutdown or reboot, default 4 and 1.

* Console mode functions:

    - mybat       : battery status
    - myshut      : execute a shutdown (to cancel shutdown execute a new request in time delay of 30 secondes)
    - myreboot    : execute a reboot (to cancel reboot execute a new request in time delay of 30 secondes)
    - myrtl       : set RTL mode *NEW*
    - mystabilize : set STABILIZE mode *NEW*

    Shutdown and reboot may be canceled : execute a new command before delay (30sec) to do that .

    The STATUSTEXT progress message is displayed on the screen 2 on the telemetry radio.

    A YAW MAX 3 seconds (ARMED) also cancels all requests for shutdown or reboot in progress.

* Here the module test procedure:

    -1- Install MAVproxy with git clone https://github.com/Dronecode/MAVProxy.git
    
    -2- Create your MAVProxy Module/modules/mavproxy_MyPiModule.py module available here: git clone https://github.com/MyPiDrone/MyPiModule
    
    -3- Execute python setup.py build install
    
    -4- Execute ArduPilot:
      /usr/bin/ArduCopter-quad -A /dev/ttyAMA0 -C udp:127.0.0.1:14550
      
    -5- Execute MAVProxy (in console mode remove --deamon) /usr/local/bin/mavproxy.py –master=udp:127.0.0.1:14550 –quadcopter –out=/dev/ttyUSB0,57600 –default-modules=’MyPiModule’ –daemon

     You can also load the module when MAVProxy is already started with the command module load MyPiModule or module reload MyPiModule
     You can add this self-loading in file /.mavinit.scr or /root/.mavinit.scr by adding the line module load MyPiModule
     MAVproxy load ten modules and --default-modules='MyPiModule' option allows load only the list of desired modules (comma separator) to consume less CPU on RPI2 and therefore less battery.

    ==> Observe the behavior in the log file: tail -f /var/log/mavproxy_MyPiModule.log


*** the end ***

