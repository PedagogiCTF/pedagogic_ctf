#!/usr/bin/python3

import os
import random
import string
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

    if ret != 0:
        print("Invalid execution : {}".format(out))
        sys.exit(1)

    return out.decode(), ret


def check(correction_file, secret):

    directory = "/tmp/injection_conf/inject_conf_" + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
    folder_configured_path = os.path.join(directory, "folder_configured")
    out, ret = run_cmd(correction_file, [directory])
    if ret != 0 or not os.path.isdir(directory) or not os.path.isfile(folder_configured_path):
        print("Your code should have created a directory with an init file \"folder_configured in it\". But it appears it failed to do it. Here is the output of your code : " + out)
        return False

    directory = "/home/whatever"
    out, ret = run_cmd(correction_file, [directory])
    if ret != 0 or out != "Error, directory param not valid.\n":
        print("Output is wrong. The output of your code is : " + out + "\nAnd it should be : \"Error, directory param not valid.\"")
        return False

    directory = "/tmp/injection_conf/&ls"
    out, ret = run_cmd(correction_file, [directory])
    if ret != 0 or out != "Error, directory param not valid.\n":
        print("Output is wrong. The output of your code is : " + out + "\nAnd it should be : \"Error, directory param not valid.\"")
        return False

    out, ret = run_cmd(correction_file, [])
    if ret != 0 or out != "Please send me a directory path so I can launch my configuration script !\n":
        print("Output of `./youcode_compiled` should be :\n\"Please send me a directory path so I can launch my configuration script !\"\n\nBut the output is :\n\"" + out + "\"")
        return False

    return True


def main():

    correction_file = sys.argv[1]
    secret = sys.argv[2]
    return_code = 0 if check(correction_file, secret) else 2
    sys.exit(return_code)


if __name__ == "__main__":
    main()
