import pytest

from pubint.viewer import query


@pytest.fixture
def name() -> str:
    return "JOHN"


@pytest.fixture
def nonexistent_name() -> str:
    return "NONEXISTENT"


def C(u, r):
    return {"u": u, "r": r}


@pytest.fixture
def topic_1(name):
    return C("A", [
        C("A", [
            C(name, []),
        ]),
        C("C", []),
        C("D", [
            C("C", [
                C(name, [
                    C("A", []),
                ]),
            ]),
            C("A", []),
        ]),
    ])


def extract_for(topic, username) -> dict:
    return {}


def test_can_transform_rows_into_tree():
    assert False


def test_tree_cuts_off_at_deepest_occur(name, topic_1):
    expected = extract_for(topic_1, name)
    assert expected == C("A", [
        C("A", [
            C(name, []),
        ]),
        C("D", [
            C("C", [
                C(name, []),
            ]),
        ]),
    ])


def test_tree_empty_when_not_found(nonexistent_name, topic_1):
    expected = extract_for(topic_1, nonexistent_name)
    assert expected is None
