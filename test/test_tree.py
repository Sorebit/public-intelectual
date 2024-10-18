import pytest

from pubint.viewer import query, filter_tree, create_trees_from_rows, Tree, traverse


@pytest.fixture
def name() -> str:
    return "JOHN"


@pytest.fixture
def nonexistent_name() -> str:
    return "NONEXISTENT"


def mk_row(post_id, owner, reply_to, indent):
    return {
        # "text_content": None,
        "post_id": post_id,
        "reply_to": reply_to,
        "owner": owner,
        "indent": indent,
    }


def mk_node(post_id, owner, indent, replies):
    post = {"post_id": post_id, "owner": owner, "replies": replies, "indent": indent, "reply_to": None}
    for reply in replies:
        reply["reply_to"] = post_id
    return post


def mk_node_map(tree: Tree) -> dict[str, Tree]:
    nodes_by_id = dict()

    def process(node: Tree) -> None:
        nodes_by_id[node["post_id"]] = node

    traverse(tree, process)
    return nodes_by_id


@pytest.fixture
def rows_1(name):
    return [
        mk_row(101, "A", None, 0),
        mk_row(102, "A", 101, 1),
        mk_row(103, name, 102, 2),
        mk_row(104, "C", 101, 1),
        mk_row(105, "D", 101, 1),
        mk_row(106, "C", 105, 2),
        mk_row(107, name, 106, 3),
        mk_row(108, "A", 107, 4),
        mk_row(109, "A", 105, 2),
    ]



@pytest.fixture
def tree_1(name):
    return mk_node(101, "A", 0, [
        mk_node(102, "A", 1, [
            mk_node(103, name, 2, []),
        ]),
        mk_node(104, "C", 1, []),
        mk_node(105, "D", 1, [
            mk_node(106, "C", 2, [
                mk_node(107, name, 3, [
                    mk_node(108, "A", 4, []),
                ]),
            ]),
            mk_node(109, "A", 2, []),
        ]),
    ])


@pytest.fixture
def tree_1_map(tree_1):
    return mk_node_map(tree_1)


@pytest.fixture
def rows_deleted_user():
    return [
        mk_row(201, "A", None, 0),
        mk_row(202, None, None, 1), # position=1, indent=1
        mk_row(203, "B", 202, 2),
        mk_row(204, "C", 202, 2),
        mk_row(205, None, 202, 2), # position=4, indent=2
        mk_row(206, None, 201, 1), # position=5, indent=1
    ]


@pytest.fixture
def tree_deleted_user():
    return mk_node(201, "A", 0, [
        mk_node(202, None, 1, [
            mk_node(203, "B", 2, []),
            mk_node(204, "C", 2, []),
            mk_node(205, None, 2, []),
        ]),
        mk_node(206, None, 1, []),
    ])

@pytest.fixture
def tree_banned_comment():
    return mk_node(

    )

@pytest.fixture
def tree_monologue(name):
    return mk_node(301, name, 0, [
        mk_node(302, name, 1, [
            mk_node(303, name, 2, [
                mk_node(304, name, 3, [])
            ])
        ])
    ])


def test_can_transform_rows_into_tree(rows_1, tree_1):
    result, _ = create_trees_from_rows(rows_1)
    assert result == [tree_1]


@pytest.mark.skip
def test_create_trees_can_handle_deleted_users(rows_deleted_user, tree_deleted_user):
    result, _ = create_trees_from_rows(rows_deleted_user)
    assert result == [tree_deleted_user]


def test_tree_cuts_off_at_deepest_occur(name, tree_1, tree_1_map):
    expected = filter_tree(tree_1, tree_1_map, name)
    assert expected == mk_node(101, "A", 0, [
        mk_node(102, "A", 1, [
            mk_node(103, name, 2, []),
        ]),
        mk_node(105, "D", 1, [
            mk_node(106, "C", 2, [
                mk_node(107, name, 3, []),
            ]),
        ]),
    ])


def test_tree_empty_when_not_found(nonexistent_name, tree_1, tree_1_map):
    expected = filter_tree(tree_1, tree_1_map, nonexistent_name)
    assert expected == None
