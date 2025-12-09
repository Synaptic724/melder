import pytest

from melder.utilities.custom_exceptions.operation_cancelled_error import OperationCancelledError


def test_operation_cancelled_error_is_runtime_error():
    err = OperationCancelledError()
    assert isinstance(err, RuntimeError)


def test_operation_cancelled_error_raises():
    with pytest.raises(OperationCancelledError):
        raise OperationCancelledError("stopped")
