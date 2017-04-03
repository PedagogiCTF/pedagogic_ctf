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

echo " [*] Installing dependencies"
sudo apt-get update && sudo apt-get install --fix-missing -y build-essential python3 golang-1.7 perl libauthen-passphrase-perl libmojolicious-perl libdigest-sha-perl libdbi-perl libdbd-sqlite3-perl libhtml-scrubber-perl libhtml-defang-perl libcrypt-cbc-perl libstring-random-perl python3-pip python3-lxml openssl dnsutils libxml2-dev libxslt1-dev npm > /dev/null &
spinner $!
sudo cpan MIK/CryptX-0.044.tar.gz
echo " [*] Installing Python dependencies"
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip3 install -r requirements.txt > /dev/null &
spinner $! 

echo " [*] Building Go API"
sudo groupadd docker
sudo gpasswd -a ${USER} docker
go build src/ctf/main/main.go &
spinner $! 

rm challenges.json
echo "[]" > challenges.json
for chall_name in `ls challs|grep dir|sed "s/.dir$//"`
do
    cat challs/${chall_name}.dir/${chall_name}.json | python -c "import json, sys; chall = json.loads(''.join([line for line in sys.stdin])); chall['challenge_id']=sys.argv[1]; f=open('challenges.json', 'r'); challs=json.loads(f.read()); challs.append(chall); f.close(); f=open('challenges.json', 'w');f.write(json.dumps(challs));f.close()" $chall_name
done

echo " [*] Building AngularJS app"
sudo ln -s /usr/bin/nodejs /usr/bin/node
sudo npm install -g bower
cd frontend-angular && bower install --allow-root

cd ../dockerfiles
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
