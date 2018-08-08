#!/usr/bin/python3

import subprocess
import sys


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
    out = child.communicate()[0]
    ret = child.returncode
    return out.decode(), ret


def check(correction_file, secret):
    """
        Check if the corrected source code is still usable
    """
    checks = [
        {
            'params': ['debug-e9bc7d25d163', 'e9bc7d25d16348f9c5f6b9251c270c0da39aff8b', '/aze'],
            'response': 'not found',
            'message': 'Calling invalid endpoint does not return "not found". Your code output \n\n{}',
        },
        {
            'params': ['debug-e9bc7d25d163', 'e9bc7d25d16348f9c5f6b9251c270c0da39aff8b', '/me'],
            'response': 'debug-e9bc7d25d163',
            'message': 'Calling /me does not return my user. Your code output \n\n{}',
        },
        {
            'params': ['debug-e9bc7d25d163', 'e9bc7d25d16348f9c5f6b9251c270c0da39aff8b', '/get-secret'],
            'response': 'you are not allowed to request',
            'message': '/get-secret endpoint seems unavailable or broken. Your code output \n\n{}',
        },
    ]

    for _check in checks:

        out, return_code = run_cmd(correction_file, _check['params'])
        if return_code != 0:
            print("Invalid execution : {}".format(out))
            sys.exit(1)
        if _check['response'] not in out.lower():
            print(_check['message'].format(out))
            return False

    checks = [
        {
            'params': ['', '', '/get-secret'],
            'response': ('missing or invalid token', 'debug: username list'),
            'message': 'User check seems broken.\n\n Your code output \n\n{}',
        },
        {
            'params': ['test', 'test', '/get-secret'],
            'response': ('invalid x-api-token', 'debug: token list'),
            'message': 'Token check seems broken.\n\n Your code output \n\n{}',
        }
    ]

    for _check in checks:

        out, return_code = run_cmd(correction_file, _check['params'])
        if return_code != 0:
            print("Invalid execution : {}".format(out))
            sys.exit(1)
        if not any(r in out.lower() for r in _check['response']):
            print(_check['message'].format(out))
            return False

    return True


def main():

    secret = sys.argv[1]
    correction_file = sys.argv[2]
    return_code = 0 if check(correction_file, secret) else 2
    sys.exit(return_code)


if __name__ == "__main__":
    main()
