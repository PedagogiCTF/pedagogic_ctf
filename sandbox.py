#!/usr/bin/python3

import importlib.machinery
import os
import pwd
import random
import shutil
import string
import sys

from base64 import b64decode
from subprocess import STDOUT, CalledProcessError, check_output, TimeoutExpired

SUPPORTED_EXTENSIONS = ['.py', '.go', '.pl', '.php']


def run_cmd(cmd_list, timeout=7):
    """
        Exec a command on the system
    """
    try:
        output = check_output(cmd_list, stderr=STDOUT, timeout=timeout)
        return output.decode(), 0
    except CalledProcessError as ex:
        return ex.output.decode(), ex.returncode
    except TimeoutExpired:
        return "Command timeout", 1
    except Exception:
        return "Unknown exception", 1


def random_string(size):
    """
        Return a random string of length `size`
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))


def get_sandbox_user(chall_name, recursive_count=0):
    """
        Returns a random non-existing user
    """
    if recursive_count > 10:
        raise OSError("Can't find a free username..")
    user = chall_name[-9:] + "_" + random_string(10)
    try:
        pwd.getpwnam(user)
        return get_sandbox_user(chall_name, recursive_count + 1)
    except:
        return user


def check_args(chall_name, extension):
    """
        Check script args compliance
    """
    if extension not in SUPPORTED_EXTENSIONS:
        print("Extension not supported : " + extension)
        sys.exit(1)

    challenge_path = os.path.join(os.path.sep, 'srv', 'ctf_go', 'challs', chall_name + '.dir')
    if not os.path.isdir(challenge_path):
        print("Directory does not exists : " + challenge_path)
        sys.exit(1)


def init_sandbox(language_extension, challenge_name, sandbox_dir):

    # create unique user
    sandbox_user = get_sandbox_user(challenge_name)
    output, return_code = run_cmd(['useradd', sandbox_user])
    if return_code != 0:
        print("An error occured while adding user '" + sandbox_user + "' : " + str(output))
        sys.exit(1)

    # compile challenge
    script_path = os.path.join(sandbox_dir, challenge_name + language_extension)
    script_path_compiled = os.path.join(sandbox_dir, challenge_name)
    if language_extension == ".pl":
        # we just need to create a symbolic link
        os.symlink(script_path, script_path_compiled)
    elif language_extension == ".py":
        # we just need to create a symbolic link
        os.symlink(script_path, script_path_compiled)
    elif language_extension == ".go":
        output, return_code = run_cmd(["/usr/bin/go", "build", "-o", script_path_compiled, script_path])
        if return_code != 0:
            print("An error occured while building go file : " + str(output))
            sys.exit(1)

    # change wrapper
    wrapper_path = os.path.join(sandbox_dir, 'wrapper.c')
    with open(wrapper_path) as wrapper_handler:
        wrapper = wrapper_handler.read()
    wrapper = wrapper.replace('CHALLENGE', script_path_compiled)
    wrapper = wrapper.replace('THE_USER', sandbox_user)
    with open(wrapper_path, "w") as wrapper_handler:
        wrapper_handler.write(wrapper)
    # compile wrapper
    wrapper_bin_path = os.path.join(sandbox_dir, 'wrapper')
    output, return_code = run_cmd(['/usr/bin/gcc', "-o", wrapper_bin_path, wrapper_path])
    if return_code != 0:
        print("An error occured while compiling wrapper : " + str(output))
        sys.exit(1)
    os.remove(wrapper_path)

    # chown / chmod
    output, return_code = run_cmd(['/bin/chown', sandbox_user + ":" + sandbox_user, sandbox_dir, '-R'])
    if return_code != 0:
        print("An error occured while chowning : " + str(output))
        sys.exit(1)
    output, return_code = run_cmd(['/bin/chown', "root:" + sandbox_user, wrapper_bin_path])
    if return_code != 0:
        print("An error occured while chowning : " + str(output))
        sys.exit(1)
    output, return_code = run_cmd(['/bin/chmod', "500", script_path_compiled])
    if return_code != 0:
        print("An error occured while chmoding : " + str(output))
        sys.exit(1)
    output, return_code = run_cmd(['/bin/chmod', "4750", wrapper_bin_path])
    if return_code != 0:
        print("An error occured while chmoding : " + str(output))
        sys.exit(1)

    return sandbox_user


# TODO: Use docker
def create_sandbox(content, chall_name, extension, interpret_only=False):
    """
        Create a pseudo sandbox to execute user's submitted code
    """
    sandbox_dir = "/srv/writable/" + chall_name + "_" + random_string(30) + "/"
    os.makedirs(sandbox_dir)

    sandbox_file = sandbox_dir + chall_name + extension
    with open(sandbox_file, 'wb') as _file:
        _file.write(content)

    base_challs_path = os.path.join(os.path.sep, 'srv', 'ctf_go', 'challs')
    challenge_path = os.path.join(base_challs_path, chall_name + '.dir')

    shutil.copy(os.path.join(base_challs_path, "wrapper.c"), sandbox_dir)

    if not interpret_only:
        shutil.copy(os.path.join(challenge_path, "init.py"), sandbox_dir)
        shutil.copy(os.path.join(challenge_path, "exploit.py"), sandbox_dir)
        shutil.copy(os.path.join(challenge_path, "check.py"), sandbox_dir)

    return sandbox_dir


def delete_sandbox(sandbox_user, sandbox_dir):
    """
        Delete sandbox directory and sandbox user
    """
    shutil.rmtree(sandbox_dir)
    output, return_code = run_cmd(['userdel', sandbox_user])
    if return_code != 0:
        print("An error occured while removing user '{}' : {}".format(
            sandbox_user,
            output)
        )
        sys.exit(1)


def init_corrected_challenge(sandbox_dir, sandbox_user, random_secret,
                             challenge_name, extension):

    init = importlib.machinery.SourceFileLoader(
        'init',
        os.path.join(sandbox_dir, "init.py")
    ).load_module()
    init.init(sandbox_dir, random_secret, challenge_name + extension)
    run_cmd(['/bin/chown', sandbox_user + ":" + sandbox_user, sandbox_dir, '-R'])


def exploit_corrected_challenge(sandbox_dir, random_secret):

    binary = os.path.join(sandbox_dir, "wrapper")
    exploit = importlib.machinery.SourceFileLoader(
        'exploit',
        os.path.join(sandbox_dir, "exploit.py")
    ).load_module()
    return exploit.exploit(binary, random_secret)


def check_corrected_challenge(sandbox_dir, random_secret):

    binary = os.path.join(sandbox_dir, "wrapper")
    check = importlib.machinery.SourceFileLoader(
        'check',
        os.path.join(sandbox_dir, "check.py")
    ).load_module()
    return check.check(binary, random_secret)


def main():

    # TODO: use argparse

    return_code = 0

    sandboxed_content = b64decode(sys.argv[1])
    challenge_name = sys.argv[2]
    language_extension = sys.argv[3]
    interpret_only = len(sys.argv) == 5  # Playground mode

    check_args(challenge_name, language_extension)

    sandbox_dir = create_sandbox(
        sandboxed_content,
        challenge_name,
        language_extension,
        interpret_only=interpret_only
    )

    sandbox_user = init_sandbox(
        language_extension,
        challenge_name,
        sandbox_dir,
    )

    os.chdir(sandbox_dir)

    if interpret_only:
        binary = os.path.join(sandbox_dir, "wrapper")
        output, _ = run_cmd((binary))
        try:
            print(output)
        except:
            print(output.encode('utf-8'))
    else:
        random_secret = random_string(30)
        init_corrected_challenge(
            sandbox_dir,
            sandbox_user,
            random_secret,
            challenge_name,
            language_extension
        )
        can_use = check_corrected_challenge(sandbox_dir, random_secret)
        if not can_use:
            print("You broke a functionnality in the code ! So your fix is not accepted.\n")
            return_code = 1
        if can_use:
            can_exploit = exploit_corrected_challenge(sandbox_dir, random_secret)
            if can_exploit:
                print("I can still exploit your code ;)")
                return_code = 1

    delete_sandbox(sandbox_user, sandbox_dir)
    sys.exit(return_code)


if __name__ == "__main__":

    main()
