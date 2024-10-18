import pdb
import sqlite3

import flask

from pubint import db, settings


Tree = dict


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
    return [row["topic_url"] for row in s2]


def query(conn: sqlite3.Connection, topic_urls: list[str]):
    """
    TODO: Topic as separate table with title
    """
    stmt = """
        SELECT post_id, topic_url, topic_title, text_content, owner, position, indent, reply_to, reply_to_url
        FROM comment
        WHERE topic_url IN {}
        ORDER BY topic_url, position
    """.format(db.format_tuple(topic_urls))
    db.logger.debug(stmt)
    res = conn.execute(stmt)
    return res.fetchall()


def traverse(node: Tree, fn):
    fn(node)
    for child in node["replies"]:
        traverse(child, fn)


def filter_tree(tree: Tree, nodes_by_id: dict[str, Tree], username: str) -> Tree:
    owned_by_user = []  # This will contain all nodes with owner == username

    def mark(node: Tree) -> None:
        if node["owner"] == username:
            owned_by_user.append(node)

    traverse(tree, mark)
    # Gather all paths leading from marked nodes back to root.
    # Ordering starting nodes by index (desc) prevents traversing the same path multiple times.
    by_indent_desc = sorted(owned_by_user, key=lambda node: -node["indent"])
    visited = set()
    def walk_to_root(node: Tree) -> None:
        #breakpoint()
        if node["post_id"] in visited:
            return  # Reached already traversed path
        visited.add(node["post_id"])
        parent_id = node["reply_to"]
        if parent_id is None:
            return  # Reached root for the first time
        walk_to_root(nodes_by_id[parent_id])

    for start in by_indent_desc:
        walk_to_root(start)

    def add_node_to_new_tree(node: Tree):
        original_node = nodes_by_id[node["post_id"]]
        for child in original_node["replies"]:
            if child["post_id"] in visited:
                node["replies"].append({**child, "replies": []})

        for child in node["replies"]:
            add_node_to_new_tree(child)

    new_root = {**tree, "replies": []}
    add_node_to_new_tree(new_root)

    return new_root


def filter_trees(trees: list[Tree], nodes_by_id: dict[str, Tree], username: str) -> list[Tree]:
    return [filter_tree(tree, nodes_by_id, username) for tree in trees]


def create_trees_from_rows(rows: list) -> tuple[list[Tree], dict[str, Tree]]:
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

    return roots, posts_by_id


app = flask.Flask(__name__)


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
        comments_rows = query(conn, topic_urls)
        comments, comments_by_id = create_trees_from_rows(comments_rows)

    # breakpoint()
    # for item in items:
    #     item['replies'] = [item.copy()]

    # TODO: filter on/off toggle
    topics = filter_trees(comments, comments_by_id, username)

    return flask.render_template(
        "search.html",
        username=username,
        count=len(topics),
        comments=topics,
        no_user_placeholder="użytkownik usunięty",
    )
