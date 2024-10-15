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
        SELECT post_id, topic_url, topic_title, text_content, owner, position, indent, reply_to
        FROM comment
        WHERE owner LIKE :username
    """
    res = conn.execute(stmt, {"username": username})
    return res.fetchall()


def topics_with_user(conn: sqlite3.Connection, username: str) -> list[str]:
    """List of topic IDs in which given user has made at least 1 comment"""
    return []


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
        # topics = topics_with_user(conn, username)
        items = query(conn, username)

    for item in items:
        item['replies'] = [item.copy()]

    return flask.render_template(
        "search.html",
        username=username,
        count=len(items),
        comments=items,
    )
