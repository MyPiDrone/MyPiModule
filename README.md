# MyPiModule

http://www.MyPiDrone.com

MAVProxy MyPiModule for MyPiDrone

########################################################################################################
- build.sh                                            : to install MyPiModule
- mavproxy_MyPiModule.py                              : module MAVProxy
- rc.local                                            : exec StartArduCopter-quad.sh
- StartArduCopter-quad.sh                             : manage ArduCopter-quad and Video Wifibroadcast
- start_tx_with_video_recording.sh                    : start Video Wifibroadcast
- start_tx_with_video_recording_broadcast_over_ap.sh  : start Video Broadcast over Wifi AP : Beta test
- start_ap.sh                                         : start Wifi AP on GCS
- start_tx.sh                                         : view Video on GCS
########################################################################################################


The Raspberry PI2 consumes between 1A and 2A according to the WiFi is enabled or not and MAVproxy module (MyPiModule) will therefore help preserve the battery and control various functions of RPI2 (AP Wifi, Video Wifibroadcast, shutdown, reboot etc.) from the radio (Taranis x9d opentx in our project)

The main functions of MyPiModule (MAVProxy module):

my_battery_check function:

    Preserve the minimum battery voltage if the drone is in STANDBY mode and if the engines are not armed. Under these conditions with a weak battery module executes the stop Raspberry PI 2 (init 0)

my_rc_check function:

    Run a shutdown of RPI2 from the radio:
        Conditions: STANDBY + DISARMED
        On the radio: LOW YAW (RC4) and ROLL HIGH (RC1)
    Perform a reboot of RPI2 from the radio:
        Conditions: STANDBY + DISARMED
        On the radio: LOW YAW (RC4) and ROLL LOW (RC1)
    enable / disable the wireless network from the radio wlan0:
        RC8 LOW (the low level is also used in flight for SINGLE MODE OFF) or RC8 MIDDLE (the neutral is also used in flight for SINGLE MODE ON): ifdown wlan0
        RC8 HIGH: ifup wlan0
    enable / disable the video on wifibroadcast wlan1 from the radio:
        RC6 LOW (also used to tilt the camera left): Video wifibroadcast ON
        RC6 HIGH (also used to tilt the camera to right): Video wifibroadcast OFF

Logs: /var/log/mavproxy_MyPiModule.log


Parameters for functions and telemetry:
(Change in /.mavinit.scr or /root/.mavinit.scr if necessary).

    mydelayinit: : 30 seconds delay to reboot or shutdown to allow cancel.
    myminremain : 10% (low battery remaining mark).
    myminvolt : 10V (battery low voltage mark).
    mytimebat : 5sec interval data mesurement of the battery voltage.
    mytimerc : 5sec interval data mesurement of the radio channels.
    myrcvideo : channel to control video on / off, default 6.
    myrcwlan0 : channel to control the AP wifi on / off, default 8.
    myrcyaw and myrcroll : the two channels to control the shutdown or reboot, default 4 and 1.

Console mode functions:

    mybat : battery status
    myshut : execute a shutdown (to cancel shutdown execute a new request in time delay of 30 secondes)
    myreboot : execute a reboot (to cancel reboot execute a new request in time delay of 30 secondes)

Shutdown and reboot may be canceled : execute a new command before delay (30sec) to do that .

The STATUSTEXT progress message is displayed on the screen 2 on the telemetry radio.

A YAW MAX 3 seconds (ARMED) also cancels all requests for shutdown or reboot in progress.

Here the module test procedure:

    Install MAVproxy with git clone https://github.com/Dronecode/MAVProxy.git
    Create your MAVProxy Module/modules/mavproxy_MyPiModule.py module available here: git clone https://github.com/MyPiDrone/MyPiModule
    Execute python setup.py build install
    Execute ArduPilot:
    /usr/bin/ArduCopter-quad -A /dev/ttyAMA0 -C udp:127.0.0.1:14550
    Execute MAVProxy (in console mode remove --deamon) /usr/local/bin/mavproxy.py –master=udp:127.0.0.1:14550 –quadcopter –out=/dev/ttyUSB0,57600 –default-modules=’MyPiModule’ –daemon
    You can also load the module when MAVProxy is already started with the command module load MyPiModule or module reload MyPiModule

You can add this self-loading in file /.mavinit.scr or /root/.mavinit.scr by adding the line module load MyPiModule

MAVproxy load ten modules and --default-modules='MyPiModule' option allows load only the list of desired modules (comma separator) to consume less CPU on RPI2 and therefore less battery.

    Observe the behavior in the log file: tail -f /var/log/mavproxy_MyPiModule.log

example :

2016-02-27 08:41:19 INFO Armed: False MyState: 3 Mythrottle 0 MyVolt 11617 MyCurrent 150 MyRemaining 97 MyRC2Raw 0 MyRC3Raw 0 : Reboot ByRadio
2016-02-27 08:41:19 INFO Armed: False MyState: 3 Mythrottle 0 MyVolt 11617 MyCurrent 150 MyRemaining 97 Reboot ByRadio after 30sec
2016-02-27 08:41:19 INFO Armed: False MyState: 3 Mythrottle 0 MyVolt 11617 MyCurrent 150 MyRemaining 97 MySeverity 1 MyStatusText Reboot ByRadio after 30sec at 08h41m19s
2016-02-27 08:41:20 INFO Armed: False MyState: 3 Mythrottle 0 MyVolt 11617 MyCurrent 150 MyRemaining 97 MySeverity 6 MyStatusText SIMPLE mode on
2016-02-27 08:41:23 INFO Armed: False MyState: 3 Mythrottle 0 MyVolt 11574 MyCurrent 164 MyRemaining 97 LowVolt >10000 or LowRemain >10 : Good status
2016-02-27 08:41:24 INFO Armed: False MyState: 3 Mythrottle 0 MyVolt 11579 MyCurrent 147 MyRemaining 97 ifup wlan0 RPI2
2016-02-27 08:41:24 INFO Armed: False MyState: 3 Mythrottle 0 MyVolt 11579 MyCurrent 147 MyRemaining 97 cmd ['ifup', 'wlan0'] sdtout
2016-02-27 08:41:24 INFO Armed: False MyState: 3 Mythrottle 0 MyVolt 11579 MyCurrent 147 MyRemaining 97 cmd ['ifup', 'wlan0'] stderr ifup: interface wlan0 already configured


*** the end ***

