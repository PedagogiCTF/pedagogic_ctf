#!/bin/bash

prog=$1
  
if [ -z $1 ]; then
  echo "you must provide a file"
  exit 1
fi

if [ ! -f $1 ]; then
  echo "file does not exist"
  exit 1
fi

export PATH=$PATH:/usr/lib/go-1.7/bin/

extension="${prog##*.}"
case "$extension" in
  "go")
    go run $prog
    ;;
  "pl")
    perl $prog
    ;;
  "py")
    python3 $prog
    ;;
  "sh")
    /bin/bash $prog
    ;;
  *)
    echo "invalid language"
    exit 1
    ;;
esac
