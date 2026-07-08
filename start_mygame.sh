#!/bin/bash
cd /opt/bigworld/my_game/res/server
export BW_RES_PATH=/opt/bigworld/my_game/res:/opt/bigworld/2.1/server/res
export LD_LIBRARY_PATH=/opt/bigworld/2.1/server/bigworld/bin/Hybrid64
BIN=/opt/bigworld/2.1/server/bigworld/bin/Hybrid64

pkill -9 -f 'server/bigworld/bin/Hybrid64' 2>/dev/null
pkill -9 -x bwmachined2 2>/dev/null
pkill -9 -x socat 2>/dev/null
sleep 3

iptables -F 2>/dev/null
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -s 192.168.56.1 -p udp --dport 20013 -j ACCEPT
iptables -A INPUT -s 192.168.56.1 -p udp --dport 20015 -j ACCEPT
iptables -A INPUT -s 192.168.56.1 -p udp -j DROP
echo "iptables OK"

nohup /opt/bigworld/2.1/bwmachined/sbin/bwmachined2 > /dev/null 2>&1 &
sleep 3; echo "bwmachined OK"

nohup $BIN/dbmgr --daemon --uid 6001 > /tmp/mg_dbmgr.log 2>&1 &
echo "dbmgr starting..."
sleep 15
pidof dbmgr > /dev/null && echo "dbmgr OK" || { echo "dbmgr FAILED"; tail -5 /tmp/mg_dbmgr.log; exit 1; }

nohup $BIN/baseappmgr --daemon --uid 6001 > /tmp/mg_bam.log 2>&1 &
sleep 3; echo "baseappmgr OK"

nohup $BIN/cellappmgr --daemon --uid 6001 > /tmp/mg_cam.log 2>&1 &
sleep 3; echo "cellappmgr OK"

nohup $BIN/loginapp --daemon --uid 6001 > /tmp/mg_login.log 2>&1 &
sleep 5; echo "loginapp OK"

nohup $BIN/baseapp --daemon --uid 6001 > /tmp/mg_baseapp.log 2>&1 &
sleep 5; echo "baseapp OK"

nohup $BIN/cellapp --daemon --uid 6001 > /tmp/mg_cellapp.log 2>&1 &
sleep 5; echo "cellapp OK"

echo "=== PROCESSES ==="
for p in bwmachined2 dbmgr baseappmgr cellappmgr loginapp baseapp cellapp; do
  pid=$(pidof $p 2>/dev/null)
  if [ -n "$pid" ]; then echo "$p OK pid=$pid"; else echo "$p MISSING"; fi
done

echo "=== NETWORK ==="
ss -ulnp | grep -E '192.168|20013|20015'

echo "=== DONE ==="
