import pytest

from pubint.viewer import query, filter_tree, create_trees_from_rows


@pytest.fixture
def name() -> str:
    return "JOHN"


@pytest.fixture
def nonexistent_name() -> str:
    return "NONEXISTENT"


def mk_row(post_id, owner, reply_to):
    return {
        # "text_content": None,
        "post_id": post_id,
        "reply_to": reply_to,
        "owner": owner,
    }


def mk_node(post_id, owner, replies):
    post = {"post_id": post_id, "owner": owner, "replies": replies, "reply_to": None}
    for reply in replies:
        reply["reply_to"] = post_id
    return post


@pytest.fixture
def rows_1(name):
    return [
        mk_row(101, "A", None),
        mk_row(102, "A", 101),
        mk_row(103, name, 102),
        mk_row(104, "C", 101),
        mk_row(105, "D", 101),
        mk_row(106, "C", 105),
        mk_row(107, name, 106),
        mk_row(108, "A", 107),
        mk_row(109, "A", 105),
    ]



@pytest.fixture
def tree_1(name):
    return mk_node(101, "A", [
        mk_node(102, "A", [
            mk_node(103, name, []),
        ]),
        mk_node(104, "C", []),
        mk_node(105, "D", [
            mk_node(106, "C", [
                mk_node(107, name, [
                    mk_node(108, "A", []),
                ]),
            ]),
            mk_node(109, "A", []),
        ]),
    ])


def test_can_transform_rows_into_tree(rows_1, tree_1):
    assert create_trees_from_rows(rows_1) == [tree_1]


def test_tree_cuts_off_at_deepest_occur(name, tree_1):
    expected = filter_tree(tree_1, name)
    assert len(expected) == 1
    assert expected[0] == mk_node(101, "A", [
        mk_node(102, "A", [
            mk_node(103, name, []),
        ]),
        mk_node(105, "D", [
            mk_node(106, "C", [
                mk_node(107, name, []),
            ]),
        ]),
    ])


def test_tree_empty_when_not_found(nonexistent_name, tree_1):
    expected = filter_tree(tree_1, nonexistent_name)
    assert expected == []
