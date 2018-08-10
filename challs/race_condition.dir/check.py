#!/usr/bin/python3

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


def random_string(size):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))


def check(correction_file, secret):

    out, return_code = run_cmd(correction_file, ["login", secret, secret])
    if "You are logged in. And congratz ! Here is the secret : " + secret + "\n" not in out:
        print(
            "Output is wrong when the admin tries to log in. The output of your code is : "
            + out
            + "\nAnd it should contain : \"You are logged in. And congratz ! Here is the secret : " + secret + "\"")
        return False
    user = random_string(20)
    password = random_string(20)
    out_reg, return_code_reg = run_cmd(correction_file, ["register", user, password])
    if "You are registered !\n" not in out_reg:
        print(
            "Output is wrong when a regular user tries to register. The output of your code is : "
            + out
            + "\nAnd it should contain : \"You are registered !\"")
        return False
    out_log, return_code_log = run_cmd(correction_file, ["login", user, password])
    if "You are logged in. But sorry you are not allowed to see the secret.\n" not in out_log:
        print(
            "Output is wrong when a regular user tries to log in. The output of your code is : " + out + "\nAnd it should contain : \"You are logged in. But sorry you are not allowed to see the secret.\"")
        return False

    out_fake_log, return_code_fake_log = run_cmd(correction_file, ["login", "reallyrandom", "reallyrandom"])
    if "We failed to log you in :/\n" != out_fake_log:
        print(
            "Output is wrong when a user fail to log in. The output of your code is : " + out + "\nAnd it should contain : \"We failed to log you in :/\"")
        return False

    out, ret = run_cmd(correction_file, [])
    if "Please send me an 'action' (register or login) with your credentials (login, then password)\n" not in out:
        print(
            "Output of `./youcode_compiled` should be :\n\"Please send me an 'action' (register or login) with your credentials (login, then password)\"\n\nBut the output is :\n\"" + out + "\"")
        return False

    return True


def main():
    secret = sys.argv[1]
    correction_file = sys.argv[2]
    return_code = 0 if check(correction_file, secret) else 2
    sys.exit(return_code)


if __name__ == "__main__":
    main()
