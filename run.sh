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
sudo docker run --name=selenium --network=pedagogic_ctf -p 6379:6379 -p 8888:8888 -d -t selenium >/dev/null
echo " [*] Running API ..."
./main
