#!/bin/bash

userdel ctf_interne
groupdel ctf_interne
useradd ctf_interne
mkdir /home/ctf_interne && chown ctf_interne:ctf_interne /home/ctf_interne -R
rm -rf /srv/ctf_go && mkdir /srv/ctf_go

# Install Go
wget --quiet "https://storage.googleapis.com/golang/go1.8.linux-amd64.tar.gz"
tar -xf go1.8.linux-amd64.tar.gz
mv go /usr/local
export GOPATH=`pwd`
export PATH=$PATH:/usr/local/go/bin:${GOPATH}/bin
echo "Fetching golang requirements.."
go get ctf/main

cp . -R /srv/ctf_go
rm -rf /srv/writable && mkdir /srv/writable && chmod 733 /srv/writable
chmod 733 /tmp
cp /srv/ctf_go/src/ctf/utils/config.json.example /srv/ctf_go/src/ctf/utils/config.json
touch /srv/ctf_go/database.db
chown ctf_interne /srv/ctf_go -R
chmod o-rwx /srv/ctf_go -R
chmod o+rx /srv/ctf_go/
chmod o+rx /srv/ctf_go/challs/
chown :www-data /srv/ctf_go/frontend-angular/ -R

# Build app that wrap and execute user's code
gcc /srv/ctf_go/sandbox.c -o /srv/ctf_go/sandbox
chown root:ctf_interne /srv/ctf_go/sandbox
chmod 4750 /srv/ctf_go/sandbox
chown root:root /srv/ctf_go/sandbox.py
chmod 500 /srv/ctf_go/sandbox.py

# Init challenges
for chall_name in `ls challs|grep dir|sed "s/.dir$//"`
do
    userdel $chall_name
    groupdel $chall_name
    printf "thesecret" > /srv/ctf_go/challs/${chall_name}.dir/secret
    (cd /srv/ctf_go/ && ./load_challenges.py $chall_name)
done

# Selenium based challs specific
# TODO: add to init challenges
cd /usr/local/bin
wget --quiet "https://github.com/mozilla/geckodriver/releases/download/v0.15.0/geckodriver-v0.15.0-linux64.tar.gz"
tar xvzf geckodriver-v0.15.0-linux64.tar.gz
chmod +x geckodriver

chown root:stored_xss /srv/ctf_go/challs/stored_xss.dir/victim_browser.py
chmod +x /srv/ctf_go/challs/stored_xss.dir/victim_browser.py
touch /tmp/api.log
chmod 666 /tmp/api.log

touch /srv/ctf_go/challs/data_exposure.dir/key
chown root:data_exposure /srv/ctf_go/challs/data_exposure.dir/key


chown ctf_interne /srv/ctf_go/challenges.json

rm -Rf /pedagogic_ctf

# configure nginx
cp /srv/ctf_go/nginx.conf /etc/nginx/sites-available/pedagogictf
ln -s /etc/nginx/sites-available/pedagogictf /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
service nginx restart

echo
echo "Check src/ctf/utils/config.json !"
