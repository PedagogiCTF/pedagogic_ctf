#!/usr/bin/python3
import os
import subprocess
import sqlite3


def init_db():
    os.system("rm -rf /tmp/stored_xss && mkdir /tmp/stored_xss")
    db = "/tmp/stored_xss/stored_xss.db"

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

    subprocess.call(["chown", "--", "1000:1000", db])
    subprocess.call(["chmod", "--", "640", db])


def main():
    init_db()


if __name__ == "__main__":
    main()
