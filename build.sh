#!/bin/sh
#########################################################
#### www.MyPiDrone.com
#########################################################
date=`date`
MYDIR="/home/kevin/MAVProxy-1.4.40"
cd $MYDIR
#git clone  https://github.com/MyPiDrone/MyPiModule
vi MAVProxy/modules/mavproxy_MyPiModule.py
python setup.py build install
[ $? -ne 0 ] && exit 1
cp MAVProxy/modules/mavproxy_MyPiModule.py MyPiModule/
cp /usr/local/bin/StartArduCopter-quad.sh MyPiModule/
cp /home/kevin/fpv/TESTS/start_tx_with_video_recording_broadcast_over_ap.sh MyPiModule/
cp /home/kevin/fpv/start_tx_with_video_recording.sh MyPiModule/
cp /etc/rc.local MyPiModule/
cd MyPiModule
VERSION=`grep "self.myversion" mavproxy_MyPiModule.py|head -n 1|awk -F'"' '{print "v"$2}'`
echo "mavproxy_MyPiModule.py VERSION=$VERSION"
LIST="build.sh mavproxy_MyPiModule.py StartArduCopter-quad.sh start_tx_with_video_recording.sh start_tx_with_video_recording_broadcast_over_ap.sh start_rx.sh start_ap.sh rc.local README.md"
git add $LIST
git commit $LIST -m "$VERSION $date"
#git commit StartArduCopter-quad.sh -m "$date"
#git commit start_tx_with_video_recording.sh -m "$date"
#git commit start_tx_with_video_recording_broadcast_over_ap.sh -m "$date"
#git commit start_rx.sh -m "$date"
#git commit start_ap.sh -m "$date"
#git commit rc.local -m "$date"
#git commit build.sh -m "$date"
#git commit README.md -m "$date"
#git pull
git push
cd $MYDIR
C=`ps -ef |grep -v grep |grep -c /usr/local/bin/mavproxy.py`
if [ $C -ne 0 ]; then
        echo "kill /usr/local/bin/mavproxy.py"
        ps -ef |grep -v grep |grep /usr/local/bin/mavproxy.py
        ps -ef |grep -v grep |grep /usr/local/bin/mavproxy.py|awk '{print $2}'|xargs kill
fi
echo "/usr/bin/python /usr/local/bin/mavproxy.py --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule' --show-errors"
### load only MyPiModule
/usr/bin/python /usr/local/bin/mavproxy.py --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --default-modules='MyPiModule,mode' --show-errors
### load all modules
#/usr/bin/python /usr/local/bin/mavproxy.py --master=udp:127.0.0.1:14550 --quadcopter --out=/dev/ttyUSB0,57600  --show-errors

