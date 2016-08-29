#!/usr/bin/python3
import sys, os
import re
import random, string

## check params
if len(sys.argv) != 2 or !sys.argv[1]:
    print("Please send me a directory path so I can launch my configuration script !")
    sys.exit(0)
directory = sys.argv[1]
regex_dir = r"[a-zA-Z0-9_\/-]+"
regex_dir_compiled = re.compile(regex_dir)
if not directory or not regex_dir_compiled.match(directory):
    print("Error, directory param not valid.")
    sys.exit(0)
if os.path.isdir(directory):
    print("Directory already exists.")
    sys.exit(0)
## end check params

## write configuration file
file_name = "/srv/writable/";
file_name += ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
file_name += "_config.sh"
with open(file_name, "w") as fh:
    fh.write("DATE=`date`\n")
    fh.write("DIRECTORY=" + directory + "\n")
## end write configuration file

## call configuration
command = ". " + file_name + " && ";
command += 'mkdir "${DIRECTORY}" && ';
command += 'echo ${DATE} > "${DIRECTORY}/folder_configured"';
os.system(command)
## end call configuration

if os.path.isdir(directory):
    print("Directory configured.")
else:
    print("Failed to configure directory.")
