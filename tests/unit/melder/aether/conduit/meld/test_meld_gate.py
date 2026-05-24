import threading

import pytest

from melder.utilities.synchronization.creation_gate import CreationGate


def test_creation_gate_initial_state_enabled() -> None:
    """
    Purpose:
        Verify the default CreationGate starts enabled and open.
    Contract:
        - enabled=True by default.
        - Gate is not terminally closed.
        - No active tickets are registered.
    Returns:
        None.
    Raises:
        AssertionError: If initial state is incorrect.
    """
    gate = CreationGate()
    assert gate.enabled is True
    assert gate.is_closed() is False
    assert gate.has_active_tickets() is False
    assert gate.active_ticket_count() == 0


def test_creation_gate_register_unregister_tickets() -> None:
    """
    Purpose:
        Verify ticket tracking increments and decrements correctly.
    Contract:
        - register_ticket increases active_ticket_count.
        - unregister_ticket decreases active_ticket_count.
    Returns:
        None.
    Raises:
        AssertionError: If ticket counts do not match.
    """
    gate = CreationGate()
    gate.register_ticket()
    gate.register_ticket()
    assert gate.active_ticket_count() == 2
    gate.unregister_ticket()
    gate.unregister_ticket()
    assert gate.active_ticket_count() == 0


def test_creation_gate_unregister_without_ticket_raises() -> None:
    """
    Purpose:
        Ensure unregister_ticket fails when no tickets exist.
    Contract:
        - unregister_ticket raises IndexError when the deque is empty.
    Returns:
        None.
    Raises:
        AssertionError: If the IndexError is not raised.
    """
    gate = CreationGate()
    with pytest.raises(IndexError):
        gate.unregister_ticket()


def test_creation_gate_wait_blocks_until_open() -> None:
    """
    Purpose:
        Verify wait blocks while the gate is disabled and returns after open().
    Contract:
        - wait blocks when enabled=False.
        - wait returns after open() sets enabled=True and releases the Event.
    Returns:
        None.
    Raises:
        AssertionError: If wait does not block or does not release.
    """
    gate = CreationGate(enabled=False)
    waiter_started = threading.Event()
    waiter_released = threading.Event()

    def _waiter() -> None:
        waiter_started.set()
        gate.wait()
        waiter_released.set()

    worker = threading.Thread(target=_waiter)
    worker.start()

    assert waiter_started.wait(timeout=2.0) is True
    assert waiter_released.is_set() is False

    gate.open()
    assert waiter_released.wait(timeout=2.0) is True
    worker.join(timeout=1.0)


def test_creation_gate_close_and_wait_until_free_blocks_until_drain() -> None:
    """
    Purpose:
        Ensure close_and_wait_until_free blocks until active tickets drain.
    Contract:
        - The call blocks while active tickets exist.
        - The gate is terminally closed when the call returns.
    Returns:
        None.
    Raises:
        AssertionError: If the call does not block or gate state is incorrect.
    """
    gate = CreationGate()
    ticket_registered = threading.Event()
    allow_release = threading.Event()
    close_started = threading.Event()
    close_done = threading.Event()

    def _ticket_worker() -> None:
        gate.register_ticket()
        ticket_registered.set()
        allow_release.wait(timeout=2.0)
        gate.unregister_ticket()

    def _closer() -> None:
        close_started.set()
        gate.close_and_wait_until_free(timeout=2.0, interval=0.01)
        close_done.set()

    worker = threading.Thread(target=_ticket_worker)
    closer = threading.Thread(target=_closer)
    worker.start()
    assert ticket_registered.wait(timeout=2.0) is True
    closer.start()

    assert close_started.wait(timeout=1.0) is True
    assert close_done.wait(timeout=0.1) is False

    allow_release.set()
    assert close_done.wait(timeout=2.0) is True

    worker.join(timeout=1.0)
    closer.join(timeout=1.0)

    assert gate.is_closed() is True
    assert gate.enabled is False


def test_creation_gate_cleanup_marks_closed_and_blocks_ops() -> None:
    """
    Purpose:
        Verify cleanup marks the gate as closed and prevents reuse.
    Contract:
        - cleanup clears tickets and marks the gate closed.
        - check_cleaned guards open/close after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup fails to enforce closed state.
    """
    gate = CreationGate()
    gate.register_ticket()
    gate.cleanup()

    assert gate._cleaned is True
    assert gate._closed is True
    assert not hasattr(gate, "_event")
    assert not hasattr(gate, "_tickets")

    with pytest.raises(AttributeError):
        gate.open()
    with pytest.raises(AttributeError):
        gate.close()
