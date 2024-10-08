from contextlib import contextmanager
import pdb
import sqlite3

import flask

from pubint import settings


app = flask.Flask(__name__)


@contextmanager
def connection(db_uri: str):
    def dict_factory(cursor: sqlite3.Cursor, row):
        fields = [column[0] for column in cursor.description]
        return {k: v for k, v in zip(fields, row)}

    print(f"Connecting to {db_uri}")
    connection = sqlite3.connect(db_uri, uri=True)
    connection.row_factory = dict_factory
    yield connection
    print(f"Closing connection to {db_uri}")
    connection.rollback()
    connection.close()



def query(conn: sqlite3.Connection, username: str):
    """
    TODO: Topic as separate table with title
    TODO: nested reply tree
    """
    stmt = ""
    stmt += """
        SELECT post_id, topic_url, text_content, owner, position, indent, reply_to
        FROM comment
        WHERE owner LIKE :username
    """
    res = conn.execute(stmt, {"username": username})
    return res.fetchall()


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/<username>")
def search(username: str):
    items = []
    with connection(settings.SQLITE_URI) as conn:
        items = query(conn, username)

    return flask.render_template(
        "search.html",
        username=username,
        count=len(items),
        comments=items,
    )
