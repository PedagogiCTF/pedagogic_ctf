#!/usr/bin/python3

import sys


def init_secret(secret):
    with open('secret', "w") as _file:
        _file.write(secret)


def main():
    secret = sys.argv[1]
    init_secret(secret)


if __name__ == "__main__":
    main()
