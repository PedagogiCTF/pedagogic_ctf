#!/usr/bin/python3

import logging

from base64 import b64decode
from logging.handlers import RotatingFileHandler

import sqlite3

from flask import Flask, request

HOST = 'my-site.com'
PORT = 8888
NOT_LOGGED_PATH = (
    '/favicon.ico',
    '/internal/debug/get-comments',
    '/internal/debug/get-logs',
)

CSS = """<head>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>
</head>"""


def create_app():
    """
        Initialize Flask application
    """
    app = Flask(__name__)

    @app.before_request
    def log_request():

        if request.path not in NOT_LOGGED_PATH:

            try:
                msg = "{} - {} {} ".format(
                    request.headers['Referer'].split('=')[1],
                    request.method,
                    request.url,
                )
                app.logger.warning(msg)
            except KeyError:
                pass

    @app.route('/internal/debug/get-comments')
    def get_comments():
        html = request.args.get('html')

        response = CSS + html
        return response

    @app.route('/internal/debug/get-logs')
    def get_logs():

        author = request.args['client']

        with open('/tmp/api.log', 'r') as log:
            srv_logs = log.readlines()

        srv_logs = '<br>'.join([l.strip().replace(author + "&html", "") for l in srv_logs if author in l or '* Running' in l])
        srv_logs = srv_logs.replace('http://{}'.format(HOST), 'http://evil.com')

        return srv_logs

    return app


def main():
    """
        Start internal API for selenium-based challenges
    """
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app = create_app()

    handler = RotatingFileHandler('/tmp/api.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)

    app.logger.addHandler(handler)
    app.logger.warning('* Running on http://{}:{}/ (Press CTRL+C to quit)'.format(HOST, PORT))
    app.run(host="0.0.0.0", port=PORT)


if __name__ == '__main__':

    main()
