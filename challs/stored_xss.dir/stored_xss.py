#!/usr/bin/python3
import sqlite3
import subprocess
import sys

from flask import Flask, g, request
from werkzeug.exceptions import BadRequest


def create_app():
    """
        Initialize Flask application
    """
    app = Flask(__name__)

    @app.route('/comments', methods=['POST'])
    def post_comment():
        """
            Post a new comment
        """
        comment = request.form.get('comment')
        if not comment:
            raise BadRequest('Missing comment param')

        g.cursor.execute(
            "INSERT INTO comments(author, comment) VALUES(?,?)",
            (g.email, comment)
        )
        g.conn.commit()

        g.cursor.execute("SELECT author, comment FROM comments WHERE author IN ('admin', ?)", (g.email,))
        comments = g.cursor.fetchall()

        rows = ''
        resp = "<table>" \
               "  <tr>" \
               "    <th>Author</th>" \
               "    <th>comment</th>" \
               "  </tr>" \
               "  {}" \
               "</table>"
        for entry in comments:
            rows += "<tr>" \
                    "<td>{}</td>" \
                    "<td>{}</td>" \
                    "</tr>".format(
                      entry[0],
                      entry[1],
                    )

        return resp.format(rows)

    return app


APP = create_app()
APP.config['DEBUG'] = True
APP.config['TESTING'] = True

if __name__ == '__main__':
    email = sys.argv[1]
    comment = sys.argv[2]
    if not comment:
        print('Missing comment')
        sys.exit(0)

    # 1st step:
    # Post comment
    conn = sqlite3.connect('/tmp/stored_xss/stored_xss.db', isolation_level=None)
    cursor = conn.cursor()
    tester = APP.test_client()
    ctx = APP.test_request_context()
    ctx.push()
    g.conn = conn
    g.cursor = cursor
    g.email = email
    response = tester.post(
        '/comments',
        data=dict(comment=comment)
    )
    html = response.get_data(as_text=True)
    conn.close()

    # 2nd step:
    # The victim goes see the webpage containing the comments
    process = subprocess.Popen(('python3', 'victim_browser.py', email, html), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output.decode())
