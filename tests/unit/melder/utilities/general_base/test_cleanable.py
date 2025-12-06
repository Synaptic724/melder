import pytest

from melder.utilities.general_base.cleanable import Cleanable


class _Dummy(Cleanable):
    def __init__(self):
        super().__init__()
        self.cleaned_called = False

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self.cleaned_called = True
        self._cleaned = True


def test_check_cleaned_raises_after_cleanup():
    dummy = _Dummy()
    dummy.cleanup()
    assert dummy.cleaned is True
    with pytest.raises(RuntimeError):
        dummy.check_cleaned()


def test_cleanup_idempotent():
    dummy = _Dummy()
    dummy.cleanup()
    assert dummy.cleaned_called is True
    # Second call should be a no-op
    dummy.cleanup()
    assert dummy.cleaned is True
