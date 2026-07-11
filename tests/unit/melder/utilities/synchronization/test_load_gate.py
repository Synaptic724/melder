import threading
import time

import pytest

from melder.utilities.synchronization.load_gate import LoadGate


def test_load_gate_initial_state_open() -> None:
    """
    Purpose:
        Verify a fresh gate starts open with no holder.
    Contract:
        - is_held() is False.
        - describe() reports no holder thread and no label.
    """
    gate = LoadGate()
    assert gate.is_held() is False
    snapshot = gate.describe()
    assert snapshot["holder_thread_id"] is None
    assert snapshot["holder_label"] is None
    gate.cleanup()


def test_load_gate_acquire_records_holder_and_label() -> None:
    """
    Purpose:
        Verify acquire claims the gate for the calling thread.
    Contract:
        - is_held() flips True.
        - describe() reports the calling thread id and the given label.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:01TEST")
    assert gate.is_held() is True
    snapshot = gate.describe()
    assert snapshot["holder_thread_id"] == threading.get_ident()
    assert snapshot["holder_label"] == "checkpoint_load:01TEST"
    gate.release()
    gate.cleanup()


def test_load_gate_acquire_requires_label() -> None:
    """
    Purpose:
        Verify acquire refuses falsy labels.
    Contract:
        - ValueError is raised; the gate stays open.
    """
    gate = LoadGate()
    with pytest.raises(ValueError):
        gate.acquire("")
    assert gate.is_held() is False
    gate.cleanup()


def test_load_gate_second_acquire_refuses_naming_holder() -> None:
    """
    Purpose:
        Verify one-load-at-a-time: a second acquire refuses, even from the
        holder thread (nested acquire is a pairing bug, not a wait).
    Contract:
        - RuntimeError names the holding load's label.
    """
    gate = LoadGate()
    gate.acquire("first_load")
    with pytest.raises(RuntimeError, match="first_load"):
        gate.acquire("second_load")
    gate.release()
    gate.cleanup()


def test_load_gate_release_requires_holder_thread() -> None:
    """
    Purpose:
        Verify release discipline.
    Contract:
        - Releasing an open gate raises RuntimeError.
        - Releasing from a non-holder thread raises RuntimeError.
    """
    gate = LoadGate()
    with pytest.raises(RuntimeError):
        gate.release()

    gate.acquire("owned_elsewhere")
    errors: list = []

    def foreign_release() -> None:
        try:
            gate.release()
        except RuntimeError as exc:
            errors.append(exc)

    thread = threading.Thread(target=foreign_release)
    thread.start()
    thread.join()
    assert len(errors) == 1
    assert gate.is_held() is True
    gate.release()
    gate.cleanup()


def test_load_gate_wait_for_passage_open_gate_is_noop() -> None:
    """
    Purpose:
        Verify the mediator hot path: an open gate passes immediately.
    Contract:
        - wait_for_passage returns without blocking.
    """
    gate = LoadGate()
    started = time.monotonic()
    gate.wait_for_passage(timeout=5.0)
    assert time.monotonic() - started < 1.0
    gate.cleanup()


def test_load_gate_holder_thread_passes_free() -> None:
    """
    Purpose:
        Verify the loading thread's own transactions pass while it holds the
        gate ("the loading thread has all control").
    Contract:
        - wait_for_passage returns immediately for the holder thread.
    """
    gate = LoadGate()
    gate.acquire("self_load")
    started = time.monotonic()
    gate.wait_for_passage(timeout=5.0)
    assert time.monotonic() - started < 1.0
    gate.release()
    gate.cleanup()


def test_load_gate_foreign_thread_waits_and_resumes_on_release() -> None:
    """
    Purpose:
        Verify a foreign thread parks during a load and resumes on release.
    Contract:
        - wait_for_passage blocks while held by another thread.
        - release() wakes the waiter before its timeout.
    """
    gate = LoadGate()
    gate.acquire("blocking_load")
    resumed = threading.Event()

    def foreign_wait() -> None:
        gate.wait_for_passage(timeout=10.0)
        resumed.set()

    thread = threading.Thread(target=foreign_wait)
    thread.start()
    time.sleep(0.2)
    assert resumed.is_set() is False

    gate.release()
    thread.join(timeout=5.0)
    assert resumed.is_set() is True
    gate.cleanup()


def test_load_gate_foreign_thread_timeout_names_load_label() -> None:
    """
    Purpose:
        Verify the teach-grade timeout: a starved waiter learns WHICH load
        holds the system.
    Contract:
        - RuntimeError message contains the holder label.
    """
    gate = LoadGate()
    gate.acquire("slow_world_load")
    errors: list = []

    def starved_wait() -> None:
        try:
            gate.wait_for_passage(timeout=0.2)
        except RuntimeError as exc:
            errors.append(str(exc))

    thread = threading.Thread(target=starved_wait)
    thread.start()
    thread.join(timeout=5.0)
    assert len(errors) == 1
    assert "slow_world_load" in errors[0]
    gate.release()
    gate.cleanup()


def test_load_gate_cleanup_wakes_waiters_and_is_idempotent() -> None:
    """
    Purpose:
        Verify teardown never strands a parked waiter.
    Contract:
        - cleanup() clears the holder and notifies waiters.
        - cleanup() is idempotent.
    """
    gate = LoadGate()
    gate.acquire("teardown_load")
    resumed = threading.Event()

    def parked_wait() -> None:
        gate.wait_for_passage(timeout=10.0)
        resumed.set()

    thread = threading.Thread(target=parked_wait)
    thread.start()
    time.sleep(0.2)

    gate.cleanup()
    thread.join(timeout=5.0)
    assert resumed.is_set() is True
    gate.cleanup()
