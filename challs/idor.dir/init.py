#!/usr/bin/python3

import os
import sqlite3
import sys


def init_db(user, secret):

    db = os.path.join(os.path.sep, "tmp", "idor.db")

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS accounts")
    conn.commit()
    cur.execute("""CREATE TABLE accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                token TEXT NOT NULL UNIQUE,
                balance INT NOT NULL DEFAULT 100,
                description TEXT NOT NULL DEFAULT '')""")
    conn.commit()

    token = 'JqcY6oUYCiVtvyfyN7r6z461hjhG!r7SzfnndZDYvuzicSmAyaVvr6RFlZZhEorS'
    cur.execute(
        "INSERT INTO accounts(username, token, balance, description) VALUES(?, ?, ?, ?)",
        ('586b652384404', token, 1337, 'The secret is {}'.format(secret))
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
    init_db(user, secret)
    init_secret(secret)


if __name__ == "__main__":
    main()
