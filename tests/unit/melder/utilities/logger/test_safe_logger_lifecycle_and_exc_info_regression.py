"""Regression: BUG-147/BUG-148 (2026-07-17 audit) - SafeLogger lifecycle + exc fidelity.

BUG-147 symptom:
    ``SafeLogger.cleanup()`` cleared the wrapped logger reference but never
    set ``_cleaned=True``. After ``SafeLogger(None).cleanup()``, ``.cleaned``
    stayed False and ``check_cleaned()`` did not raise, so owners and
    diagnostics could not distinguish an active silent logger from a
    terminally cleaned one.

BUG-148 symptom:
    On the stdlib path, ``error(..., exc_info=<BaseException>)`` treated every
    truthy ``exc_info`` as ``logger.exception(msg)`` without forwarding the
    supplied object. Outside an active handler the record carried
    ``(None, None, None)`` instead of the caller's exception.

Contracts under test:
    - Terminal cleanup flips the Cleanable flag, is idempotent, and
      ``check_cleaned()`` refuses use-after-clean.
    - An explicit exception object is forwarded to the stdlib record;
      boolean ``True`` still uses the active exception context.
"""

import logging
from typing import Iterator, List

import pytest

from melder.utilities.logger.safe_logger import SafeLogger


class _RecordCapture(logging.Handler):
    """Handler double that captures every emitted record for inspection."""

    def __init__(self) -> None:
        """Initialize the capture list at the permissive level."""
        super().__init__(level=logging.DEBUG)
        self.records: List[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        """Append one captured record.

        Args:
            record:
                The record the wrapped stdlib logger dispatched.
        """
        self.records.append(record)


@pytest.fixture()
def captured_std_logger() -> Iterator[tuple]:
    """Provide an isolated stdlib logger wired to a capture handler.

    Contract:
        - The logger is non-propagating so records never reach global
          handlers.
        - The capture handler is detached afterwards so no state leaks
          between tests.
    """
    logger = logging.getLogger("melder.tests.safe_logger_regression")
    capture = _RecordCapture()
    logger.addHandler(capture)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    yield logger, capture
    logger.removeHandler(capture)


def test_cleanup_marks_null_adapter_cleaned_and_guard_refuses() -> None:
    """The audited BUG-147 repro: ``SafeLogger(None).cleanup()`` must latch.

    Contract assertions:
        - ``cleaned`` reads True after cleanup.
        - ``check_cleaned()`` raises the canonical use-after-clean error.
        - A second cleanup call is a no-op.
    """
    adapter = SafeLogger(None)
    assert adapter.cleaned is False

    adapter.cleanup()

    assert adapter.cleaned is True, (
        "terminal cleanup left the Cleanable flag unset (the audited "
        "BUG-147 symptom)"
    )
    with pytest.raises(RuntimeError, match="SafeLogger has already been cleaned"):
        adapter.check_cleaned()
    adapter.cleanup()
    assert adapter.cleaned is True


def test_cleanup_releases_wrapped_logger_and_emits_become_no_ops(
    captured_std_logger: tuple,
) -> None:
    """Cleanup of a wrapped adapter detaches the sink and stays log-safe.

    Contract assertions:
        - ``is_attached`` flips to False and the cleaned flag latches.
        - Emit calls after cleanup are silent no-ops through the null-logger
          path (no record reaches the old sink, no exception raised).
    """
    logger, capture = captured_std_logger
    adapter = SafeLogger(logger)

    adapter.cleanup()

    assert adapter.cleaned is True
    assert adapter.is_attached is False
    adapter.error("post-cleanup message", "test_method", exc_info=False)
    assert capture.records == []


def test_error_forwards_explicit_exception_instance_on_stdlib_path(
    captured_std_logger: tuple,
) -> None:
    """The audited BUG-148 repro: explicit exception objects must survive.

    Contract assertions:
        - Outside any active handler, the record carries the caller-supplied
          exception type and value (broken code recorded
          ``(None, None, None)``).
    """
    logger, capture = captured_std_logger
    adapter = SafeLogger(logger)
    supplied = ValueError("boom")

    adapter.error("explicit exception lost?", "test_method", exc_info=supplied)

    assert len(capture.records) == 1
    exc_info = capture.records[0].exc_info
    assert exc_info is not None, "record carried no exception info"
    assert exc_info[0] is ValueError, (
        f"record lost the supplied exception type: {exc_info!r} "
        "(the audited BUG-148 symptom)"
    )
    assert exc_info[1] is supplied


def test_error_with_true_still_uses_active_exception_context(
    captured_std_logger: tuple,
) -> None:
    """Boolean ``True`` keeps the historical active-context semantics.

    Contract assertions:
        - Inside an active handler, ``exc_info=True`` records the caught
          exception exactly as before the fix.
    """
    logger, capture = captured_std_logger
    adapter = SafeLogger(logger)

    try:
        raise KeyError("caught")
    except KeyError:
        adapter.error("active context", "test_method", exc_info=True)

    assert len(capture.records) == 1
    exc_info = capture.records[0].exc_info
    assert exc_info is not None
    assert exc_info[0] is KeyError


def test_error_without_exception_context_emits_plain_record(
    captured_std_logger: tuple,
) -> None:
    """Falsy ``exc_info`` must produce a plain error record.

    Contract assertions:
        - ``exc_info=False`` records no exception info at all.
    """
    logger, capture = captured_std_logger
    adapter = SafeLogger(logger)

    adapter.error("plain error", "test_method", exc_info=False)

    assert len(capture.records) == 1
    assert capture.records[0].exc_info is None
