#!/usr/bin/python3

import os
import sqlite3
import sys


def init_db(user):

    db = os.path.join(os.path.sep, "tmp", "broken_authentication.db")

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    cur.execute("""CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                token TEXT NOT NULL)""")
    conn.commit()

    cur.execute(
        "INSERT INTO users(username, token) VALUES(?, ?)",
        ('admin', 'f5c828ff122cd8d0509051584236cceb28c78bfa')
    )
    conn.commit()

    cur.execute(
        "INSERT INTO users(username, token) VALUES(?, ?)",
        ('debug-e9bc7d25d163', 'e9bc7d25d16348f9c5f6b9251c270c0da39aff8b')
    )

    conn.commit()
    conn.close()

    os.system('chown {}:{} {}'.format(user, user, db))
    os.system('chmod 640 ' + db)


def init_secret(secret):

    with open('secret', "w") as _file:
        _file.write(secret)


def main():

    secret = sys.argv[2]
    user = sys.argv[3]
    init_db(user)
    init_secret(secret)


if __name__ == "__main__":
    main()
