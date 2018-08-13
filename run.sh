#!/bin/bash

if ! docker network ls | grep pedagogic_ctf >/dev/null ; then
    echo " [*] Creating dedicated Docker network"
    sudo docker network create pedagogic_ctf
fi

if docker ps -a | grep selenium >/dev/null ; then
    echo " [*] Stopping running Selenium Docker instance ..."
    docker stop selenium >/dev/null
    docker rm selenium >/dev/null
fi

echo " [*] Starting Selenium Docker"
docker run --name=selenium --network=pedagogic_ctf -d --restart=unless-stopped -t pedagogictf/selenium

echo " [*] Generating challenges secrets"
for chall_name in `ls challs|grep dir|sed "s/.dir$//"`
do
    rand=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    echo " [*] Initialize ${chall_name} challenge"
    cd challs/${chall_name}.dir/
    echo -n ${rand} > secret
    python3 init.py ${rand}
    cd -
done


echo " [*] Running API ..."
./main
