import pdb
import sqlite3

import flask

from pubint import db, settings

Tree = dict

app = flask.Flask(__name__)


def get_users(conn: sqlite3.Connection):
    stmt = """
        SELECT owner as name, COUNT(post_id) as post_count
        FROM comment
        GROUP BY owner
    """
    res = conn.execute(stmt)
    return res.fetchall()


def topics_with_user(conn: sqlite3.Connection, username: str) -> list[str]:
    """List of topic IDs in which given user has made at least 1 comment"""
    stmt = """
        SELECT DISTINCT topic_url
        FROM comment
        WHERE owner = :username
    """
    res = conn.execute(stmt, {"username": username})
    s2 = res.fetchall()
    a2 = [row["topic_url"] for row in s2]
    # breakpoint()
    return a2


def format_tuple(t: tuple):
    raise NotImplementedError


def query(conn: sqlite3.Connection, topic_urls: list[str]):
    """
    TODO: Topic as separate table with title
    TODO: nested reply tree
    """
    if len(topic_urls) == 0:
        return []
    # if len(topic_urls) == 1:
    #     pass
    stmt = """
        SELECT post_id, topic_url, topic_title, text_content, owner, position, indent, reply_to, reply_to_url
        FROM comment
        WHERE topic_url IN {}
        ORDER BY topic_url, position
    """
    if len(topic_urls) == 1:
        stmt = stmt.format("('{}')".format(topic_urls[0]))
    else:
        stmt = stmt.format(tuple(topic_urls))
    db.logger.error(stmt)
    # breakpoint()
    res = conn.execute(stmt)
    a2 = res.fetchall()
    # breakpoint()
    return a2


def filter_tree(tree: Tree, username: str) -> Tree:
    return tree


def filter_trees(trees: list[Tree], username: str) -> list[Tree]:
    return [filter_tree(tree, username) for tree in trees]


def create_trees_from_rows(rows: list) -> list[Tree]:
    """Expects list ordered by position with indent never increasing by more than 1"""
    roots = []
    posts_by_id = dict()
    for row in rows:
        node = {**row, "replies": []}
        posts_by_id[row["post_id"]] = node

        if node["reply_to"] is None:
            roots.append(node)
        else:
            posts_by_id[node["reply_to"]]["replies"].append(node)

    return roots


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
        topic_urls = topics_with_user(conn, username)
        comments = query(conn, topic_urls)
        items = create_trees_from_rows(comments)

    # breakpoint()
    # for item in items:
    #     item['replies'] = [item.copy()]

    return flask.render_template(
        "search.html",
        username=username,
        count=len(items),
        comments=items,
    )
