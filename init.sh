#!/bin/bash

spinner()
{
    local pid=$1
    local delay=0.5
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c] " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

if sudo docker ps | grep selenium | grep Up >/dev/null ; then
    echo " [*] Stopping running Selenium Docker instance ..."
    sudo docker stop selenium >/dev/null &
    spinner $!
    sudo docker rm selenium >/dev/null
fi

echo " [*] Starting Selenium Docker"
sudo docker run --name=selenium --network=pedagogic_ctf -p 127.0.0.1:6379:6379 -p 127.0.0.1:8888:8888 -d -t selenium >/dev/null

for chall_name in `ls challs|grep dir|sed "s/.dir$//"`
do
    sudo userdel $chall_name
    sudo useradd $chall_name
    rand=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    echo " [*] Initialize $chall_name challenge"
    python3 challs/${chall_name}.dir/init.py "" $rand $USER
    echo -n $rand > challs/${chall_name}.dir/secret
done
