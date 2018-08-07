#!/usr/bin/python3

import os
import subprocess
import sqlite3


def init_db():
    os.system("rm -rf /tmp/broken_authentication && mkdir /tmp/broken_authentication")
    db = "/tmp/broken_authentication/broken_authentication.db"

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

    subprocess.call(["chown", "--", "1000:1000", db])
    subprocess.call(["chmod", "--", "640", db])


def main():
    init_db()


if __name__ == "__main__":
    main()
