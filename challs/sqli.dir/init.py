#!/usr/bin/python3
import os
import subprocess
import sqlite3
import sys

from hashlib import sha256


def init_db(secret):
    os.system("rm -rf /tmp/sqli && mkdir /tmp/sqli")
    db = "/tmp/sqli/sqli.db"

    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS users")
    conn.commit()

    cur.execute("""CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL)""")
    conn.commit()

    cur.execute("""CREATE TRIGGER IF NOT EXISTS hook_update
                BEFORE UPDATE ON users BEGIN SELECT CASE WHEN 1=1 THEN
                RAISE (ABORT, 'UPDATE is forbidden') END; END;""")
    cur.execute("""CREATE TRIGGER IF NOT EXISTS hook_delete
                BEFORE DELETE ON users BEGIN SELECT CASE WHEN 1=1 THEN
                RAISE (ABORT, 'DELETE is forbidden') END; END;""")
    conn.commit()

    _hash = sha256(secret.encode('utf-8')).hexdigest()
    cur.execute(
        "INSERT INTO users(username, password) VALUES(?, ?)",
        (_hash, _hash)
    )
    conn.commit()
    conn.close()

    subprocess.call(["chown", "--", "1000:1000", db])
    subprocess.call(["chmod", "--", "640", db])


def main():
    secret = sys.argv[1]
    init_db(secret)


if __name__ == "__main__":
    main()
