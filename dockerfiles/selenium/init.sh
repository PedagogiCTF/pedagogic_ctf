#!/bin/bash

cd /usr/local/bin
wget "https://github.com/mozilla/geckodriver/releases/download/v0.15.0/geckodriver-v0.15.0-linux64.tar.gz"
tar xvzf geckodriver-v0.15.0-linux64.tar.gz
chmod +x geckodriver
