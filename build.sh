date=`date`
MYDIR="/home/kevin/MAVProxy-1.4.40"
cd $MYDIR
#git clone  https://github.com/MyPiDrone/MyPiModule
#cp MyPiModule/mavproxy_MyPiModule.py MAVProxy/modules/
vi MAVProxy/modules/mavproxy_MyPiModule.py
python setup.py build install
[ $? -ne 0 ] && exit 1
cp MAVProxy/modules/mavproxy_MyPiModule.py MyPiModule
cd MyPiModule
git add build.sh mavproxy_MyPiModule.py
git commit mavproxy_MyPiModule.py -m "$date"
git commit build.sh -m "$date"
git commit README.md -m "$date"
git push
cd $MYDIR
