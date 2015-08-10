#!/bin/bash -x

#source $1

NODES="invalid"
SCRIPTDIR="invalid"
CONF="invalid"
USER="invalid"

program=$(basename $0)

usage () { # {{{
    cat <<-EOF
Usage: $program -n NODES -l scriptdir -c config.ini
	-u USER
	-n NODES - planetlab nodes to include
	-l scriptdir - directory where updatedb.py is located
	-c configuration file 
EOF
    exit 1
}
# }}}


while getopts "u:n:l:c:h" opt $* ; do # {{{
case $opt in
u)  USER=$OPTARG ;;
n)  NODES=$OPTARG ;;
l)  SCRIPTDIR=$OPTARG ;;
c)  CONF=$OPTARG ;;
*)  usage
esac
done # }}}

if [ $USER == "invalid" ]; then echo "USER file empty or does not exist"; exit 1; fi
if [[ $NODES == "invalid" ]]; then echo "NODES file empty or does not exist"; exit 1; fi
if [[ $SCRIPTDIR == "invalid" ]]; then echo "SCRIPTDIR file empty or does not exist"; exit 1;fi
if [[ $CONF == "invalid" ]]; then echo "CONF file empty or does not exist"; exit 1; fi


cat $NODES | grep -v n\/a | awk '{print $1}' >  $NODES.vps

parallel-ssh -o out -e err -x "-o StrictHostKeyChecking=no -i $KEY" -O UserKnownHostsFile=/dev/null -O StrictHostKeyChecking=no -O PasswordAuthentication=no -h $NODES.vps -l $USER "traceroute -n -m 1 143.225.229.127" > $NODES.vps.out1

cat $NODES.vps.out1 | grep SUCCESS | awk '{print $4}' > $NODES.vps.success

$SCRIPTDIR/updatedb.py $CONF $NODES.vps.success $NODES

