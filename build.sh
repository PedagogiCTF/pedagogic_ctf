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

echo " [*] Building Go API"
go build src/ctf/main/main.go &
spinner $! 

cd dockerfiles
for dir in */ ; do
    cd $dir
    image=`echo $dir|sed "s/\///"`
    echo " [*] Building $image Docker image"
    sudo docker build -q . -t $image >/dev/null &
    spinner $! 
    cd ..
done

if ! sudo docker network ls | grep pedagogic_ctf >/dev/null ; then
    echo " [*] Creating dedicated Docker network"
    sudo docker network create pedagogic_ctf
fi
