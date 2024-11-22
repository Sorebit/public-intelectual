import pdb
import sqlite3

import flask

from pubint import db, settings


Tree = dict


def get_users(conn: sqlite3.Connection, page: int = 0, page_size: int = 150) -> list:
    stmt = """
        SELECT owner as name, COUNT(post_id) as post_count
        FROM comment
        GROUP BY owner
        ORDER BY owner
        LIMIT :page_size
        OFFSET :offset
    """
    res = conn.execute(stmt, {"offset": page * page_size, "page_size": page_size})
    return res.fetchall()


def get_stats(conn: sqlite3.Connection, user: str | None = None) -> dict:
    stmt = """
        SELECT
            COUNT(DISTINCT topic_url) as total_topics, COUNT(DISTINCT post_id) as total_posts, COUNT(DISTINCT owner) as total_users
        FROM comment
    """
    if user:
        stmt += "WHERE owner = :user"
    res = conn.execute(stmt, {"user": user})
    return res.fetchone()


def topics_with_user(conn: sqlite3.Connection, username: str) -> list[str]:
    """List of topic IDs in which given user has made at least 1 comment"""
    stmt = """
        SELECT DISTINCT topic_url
        FROM comment
        WHERE owner = :username
    """
    res = conn.execute(stmt, {"username": username})
    return [row["topic_url"] for row in res.fetchall()]


def get_comments(conn: sqlite3.Connection, topic_urls: list[str]) -> list:
    """List of comments comprising given topics
    TODO: Topic as separate table with title
    """
    stmt = """
        SELECT post_id, topic_url, topic_title, text_content, owner, position, indent, reply_to, reply_to_url
        FROM comment
        WHERE topic_url IN {}
        ORDER BY topic_url, position
    """.format(db.format_tuple(topic_urls))
    res = conn.execute(stmt)
    return res.fetchall()


def create_trees_from_rows(rows: list) -> tuple[list[Tree], dict[str, Tree]]:
    """Expects list ordered by position with indent never increasing by more than 1"""
    roots = []
    posts_by_id = dict()
    latest_with_indent = dict()

    for row in rows:
        node = {**row, "replies": []}
        posts_by_id[row["post_id"]] = node
        latest_with_indent[node["indent"]] = node

        if node["indent"] == 0:
            roots.append(node)
            continue

        if node["reply_to"] is None:
            # Node's owner was deleted or post was banned
            up = latest_with_indent.get(node["indent"] - 1)
            if up is None:
                breakpoint()
            node["reply_to"] = up["post_id"]

        posts_by_id[node["reply_to"]]["replies"].append(node)

    return roots, posts_by_id


def traverse(node: Tree, fn) -> None:
    fn(node)
    for child in node["replies"]:
        traverse(child, fn)


def filter_tree(root: Tree, nodes_by_id: dict[str, Tree], username: str) -> Tree | None:
    owned_by_user = []  # This will contain all nodes with owner == username

    def mark(node: Tree) -> None:
        if node["owner"] == username:
            owned_by_user.append(node)

    traverse(root, mark)
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
    if not visited:
        return None

    def add_to_new_tree(node: Tree):
        original_node = nodes_by_id[node["post_id"]]
        for child in original_node["replies"]:
            if child["post_id"] in visited:
                node["replies"].append({**child, "replies": []})

    new_root = {**root, "replies": []}
    traverse(new_root, add_to_new_tree)

    return new_root


def filter_trees(trees: list[Tree], nodes_by_id: dict[str, Tree], username: str) -> list[Tree]:
    result = []
    for tree in trees:
        filtered = filter_tree(tree, nodes_by_id, username)
        if filtered:
            result.append(filtered)
    return result


app = flask.Flask(__name__)


@app.route("/")
def index():
    try:
        page = int(flask.request.args.get("page", 0))
    except ValueError:
        flask.abort(404)

    users = []
    with db.connection(settings.SQLITE_URI, echo=True) as conn:
        users = get_users(conn, page=page)
        stats = get_stats(conn)

    return flask.render_template("index.html", users=users, stats=stats, page=page)


@app.route("/<username>")
def search(username: str):
    items = []
    with db.connection(settings.SQLITE_URI, echo=True) as conn:
        topic_urls = topics_with_user(conn, username)
        comments_rows = get_comments(conn, topic_urls)
        stats = get_stats(conn, username)

    topics, posts_by_id = create_trees_from_rows(comments_rows)

    # TODO: filter on/off toggle
    topics = filter_trees(topics, posts_by_id, username)

    return flask.render_template(
        "search.html",
        username=username,
        comments=topics,
        stats=stats,
        no_user_placeholder="użytkownik usunięty",
        banned_text_placeholder="Wpis został zablokowany z uwagi na jego niezgodność z regulaminem",
    )
