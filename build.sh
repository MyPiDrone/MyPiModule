date=`date`
cd /root/MAVProxy
#git clone  https://github.com/MyPiDrone/MyPiModule
#cp MyPiModule/mavproxy_MyPiModule.py MAVProxy/modules/
vi MAVProxy/modules/mavproxy_MyPiModule.py
python setup.py build install
[ $? -ne 0 ] && exit 1
cp MAVProxy/modules/mavproxy_MyPiModule.py /root/MAVProxy/MyPiModule
cd /root/MAVProxy/MyPiModule
git config --global user.email "philippe.le-coq@laposte.net"
git config --global user.email "philippelecoq"
git add build.sh mavproxy_MyPiModule.py
git commit mavproxy_MyPiModule.py -m "$date"
git commit build.sh -m "$date"
git commit README.md -m "$date"
git push
cd /root/MAVProxy
