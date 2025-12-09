import pytest

from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError


def test_dead_reference_error_is_reference_error():
    err = DeadReferenceError()
    assert isinstance(err, ReferenceError)


def test_dead_reference_error_raises():
    with pytest.raises(DeadReferenceError):
        raise DeadReferenceError()
