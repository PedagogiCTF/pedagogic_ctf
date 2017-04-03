#!/usr/bin/python3

import sys


def init_secrets(secret):

    with open('secret', "w") as _file:
        _file.write(secret)

    with open('key', "w") as _file:
        _file.write(secret)


def main():

    secret = sys.argv[2]
    init_secrets(secret)


if __name__ == "__main__":
    main()
