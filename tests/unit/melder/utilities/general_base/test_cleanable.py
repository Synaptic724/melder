import pytest

from melder.utilities.general_base.cleanable import Cleanable


class DummyCleanable(Cleanable):
    def __init__(self):
        super().__init__()
        self.cleaned_count = 0

    def cleanup(self):
        if self._cleaned:
            return
        self.cleaned_count += 1
        self._cleaned = True

    async def async_cleanup(self):
        self.cleanup()


def test_cleaned_flag_and_check_cleaned():
    obj = DummyCleanable()
    assert obj.cleaned is False
    obj.cleanup()
    assert obj.cleaned is True
    with pytest.raises(RuntimeError):
        obj.check_cleaned()


def test_cleanup_idempotent():
    obj = DummyCleanable()
    obj.cleanup()
    obj.cleanup()
    assert obj.cleaned_count == 1

def test_async_cleanup_defers_to_cleanup():
    obj = DummyCleanable()
    assert obj.cleaned is False
    import asyncio

    asyncio.run(obj.async_cleanup())
    assert obj.cleaned is True
    assert obj.cleaned_count == 1


def test_is_cleaned_alias():
    obj = DummyCleanable()
    assert obj.is_cleaned is False
    obj.cleanup()
    assert obj.is_cleaned is True


def test_check_cleaned_message_contains_classname():
    obj = DummyCleanable()
    obj.cleanup()
    with pytest.raises(RuntimeError) as excinfo:
        obj.check_cleaned()
    assert "DummyCleanable" in str(excinfo.value)


class FailingCleanable(DummyCleanable):
    def cleanup(self):
        self.cleaned_count += 1
        self._cleaned = True
        raise RuntimeError("cleanup boom")
