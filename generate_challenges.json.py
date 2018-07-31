#!/usr/bin/env python3
import json
import glob
import os

challs = []
for chall_dir in glob.glob("challs/*.dir"):
    chall_name = chall_dir.split("/")[1].split(".dir")[0]
    with open(os.path.join(chall_dir, chall_name + ".json")) as f:
        chall = json.load(f)
    chall['challenge_id'] = chall_name
    challs.append(chall)

with open("challenges.json", "w") as f:
    json.dump(challs, f)
