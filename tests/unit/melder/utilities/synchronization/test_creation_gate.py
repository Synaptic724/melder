import threading
import time
from typing import Callable

import pytest

from melder.utilities.synchronization.creation_gate import CreationGate


def test_creation_gate_initial_state_enabled() -> None:
    """
    Purpose:
        Verify default CreationGate starts open and unclosed.
    Contract:
        - enabled=True by default.
        - gate is not terminally closed.
        - ticket deque starts empty.
    """
    gate = CreationGate()
    assert gate.enabled is True
    assert gate.is_closed() is False
    assert gate.has_active_tickets() is False
    assert gate.active_ticket_count() == 0


def test_creation_gate_initial_state_disabled() -> None:
    """
    Purpose:
        Verify disabled initialization starts closed-for-entry but not terminally closed.
    Contract:
        - enabled=False when constructed disabled.
        - gate remains non-terminal.
    """
    gate = CreationGate(enabled=False)
    assert gate.enabled is False
    assert gate.is_closed() is False
    assert gate.has_active_tickets() is False


def test_creation_gate_register_unregister_tickets() -> None:
    """
    Purpose:
        Verify ticket accounting increments/decrements correctly.
    """
    gate = CreationGate()
    gate.register_ticket()
    gate.register_ticket()
    assert gate.active_ticket_count() == 2
    gate.unregister_ticket()
    assert gate.active_ticket_count() == 1
    gate.unregister_ticket()
    assert gate.active_ticket_count() == 0


def test_creation_gate_unregister_without_ticket_raises() -> None:
    """
    Purpose:
        Ensure ticket pairing errors are surfaced as IndexError.
    """
    gate = CreationGate()
    with pytest.raises(IndexError):
        gate.unregister_ticket()


def test_creation_gate_has_active_tickets_false_when_empty() -> None:
    """
    Purpose:
        Verify has_active_tickets reflects empty state.
    """
    gate = CreationGate()
    assert gate.has_active_tickets() is False


def test_creation_gate_wait_returns_immediately_when_enabled() -> None:
    """
    Purpose:
        Validate wait fast-path when gate is already enabled.
    """
    gate = CreationGate(enabled=True)
    started = time.perf_counter()
    gate.wait()
    elapsed = time.perf_counter() - started
    assert elapsed < 0.05


def test_creation_gate_wait_blocks_until_open() -> None:
    """
    Purpose:
        Verify disabled gate blocks waiters until open() is called.
    """
    gate = CreationGate(enabled=False)
    waiter_started = threading.Event()
    waiter_released = threading.Event()

    def _waiter() -> None:
        waiter_started.set()
        gate.wait()
        waiter_released.set()

    worker = threading.Thread(target=_waiter, daemon=True)
    worker.start()
    assert waiter_started.wait(timeout=1.0) is True
    assert waiter_released.wait(timeout=0.05) is False
    gate.open()
    assert waiter_released.wait(timeout=1.0) is True
    worker.join(timeout=1.0)


def test_creation_gate_close_disables_and_open_reenables() -> None:
    """
    Purpose:
        Verify close/open transitions enabled flag.
    """
    gate = CreationGate()
    gate.close()
    assert gate.enabled is False
    gate.open()
    assert gate.enabled is True


def test_creation_gate_cleanup_sets_closed_and_unblocks_waiters() -> None:
    """
    Purpose:
        Verify cleanup terminally closes and releases waiters.
    """
    gate = CreationGate(enabled=False)
    waiter_released = threading.Event()

    def _waiter() -> None:
        gate.wait()
        waiter_released.set()

    worker = threading.Thread(target=_waiter, daemon=True)
    worker.start()
    assert waiter_released.wait(timeout=0.05) is False
    gate.cleanup()
    assert waiter_released.wait(timeout=1.0) is True
    worker.join(timeout=1.0)
    assert gate.is_closed() is True
    assert gate.enabled is True


def test_creation_gate_cleanup_idempotent() -> None:
    """
    Purpose:
        Verify repeated cleanup calls are safe.
    """
    gate = CreationGate()
    gate.register_ticket()
    gate.cleanup()
    gate.cleanup()
    assert gate.is_closed() is True
    assert gate.has_active_tickets() is False


def test_creation_gate_cleanup_returns_when_marked_clean_inside_lock() -> None:
    """
    Purpose:
        Cover defensive cleanup branch where cleaned flips true after lock entry.
    """
    gate = CreationGate()

    class _LockThatFlipsCleaned:
        def __enter__(self) -> "_LockThatFlipsCleaned":
            gate._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    gate._lock = _LockThatFlipsCleaned()
    gate.cleanup()
    assert gate._cleaned is True
    assert gate.is_closed() is False


@pytest.mark.parametrize(
    "method_name,args",
    [
        ("open", ()),
        ("close", ()),
        ("active_ticket_count", ()),
        ("close_and_wait_until_free", ()),
    ],
)
def test_creation_gate_methods_raise_after_cleanup(
    method_name: str,
    args: tuple[object, ...],
) -> None:
    """
    Purpose:
        Ensure guarded methods reject calls after cleanup.
    """
    gate = CreationGate()
    gate.cleanup()
    method: Callable[..., object] = getattr(gate, method_name)
    with pytest.raises(RuntimeError, match="CreationGate has already been cleaned"):
        method(*args)


def test_creation_gate_close_and_wait_until_free_blocks_until_drain() -> None:
    """
    Purpose:
        Verify close_and_wait_until_free waits for in-flight tickets.
    """
    gate = CreationGate()
    registered = threading.Event()
    release = threading.Event()
    close_done = threading.Event()

    def _ticket_worker() -> None:
        gate.register_ticket()
        registered.set()
        release.wait(timeout=2.0)
        gate.unregister_ticket()

    def _close_worker() -> None:
        gate.close_and_wait_until_free(timeout=2.0, interval=0.01)
        close_done.set()

    ticket_thread = threading.Thread(target=_ticket_worker, daemon=True)
    close_thread = threading.Thread(target=_close_worker, daemon=True)
    ticket_thread.start()
    assert registered.wait(timeout=1.0) is True
    close_thread.start()
    assert close_done.wait(timeout=0.05) is False
    release.set()
    assert close_done.wait(timeout=1.0) is True
    ticket_thread.join(timeout=1.0)
    close_thread.join(timeout=1.0)


def test_creation_gate_close_and_wait_until_free_timeout_raises() -> None:
    """
    Purpose:
        Verify timeout path raises when tickets do not drain.
    """
    gate = CreationGate()
    gate.register_ticket()
    with pytest.raises(RuntimeError, match="Timeout waiting for creation tickets to drain"):
        gate.close_and_wait_until_free(timeout=0.05, interval=0.01)
    gate.unregister_ticket()


def test_creation_gate_close_and_wait_until_free_sets_closed_and_disabled() -> None:
    """
    Purpose:
        Verify terminal close semantics set closed=True and enabled=False.
    """
    gate = CreationGate()
    gate.close_and_wait_until_free(timeout=0.1, interval=0.01)
    assert gate.is_closed() is True
    assert gate.enabled is False


def test_creation_gate_wait_returns_after_close_and_wait_signals_event() -> None:
    """
    Purpose:
        Verify waiters are released when close_and_wait signals event.
    """
    gate = CreationGate(enabled=False)
    released = threading.Event()

    def _waiter() -> None:
        gate.wait()
        released.set()

    worker = threading.Thread(target=_waiter, daemon=True)
    worker.start()
    assert released.wait(timeout=0.05) is False
    gate.close_and_wait_until_free(timeout=0.1, interval=0.01)
    assert released.wait(timeout=1.0) is True
    worker.join(timeout=1.0)


def test_creation_gate_is_closed_after_cleanup() -> None:
    """
    Purpose:
        Verify cleanup marks terminal closure.
    """
    gate = CreationGate()
    assert gate.is_closed() is False
    gate.cleanup()
    assert gate.is_closed() is True


def test_creation_gate_is_closed_after_close_and_wait() -> None:
    """
    Purpose:
        Verify close_and_wait marks terminal closure.
    """
    gate = CreationGate()
    assert gate.is_closed() is False
    gate.close_and_wait_until_free(timeout=0.1, interval=0.01)
    assert gate.is_closed() is True


def test_creation_gate_active_ticket_count_multiple_rounds() -> None:
    """
    Purpose:
        Verify ticket count remains correct over repeated round-trips.
    """
    gate = CreationGate()
    for _ in range(3):
        gate.register_ticket()
        gate.register_ticket()
        assert gate.active_ticket_count() == 2
        gate.unregister_ticket()
        gate.unregister_ticket()
        assert gate.active_ticket_count() == 0


def test_creation_gate_register_ticket_after_terminal_close_still_counts() -> None:
    """
    Purpose:
        Document that ticket registration itself does not enforce gate entry policy.
    """
    gate = CreationGate()
    gate.close_and_wait_until_free(timeout=0.1, interval=0.01)
    gate.register_ticket()
    assert gate.active_ticket_count() == 1
    gate.unregister_ticket()


def test_creation_gate_cleanup_clears_existing_tickets() -> None:
    """
    Purpose:
        Verify cleanup drops in-flight ticket bookkeeping.
    """
    gate = CreationGate()
    gate.register_ticket()
    gate.register_ticket()
    assert gate.active_ticket_count() == 2
    gate.cleanup()
    assert gate.has_active_tickets() is False


def test_creation_gate_close_keeps_non_terminal_state() -> None:
    """
    Purpose:
        Verify non-terminal close does not set closed flag.
    """
    gate = CreationGate()
    gate.close()
    assert gate.enabled is False
    assert gate.is_closed() is False
