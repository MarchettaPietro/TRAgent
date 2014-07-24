#!/bin/bash -x

source $1

cat $NODES | grep -v n\/a | awk '{print $1}' >  $NODES.vps

parallel-ssh -o out -e err -x "-o StrictHostKeyChecking=no -i $KEY"  -h $NODES.vps -l $USER "traceroute -n -m 1 143.225.229.127" | grep SUCCESS | awk '{print $4}' > $NODES.vps.success
#$LDIR/updatedb.py $DB $NODES.vps.success $NODES
$LDIR/updatedb.py $1 $NODES.vps.success $NODES

