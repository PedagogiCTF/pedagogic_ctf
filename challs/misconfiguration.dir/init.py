#!/usr/bin/python3

import os
import subprocess
import sqlite3
import sys

from base64 import b64encode
from random import randrange
from hashlib import sha1


def generate_user_token():
    """
    Generates an API token for given username
    """
    return sha1(b64encode(bytes(randrange(1, 99999)))).hexdigest()


def init_db(db_user):
    db = os.path.join(os.path.sep, "tmp", "misconfiguration.db")

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    cur.execute("""CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                token TEXT NOT NULL)""")
    conn.commit()

    cur.execute("INSERT INTO users(username, token) VALUES(?, ?)", ('debug-e9bc7d25d163', 'e9bc7d25d16348f9c5f6b9251c270c0da39aff8b'))
    for user in "root", "debug", "user", "admin", "whynot", 'debug-true':
        trand = generate_user_token()
        cur.execute(
            "INSERT INTO users(username, token) VALUES(?, ?)",
            (user, trand)
            )
    conn.commit()
    conn.close()

    subprocess.call(["chown", "--", "{}:{}".format(user, user), db])
    subprocess.call(["chmod", "--", "640", db])


def init_secret(secret):
    with open('secret', "w") as _file:
        _file.write(secret)


def main():
    secret = sys.argv[1]
    user = sys.argv[2]
    init_db(user)
    init_secret(secret)


if __name__ == "__main__":
    main()
