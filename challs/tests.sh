#!/bin/bash

extensions=( ".py" ".pl" ".go" )

for chall_name in `ls |grep dir|sed "s/.dir$//"`
do
    sudo userdel $chall_name 
    sudo useradd $chall_name
    rand=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    echo " [*] Testing $chall_name challenge"
    
    #### INIT ####
    cd ${chall_name}.dir
    python3 init.py "" $rand $USER
    status=$?
    if [ $status -ne 0 ]
    then
        printf "\033[0;31m [!] Failed to init $chall_name\033[0m\n"
        cd ..
        continue
    fi
    echo -n $rand > secret
    
    #### CHECK & EXPLOIT ####
    allGood=true
    for ext in "${extensions[@]}"
    do
        if [ -f $chall_name$ext ]
        then
            python3 check.py $chall_name$ext $rand $USER
            status=$?
            if [ $status -ne 0 ]
            then
                printf "\033[0;31m [!] Failed to check $chall_name$ext\033[0m\n"
                allGood=false
                continue
            fi
        fi
        if [ -f $chall_name$ext ]
        then
            python3 exploit.py $chall_name$ext $rand $USER > /dev/null
            status=$?
            if [ $status -ne 3 ]
            then
                printf "\033[0;31m [!] Failed to exploit $chall_name$ext\033[0m\n"
                allGood=false
                continue
            fi
        fi
    done
    if $allGood; then printf "\033[0;32m [+] All good for $chall_name\033[0m\n"; fi
    cd ..
done
