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

    if ret != 0:
        print("Invalid execution : {}".format(out))
        sys.exit(1)

    return out.decode(), ret


def raw_run(args):

    child = subprocess.Popen(args, stdout=subprocess.PIPE)
    out = child.communicate()[0]
    ret = child.returncode
    return out.decode(), ret


def clean_output(string_from_dig):
    array_from_dig = string_from_dig.split('\n')
    new_array = set()
    for line in array_from_dig:
        if line != "" and not line.startswith(';'):
            new_array.add(line)
    return new_array


def check(correction_file, secret):

    out_ref, ret_ref = raw_run(["/usr/bin/dig", "+short", "www.ovh.com"])
    out_bin, ret_bin = run_cmd(correction_file, ["www.ovh.com"])
    # should output the same thing
    out_ref_set = clean_output(out_ref)
    out_bin_set = clean_output(out_bin)
    if out_ref_set != out_bin_set:
        print("Output of `./yourcode_compiled www.ovh.com` different from `/usr/bin/dig +short www.ovh.com`")
        print("\n\nYour code outputs : \n" + out_bin + "\n\nAnd `dig` outputs : \n" + out_ref)
        return False

    out_ref, ret_ref = raw_run(["/usr/bin/dig", "+short", "8.8.8.8"])
    out_bin, ret_bin = run_cmd(correction_file, ["8.8.8.8"])
    # should output the same thing
    out_ref_set = clean_output(out_ref)
    out_bin_set = clean_output(out_bin)
    if out_ref_set != out_bin_set:
        print("Output of `./yourcode_compiled 8.8.8.8` different from `/usr/bin/dig +short 8.8.8.8`")
        print("\n\nYour code outputs : \n" + out_bin + "\n\nAnd `dig` outputs : \n" + out_ref)
        return False

    out, ret = run_cmd(correction_file, ["test with w!erds charac|eres"])
    if out != "Error, server param not valid.\n":
        print(
            "Output of `./yourcode_compiled \"test with w!erds charac|eres\"` should be :\n\"Error, server param not "
            "valid.\"\n\nBut the output is :\n\"" + out + "\"")
        return False

    out, ret = run_cmd(correction_file, [])
    if out != "Please send me a server address so I can dig it ! (ex: google.com or www.ovh.com)\n":
        print(
            "Output of `./yourcode_compiled` should be :\n\"Please send me a server address so I can dig it ! (ex: "
            "google.com or www.ovh.com)\"\n\nBut the output is :\n\"" + out + "\"")
        return False

    return True


def main():

    secret = sys.argv[1]
    correction_file = sys.argv[2]
    return_code = 0 if check(correction_file, secret) else 2
    sys.exit(return_code)


if __name__ == "__main__":
    main()
