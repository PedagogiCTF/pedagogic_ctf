#!/bin/bash

prog=$1

rm /entrypoint.sh
rm /requirements.txt

if [ -z $1 ]; then
  echo "you must provide a file"
  exit 1
fi

echo "127.0.0.1 $(hostname)" >> /etc/hosts

chgrp code /code
chmod 0775 /code
cd /home/code
sudo -u code /bin/bash /run-code.sh $prog
