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
            'params': ['odtokjupfpenmtyo'],
            'response': 'here is the encrypted text',
            'message': 'Encryption API is broken. Expecting to find: "here is the encrypted text" in the response\n\n'
                       'Your code output: \n\n{}',
        },
        {
            'params': [''],
            'response': 'here is the encrypted text',
            'message': 'Encryption API is broken. Without user input, return example found in secret.\n '
                       'Expecting to find: "here is the encrypted text" in the response\n\n'
                       'Your code output: \n\n{}',
        },
        {
            'params': ['tooshort'],
            'response': 'encryption problem!',
            'message': 'Encryption API is broken. Expecting : "Encryption problem!"\n\n'
                       'Your code output: \n\n{}',
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

    return True


def main():

    secret = sys.argv[1]
    correction_file = sys.argv[2]
    return_code = 0 if check(correction_file, secret) else 2
    sys.exit(return_code)


if __name__ == "__main__":
    main()
