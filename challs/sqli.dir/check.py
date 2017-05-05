#!/usr/bin/python3

import subprocess
import sys

from hashlib import sha256


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


def check(correction_file, secret):
    """
        Check if the corrected source code is still usable
    """
    debug_hash = sha256(secret.encode('utf-8')).hexdigest()

    checks = [
        {
            'params': ['a', 'a'],
            'response': 'invalid username/password',
            'message': 'Login seems broken. Your code output \n\n{}',
        },
        {
            'params': [debug_hash, debug_hash],
            'response': secret.lower(),
            'message': 'Valid credentials does not work anymore. Your code output \n\n{}',
        }
    ]

    for _check in checks:

        out, return_code = run_cmd(correction_file, _check['params'])
        if return_code != 0:
            print("Invalid execution : {}".format(out))
            sys.exit(1)

        if _check['response'] not in out.lower():
            print(_check['message'].format(out))
            return False

    return True


def main():

    correction_file = sys.argv[1]
    secret = sys.argv[2]
    return_code = 0 if check(correction_file, secret) else 2
    sys.exit(return_code)


if __name__ == "__main__":
    main()
