#!/usr/bin/python3
from random import choice
from string import ascii_lowercase


def init_key():
    with open('key', "w") as _file:
        _file.write(''.join(choice(ascii_lowercase) for _ in range(16)))


if __name__ == "__main__":
    init_key()
