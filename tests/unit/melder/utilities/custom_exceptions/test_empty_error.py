import pytest

from melder.utilities.custom_exceptions.empty_error import Empty


def test_empty_is_exception():
    err = Empty()
    assert isinstance(err, Exception)


def test_empty_raises():
    with pytest.raises(Empty):
        raise Empty("container empty")
