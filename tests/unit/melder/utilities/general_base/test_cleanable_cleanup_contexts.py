"""Contracts for `Cleanable.using_cleanup()` and `async_using_cleanup()`.

Contract under test:
    The helper contexts call the owner's cleanup at most once on exit, never
    swallow the block's exception, and let a cleanup error propagate - chained
    to the block's exception when both fail.
"""

import asyncio
from typing import List

import pytest

from melder.utilities.general_base.cleanable import Cleanable


class _Resource(Cleanable):
    """
    Purpose:
        A Cleanable whose sync and async cleanup can be told to fail.
    Contract:
        `calls` records every cleanup attempt; `fail` makes each attempt raise
        ValueError after recording it.
    """

    __slots__ = Cleanable.__slots__ + ["calls", "fail"]

    def __init__(self, fail: bool) -> None:
        """
        Purpose: Create a live resource.
        Args: fail: Whether cleanup raises.
        Returns: None.
        """
        super().__init__()
        self.calls: List[str] = []
        self.fail: bool = fail

    def cleanup(self) -> None:
        """
        Record the call, then fail or mark the resource cleaned.

        Raises:
            ValueError: When `fail` is set.
        """
        self.calls.append("cleanup")
        if self.fail:
            raise ValueError("cleanup failed")
        self._cleaned = True

    async def async_cleanup(self) -> None:
        """
        Record the call, then fail or mark the resource cleaned.

        Raises:
            ValueError: When `fail` is set.
        """
        self.calls.append("async_cleanup")
        if self.fail:
            raise ValueError("async cleanup failed")
        self._cleaned = True


def test_using_cleanup_propagates_the_cleanup_error() -> None:
    """A failing cleanup is no longer swallowed."""
    resource = _Resource(fail=True)
    with pytest.raises(ValueError, match="cleanup failed"):
        with resource.using_cleanup():
            pass
    assert resource.calls == ["cleanup"]


def test_using_cleanup_chains_the_cleanup_error_to_the_block_error() -> None:
    """When block and cleanup both fail, the cleanup error rises with the block's error as its context."""
    resource = _Resource(fail=True)
    with pytest.raises(ValueError, match="cleanup failed") as raised:
        with resource.using_cleanup():
            raise KeyError("boom")
    assert isinstance(raised.value.__context__, KeyError)


def test_using_cleanup_keeps_the_block_error_when_cleanup_succeeds() -> None:
    """A clean cleanup never hides the block's exception."""
    resource = _Resource(fail=False)
    with pytest.raises(KeyError, match="boom"):
        with resource.using_cleanup():
            raise KeyError("boom")
    assert resource.cleaned is True


def test_using_cleanup_runs_cleanup_at_most_once() -> None:
    """The helper releases its owner after the first exit, even when cleanup failed."""
    resource = _Resource(fail=True)
    context = resource.using_cleanup()
    with pytest.raises(ValueError):
        with context:
            pass
    with pytest.raises(RuntimeError, match="no longer owns"):
        with context:
            pass
    assert resource.calls == ["cleanup"]


def test_async_using_cleanup_propagates_the_cleanup_error() -> None:
    """The async twin lets a failing async cleanup propagate, once."""
    resource = _Resource(fail=True)

    async def run() -> None:
        """Enter and leave the async helper context once."""
        async with resource.async_using_cleanup():
            pass

    with pytest.raises(ValueError, match="async cleanup failed"):
        asyncio.run(run())
    assert resource.calls == ["async_cleanup"]
