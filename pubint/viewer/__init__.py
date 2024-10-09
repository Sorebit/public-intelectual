import pdb
import sqlite3

import flask

from pubint import db, settings


app = flask.Flask(__name__)


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


def get_users(conn: sqlite3.Connection):
    stmt = """
        SELECT owner as name, COUNT(post_id) as post_count
        FROM comment
        GROUP BY owner
    """
    res = conn.execute(stmt)
    return res.fetchall()


@app.route("/")
def index():
    users = []
    with db.connection(settings.SQLITE_URI) as conn:
        users = get_users(conn)
    return flask.render_template("index.html", users=users)


@app.route("/<username>")
def search(username: str):
    items = []
    with db.connection(settings.SQLITE_URI) as conn:
        items = query(conn, username)

    return flask.render_template(
        "search.html",
        username=username,
        count=len(items),
        comments=items,
    )
