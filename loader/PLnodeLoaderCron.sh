#!/bin/bash -x

source $1

cat $NODES | grep -v n\/a | awk '{print $1}' >  $NODES.vps
parallel-ssh -h $NODES.vps -l $USER "traceroute -n -m 5 143.225.229.127" | grep SUCCESS | awk '{print $3}' > $NODES.vps.success
$LDIR/updatedb.py $DB $NODES.vps.success $NODES

