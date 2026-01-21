import pytest
from melder.utilities.helpers.id_builder import IDBuilder


def test_create_id_returns_ulid_like_string():
    result = IDBuilder.create_id()
    # ULID strings are 26 chars, alphanumeric
    assert isinstance(result, str)
    assert len(result) == 26
    assert result.isalnum()


class Parent:
    def __init__(self, _id):
        self._id = _id


class Child:
    def __init__(self, id):
        self.id = id


def test_compose_with_child_and_parent():
    p = Parent("P1")
    c = Child("C1")
    composed = IDBuilder.compose(p, c)
    assert composed == "P1.Parent.C1.Child"


def test_compose_without_child():
    p = Parent("PX")
    composed = IDBuilder.compose(p)
    assert composed == "PX.Parent"


def test_compose_raises_when_missing_id():
    class NoId:
        pass
    with pytest.raises(AttributeError):
        IDBuilder.compose(NoId())


def test_conduit_and_ward_id_aliases():
    p = Parent("P1")
    c = Child("C1")
    w = Child("W1")
    assert IDBuilder.conduit_id(p, c) == "P1.Parent.C1.Child"
    assert IDBuilder.ward_id(c, w) == "C1.Child.W1.Child"
