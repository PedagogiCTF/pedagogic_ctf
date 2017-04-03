#!/usr/bin/python3

import os
import sys


def init_directory():

    directory = '/tmp/injection_conf'
    if not os.path.exists(directory):
        os.makedirs(directory)


def init_secret(secret):

    with open('secret', "w") as _file:
        _file.write(secret)


def main():

    secret = sys.argv[2]
    init_directory()
    init_secret(secret)


if __name__ == "__main__":
    main()
