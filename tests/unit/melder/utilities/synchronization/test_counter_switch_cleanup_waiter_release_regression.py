import threading
from typing import Dict, Optional

from melder.utilities.synchronization.counter_switch import CounterSwitch


class _GatedEventProbe:
    """
    Event stand-in that makes the wake-vs-teardown interleave deterministic.

    Purpose:
        Reproduce the audited BUG-007 window on demand: a follower parked in
        ``CounterSwitch.selector()`` wakes on the cleanup-set event but is
        only allowed to resume (execute its post-wake statements) after the
        test confirms ``cleanup()`` has fully completed. This models the OS
        scheduling gap in which the old code had already torn the slots the
        woken follower reads.

    Contract:
        - ``wait`` signals ``entered_wait`` before parking on the real event,
          then holds the woken thread on ``resume_gate`` before returning.
        - ``set`` / ``clear`` / ``is_set`` delegate to the real event so the
          switch under test keeps its normal signalling semantics.
    """

    def __init__(self) -> None:
        """
        Build the probe around a fresh real event in the cleared state.
        """
        self._inner: threading.Event = threading.Event()
        self.entered_wait: threading.Event = threading.Event()
        self.resume_gate: threading.Event = threading.Event()

    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Park on the inner event, then hold the woken thread on the gate.

        Args:
            timeout:
                Follower wait timeout forwarded to the inner event.

        Returns:
            bool:
                The inner event wait result.
        """
        self.entered_wait.set()
        completed = self._inner.wait(timeout)
        self.resume_gate.wait(timeout=5.0)
        return completed

    def set(self) -> None:
        """
        Delegate to the inner event.
        """
        self._inner.set()

    def clear(self) -> None:
        """
        Delegate to the inner event.
        """
        self._inner.clear()

    def is_set(self) -> bool:
        """
        Delegate to the inner event.

        Returns:
            bool:
                Whether the inner event is set.
        """
        return self._inner.is_set()


def test_cleanup_releases_follower_woken_strictly_after_teardown_completes() -> None:
    """
    Purpose:
        Regression for BUG-007: a follower parked in ``selector()`` that is
        woken by ``cleanup()`` but only scheduled again after cleanup has
        fully completed must exit with the terminal ``0``, not crash on
        torn-down state (old code: AttributeError on the deleted
        ``_tickets`` slot).
    Contract:
        - The follower parks at pending state before cleanup starts.
        - Cleanup completes fully before the follower resumes.
        - The follower returns the terminal ``0`` and raises nothing.
    """
    switch = CounterSwitch(1)
    probe = _GatedEventProbe()
    switch._event = probe
    outcome: Dict[str, object] = {}

    def _follower() -> None:
        """
        Run one follower selector, capturing its result or failure.
        """
        try:
            outcome["state"] = switch.selector(timeout_seconds=5.0)
        except Exception as error:
            outcome["error"] = error

    thread = threading.Thread(target=_follower, daemon=True)
    thread.start()
    assert probe.entered_wait.wait(timeout=5.0) is True

    switch.cleanup()
    assert switch.cleaned is True
    # Only now may the woken follower resume: the old-code teardown has
    # deterministically already run when its post-wake statements execute.
    probe.resume_gate.set()
    thread.join(timeout=5.0)
    assert thread.is_alive() is False

    assert "error" not in outcome, f"follower crashed: {outcome.get('error')!r}"
    assert outcome["state"] == 0


def test_cleanup_releases_many_parked_followers_with_terminal_zero() -> None:
    """
    Purpose:
        End-to-end release check: several followers parked at pending state
        are all released by one cleanup call and all observe the terminal
        ``0`` without raising.
    Contract:
        - All followers park while the switch is pending.
        - One cleanup releases every follower.
        - Every follower returns ``0``; none raises.
    """
    switch = CounterSwitch(1)
    results: Dict[int, object] = {}
    started = threading.Barrier(parties=5)

    def _follower(slot: int) -> None:
        """
        Park one follower and record its selector outcome.

        Args:
            slot:
                Result-map key for this follower.
        """
        started.wait(timeout=5.0)
        try:
            results[slot] = switch.selector(timeout_seconds=5.0)
        except Exception as error:
            results[slot] = error

    threads = [
        threading.Thread(target=_follower, args=(index,), daemon=True)
        for index in range(4)
    ]
    for thread in threads:
        thread.start()
    started.wait(timeout=5.0)

    switch.cleanup()
    for thread in threads:
        thread.join(timeout=5.0)
        assert thread.is_alive() is False

    assert results == {0: 0, 1: 0, 2: 0, 3: 0}


def test_cleanup_retains_all_slots_as_alive_terminal_surfaces() -> None:
    """
    Purpose:
        Verify the retained-terminal-surface contract (LoadGate tombstone
        law): cleanup keeps every slot alive instead of deleting it, so late
        readers observe a coherent terminal state instead of AttributeError.
    Contract:
        - ``_event`` stays alive and terminally set.
        - ``_tickets`` stays alive and empty; ``len``/``bool``/``state``
          read the terminal ``0``.
        - ``fast_state`` mirror reads ``0``.
        - A second cleanup is a no-op.
    """
    switch = CounterSwitch(2)
    switch.cleanup()

    assert switch.cleaned is True
    assert switch._event.is_set() is True
    assert len(switch) == 0
    assert bool(switch) is False
    assert switch.state == 0
    assert switch.fast_state == 0
    switch.cleanup()
    assert switch.cleaned is True


def test_selector_after_cleanup_returns_terminal_zero_without_claiming() -> None:
    """
    Purpose:
        Verify a selector arriving after cleanup observes the terminal idle
        state and cannot resurrect the pending state: claiming leadership on
        a cleaned switch would clear the terminally set event and park later
        followers forever.
    Contract:
        - Post-cleanup ``selector()`` returns ``0`` immediately.
        - No ticket is appended and the event stays set.
        - The result is stable across repeated calls.
    """
    switch = CounterSwitch(0)
    switch.cleanup()

    assert switch.selector(timeout_seconds=0.5) == 0
    assert switch.selector(timeout_seconds=0.5) == 0
    assert len(switch._tickets) == 0
    assert switch.fast_state == 0
    assert switch._event.is_set() is True


def test_live_switch_behavior_is_unchanged_by_the_cleanup_fix() -> None:
    """
    Purpose:
        Guard the lockless live-path contract around the cleanup change: the
        idle leader claim, the pending follower wait, and the advance-driven
        release must behave exactly as before while the switch is live.
    Contract:
        - Idle ``selector()`` claims leadership and returns ``1``.
        - A pending follower blocks, then releases on ``advance(1)`` with
          the open state ``2``.
        - Mirror and deque stay in lockstep at every observed point.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    assert switch.fast_state == 1
    assert switch.state == 1

    done = threading.Event()
    outcome: Dict[str, int] = {}

    def _follower() -> None:
        """
        Park one follower and record its post-release state.
        """
        outcome["state"] = switch.selector(timeout_seconds=5.0)
        done.set()

    thread = threading.Thread(target=_follower, daemon=True)
    thread.start()
    assert done.wait(timeout=0.05) is False

    assert switch.advance(1) == 2
    assert done.wait(timeout=5.0) is True
    thread.join(timeout=5.0)
    assert outcome["state"] == 2
    assert switch.fast_state == 2
    switch.cleanup()
