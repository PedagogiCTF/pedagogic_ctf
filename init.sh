#!/bin/bash

if sudo docker ps -a | grep selenium >/dev/null ; then
    echo " [*] Stopping running Selenium Docker instance ..."
    sudo docker stop selenium >/dev/null
    sudo docker rm selenium >/dev/null
fi

echo " [*] Starting Selenium Docker"
sudo docker run --name=selenium --network=pedagogic_ctf -p 127.0.0.1:6379:6379 -p 127.0.0.1:8888:8888 -d -t selenium >/dev/null

for chall_name in `ls challs|grep dir|sed "s/.dir$//"`
do
    if [ -d "/tmp/$chall_name" ]; then
        rm -Rf /tmp/$chall_name
    fi
    rand=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    echo " [*] Initialize $chall_name challenge"
    cd challs/${chall_name}.dir/
    python3 init.py "" $rand $USER
    mkdir /tmp/$chall_name
    if [ -f "/tmp/${chall_name}.db" ]; then
        mv /tmp/${chall_name}.db /tmp/$chall_name/${chall_name}.db
    fi
    cd ../../
done
