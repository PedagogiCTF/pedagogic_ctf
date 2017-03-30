#!/usr/bin/python3

import sqlite3
import sys

from base64 import b64encode
from time import sleep
from urllib.parse import quote

import requests

from redis import Redis
from rq import Queue

SELENIUM_HOST = "selenium.pedagogic_ctf"
HOST = 'my-site.com'
PORT = 8888
DB_REQUEST_PATH = '/internal/debug/get-comments'

selenium_queue = Queue(
    connection=Redis(
        host=SELENIUM_HOST,
        port=6379
    ),
    name='selenium'
)


def victim_browse(user_email, secret):
    """
        Fake a browser navigation
    """
    con = sqlite3.connect('/tmp/stored_xss.db', isolation_level=None)
    dump = b64encode(bytes(
        '\n'.join(line for line in con.iterdump() if '"sqlite_sequence"' not in line),
        "utf-8"
    )).decode()
    con.close()

    job = selenium_queue.enqueue(
        'worker.get_screenshot',
        host=HOST,
        port=PORT,
        path=DB_REQUEST_PATH,
        client=user_email,
        secret=secret,
        db_dump=quote(dump)
    )

    while job.status != 'finished':
        sleep(0.2)

    return job.result


def main():

    ctf_user_email = sys.argv[1]

    with open('secret') as _file:
        secret = _file.read().strip()

    victim_response = victim_browse(ctf_user_email, secret)

    logs = requests.get('http://{}:{}/internal/debug/get-logs?client={}'.format(
        SELENIUM_HOST,
        PORT,
        ctf_user_email
    )).text

    response = "<h2>Victim browser's screenshot</h2><br>{}<h2>Server logs</h2><pre>{}</pre>"
    response = response.format(victim_response, logs)
    print(response)

if __name__ == '__main__':

    main()
