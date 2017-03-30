#!/bin/bash

user=$1
correction=$2

files=( "init.py" "check.py" "exploit.py" )

rm /entrypoint.sh
rm /requirements.txt

echo "127.0.0.1 $(hostname)" >> /etc/hosts
echo "127.0.0.1 evil.com" >> /etc/hosts
echo "127.0.0.1 my-site.com" >> /etc/hosts

tc qdisc add dev eth0 root tbf rate 10kbps latency 50ms burst 2500

rand=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

chgrp code /code
chmod 0775 /code
cd /code
    
for i in "${files[@]}"
do
    output=$(sudo -u code /usr/bin/python3 $i $correction $rand $user)
    status=$?
    if [ $status -ne 0 ]
    then
        echo $output
        exit $status
    fi
done
