#!/usr/bin/python3
import base64
import random
import sqlite3
import subprocess
import sys

from base64 import b64encode
from string import ascii_letters, digits
from urllib.parse import quote

import requests

SELENIUM_HOST = "selenium.pedagogic_ctf"
PORT = 8888


def run_cmd(correction_file, args):

    args.insert(0, correction_file)

    if correction_file.endswith('.py'):
        args.insert(0, 'python3')
    elif correction_file.endswith('.pl'):
        args.insert(0, 'perl')
    elif correction_file.endswith('.go'):
        args.insert(0, 'run')
        args.insert(0, 'go')

    child = subprocess.Popen(args, stdout=subprocess.PIPE)
    streamdata = child.communicate()[0]
    ret = child.returncode
    return streamdata.decode(), ret


def check(correction_file):
    """
        Check if the corrected source code is still usable
    """
    user = ''.join(random.SystemRandom().choice(ascii_letters + digits) for _ in range(32))

    out, return_code = run_cmd(correction_file, [user, 'test'])
    if return_code != 0:
        print("Invalid execution : {}".format(out))
        sys.exit(1)

    if not all(k in out.lower() for k in ('running', 'base64', 'img', '8888')):
        print("Unable to validate victim_browser.py output: {}".format(out))
        return False

    try:
        response = out.split("For debugging purposes: ")[-1].split(" ")[0]
        response = base64.b64decode(response.encode()).decode()
    except Exception:
        print("The expected HTML was not found in response")
        return False

    if '<tr><td>{}</td><td>test</td></tr>'.format(user) not in response:
        print("POST comments seems broken, unable to find test comment in {}".format(response))
        return False

    return True


def main():
    correction_file = sys.argv[2]

    return_code = 0 if check(correction_file) else 2
    sys.exit(return_code)


if __name__ == "__main__":
    main()
