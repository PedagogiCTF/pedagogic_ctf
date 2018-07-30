#!/usr/bin/python3

import os
import subprocess
import sqlite3
import sys


def init_db(user):
    db = os.path.join(os.path.sep, "tmp", "stored_xss.db")

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS comments")
    conn.commit()
    cur.execute("""CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                comment TEXT NOT NULL)""")
    conn.commit()

    cur.execute(
        "INSERT INTO comments(author, comment) VALUES(?, ?)",
        ('admin', 'Not funny comment, please.')
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
