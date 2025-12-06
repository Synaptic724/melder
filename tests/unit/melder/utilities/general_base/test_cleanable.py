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


def test_context_manager_using_cleanup_calls_cleanup():
    obj = DummyCleanable()
    with obj.using_cleanup() as inner:
        assert inner is obj
        assert obj.cleaned is False
    assert obj.cleaned is True
    assert obj.cleaned_count == 1


def test_using_cleanup_does_not_suppress_exceptions():
    obj = DummyCleanable()
    with pytest.raises(ZeroDivisionError):
        with obj.using_cleanup():
            1 / 0
    assert obj.cleaned is True
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


def test_using_cleanup_swallows_cleanup_exception():
    obj = FailingCleanable()
    with obj.using_cleanup():
        pass
    # Even though cleanup raises, context manager should swallow
    assert obj.cleaned is True
    assert obj.cleaned_count == 1


def test_using_cleanup_multiple_times_idempotent():
    obj = DummyCleanable()
    for _ in range(2):
        with obj.using_cleanup():
            pass
    assert obj.cleaned_count == 1


def test_async_cleanup_then_using_cleanup_noop():
    obj = DummyCleanable()
    import asyncio

    asyncio.run(obj.async_cleanup())
    with obj.using_cleanup():
        pass
    assert obj.cleaned_count == 1
