#!/usr/bin/python3

import sys

from random import choice
from string import ascii_lowercase


def init_secrets(secret):
    with open('secret', "w") as _file:
        _file.write(secret)

    with open('key', "w") as _file:
        _file.write(''.join(choice(ascii_lowercase) for i in range(16)))


def main():
    secret = sys.argv[1]
    init_secrets(secret)


if __name__ == "__main__":
    main()
