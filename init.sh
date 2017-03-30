#!/bin/bash

for chall_name in `ls challs|grep dir|sed "s/.dir$//"`
do
    sudo userdel $chall_name
    sudo useradd $chall_name
    rand=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    echo " [*] Initialize $chall_name challenge"
    python3 challs/${chall_name}.dir/init.py "" $rand $USER
    echo -n $rand > challs/${chall_name}.dir/secret
done
