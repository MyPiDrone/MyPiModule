#!/bin/sh
################################################
#### wwww.MyPiDrone.com
################################################

# dongle 1 atheros
#WLAN="wlan1"
WLAN="wlx60e3270f04fd"
# other wlan0 or eth0
#WLAN_INTERNET="wlan0"
#WLAN_INTERNET="eth0"
WLAN_INTERNET="enp3s0"
service NetworkManager stop
ifconfig $WLAN down
/sbin/ifconfig $WLAN up 10.0.0.1 netmask 255.255.255.0
#Enable NAT
iptables --flush
iptables --table nat --flush
iptables --delete-chain
iptables --table nat --delete-chain
iptables --table nat --append POSTROUTING --out-interface $WLAN_INTERNET -j MASQUERADE
iptables --append FORWARD --in-interface $WLAN -j ACCEPT
#Enable routage ON
sysctl -w net.ipv4.ip_forward=1
iptables -L -t nat
#
service dnsmasq stop
service dnsmasq start
#service hostapd start
# debug
sed -i -e"s/^interface=.*/interface=$WLAN/"  /etc/hostapd/hostapd.conf
grep "^interface" /etc/hostapd/hostapd.conf
service hostapd stop
killall hostapd
iwconfig $WLAN
ip a
/usr/local/bin/hostapd -d -K /etc/hostapd/hostapd.conf
### restart once if exit failed
sleep 1
/usr/local/bin/hostapd -d -K /etc/hostapd/hostapd.conf
#

