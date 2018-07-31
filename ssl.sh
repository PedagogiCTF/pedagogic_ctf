#!/usr/bin/env bash
echo "Please create a 'ssl' directory in the current dir and add the certificate and the key: pedagogictf.crt and pedagogictf.key)"
echo "For example:"
echo "mkdir ssl && cd ssl && openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout pedagogictf.key -out pedagogictf.crt"
echo "Then run:"
echo "docker run --rm -v $(pwd)/ssl/:/src -v frontend-ssl:/data debian bash -c 'cp -r /src/. /data/ && chmod 600 /data/*'"
