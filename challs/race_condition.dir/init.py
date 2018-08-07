#!/usr/bin/python3
import os
import subprocess
import sqlite3
import sys

import bcrypt


def init_db(secret):
    os.system("rm -rf /tmp/race_condition && mkdir /tmp/race_condition")
    db = "/tmp/race_condition/race_condition.db"

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS forbidden_ids")
    conn.commit()
    cur.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL)""")

    cur.execute("""CREATE TABLE forbidden_ids (user_id INTEGER NOT NULL UNIQUE)""")
    conn.commit()

    hashed_secret = bcrypt.hashpw(secret.encode("utf-8"), bcrypt.gensalt(8)).decode('utf-8')
    hashed_secret = hashed_secret.replace("$2b$", "$2a$")
    cur.execute("INSERT INTO users(login, password) VALUES(?, ?)", [secret, hashed_secret])

    conn.commit()
    conn.close()

    subprocess.call(["chown", "--", "1000:1000", db])
    subprocess.call(["chmod", "--", "640", db])


def main():
    secret = sys.argv[1]
    init_db(secret)


if __name__ == "__main__":
    main()
