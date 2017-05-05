#!/usr/bin/python3

import sqlite3
import sys

from flask import Flask, g, request
from werkzeug.exceptions import InternalServerError, Unauthorized


def get_user(username, password):
    """
        Fetch user in database
    """
    g.cursor.execute(
        "SELECT username FROM users WHERE username='{}' AND password='{}'".format(
            username,
            password
        )
    )
    return g.cursor.fetchone()


def create_app():
    """
        Initialize Flask application
    """
    app = Flask(__name__)

    @app.route('/login', methods=['POST'])
    def get_secret_page():
        """
            Get secret page
        """
        username = request.form['username']
        password = request.form['password']

        try:
            user = get_user(username, password)
            if not user:
                raise Unauthorized('Invalid username/password')
        except sqlite3.OperationalError:
            raise InternalServerError('Something went wrong')

        with open('secret') as _file:
            secret = _file.read().strip()

        return 'You are logged in. The secret is {}'.format(secret)

    return app


APP = create_app()
APP.config['DEBUG'] = True
APP.config['TESTING'] = True


if __name__ == '__main__':

    # Parse params
    if len(sys.argv) != 3:
        print("Missing parameters")
        sys.exit(0)

    username = sys.argv[1]
    password = sys.argv[2]

    if not all((username, password)):
        print("Missing username or password")
        sys.exit(0)

    # Init app and db cursor
    try:
        tester = APP.test_client()
        ctx = APP.test_request_context()
        ctx.push()
        conn = sqlite3.connect('/tmp/sqli.db', isolation_level=None)
        cursor = conn.cursor()
        g.cursor = cursor
    except:
        print('Error while connecting to db.')
        sys.exit(1)

    # Make request
    response = tester.post(
        '/login',
        data=dict(
            username=username,
            password=password
        )
    )

    print(response.get_data().decode('unicode_escape'))
