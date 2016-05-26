#!/bin/sh
#TITLE# DRONE manage wlan0 called by MyPiModule
#
WLAN=$2
[ "_$WLAN" = "_" ] && WLAN="wlan0"
case "$1" in
  start)
        nohup ifup $WLAN >/var/log/stop_network.log 2>&1 &
        echo "ifup $WLAN"
        ;;
  stop)
        #nohup ifdown $WLAN >/var/log/start_network.log 2>&1 &
        echo "ifdown $WLAN"
        ;;
  status)
        IP=`ip a|grep "inet"|grep "$WLAN"|awk '{print $2}'|awk -F'/' '{print $1}'`
        if [ "_$IP" = "_" ]; then
                echo "$WLAN is down"
                exit 1
        else
                echo "$IP"
                exit 1
        fi
        ;;
  *)
        echo "Usage: $0 {start|stop|status} wlan_name"
	echo "       default wlan_name = wlan0"
        exit 1
esac

exit 0

