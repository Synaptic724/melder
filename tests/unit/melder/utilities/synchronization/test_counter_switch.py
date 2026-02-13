import threading
import time

import pytest

from melder.utilities.synchronization.counter_switch import CounterSwitch


def test_counter_switch_defaults_to_open_latch() -> None:
    """
    Purpose:
        Verify default construction starts in open latch mode.
    Contract:
        - Default state is ``2``.
        - Bool view is true.
        - Selector returns ``2`` immediately.
    """
    switch = CounterSwitch()
    assert switch.state == 2
    assert bool(switch) is True
    assert switch.selector() == 2


def test_counter_switch_selector_claims_leader_from_idle() -> None:
    """
    Purpose:
        Verify selector performs owner election from idle state.
    Contract:
        - ``0 -> 1`` transition occurs on selector call.
        - Selector returns ``1`` for elected leader.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    assert switch.state == 1
    assert bool(switch) is False


def test_counter_switch_close_selector_promotes_pending_to_open() -> None:
    """
    Purpose:
        Verify leader close operation opens latch and releases waiters.
    Contract:
        - Pending ``1`` becomes open ``2`` after close.
        - Selector then returns ``2``.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    switch.close_selector()
    assert switch.state == 2
    assert switch.selector() == 2


def test_counter_switch_selector_waits_while_pending_until_closed() -> None:
    """
    Purpose:
        Verify followers block while state is pending.
    Contract:
        - Follower selector call blocks at ``1``.
        - Follower resumes after leader close.
        - Follower receives open state.
    """
    switch = CounterSwitch(0)
    leader_mode = switch.selector()
    assert leader_mode == 1

    done = threading.Event()
    result_holder: dict[str, int] = {}

    def _follower() -> None:
        result_holder["state"] = switch.selector(timeout_seconds=1.0)
        done.set()

    thread = threading.Thread(target=_follower, daemon=True)
    thread.start()
    assert done.wait(timeout=0.05) is False
    switch.close_selector()
    assert done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    assert result_holder["state"] >= 2


def test_counter_switch_selector_timeout_raises_when_stuck_pending() -> None:
    """
    Purpose:
        Verify selector timeout when leader never closes pending state.
    Contract:
        - Pending wait with finite timeout raises ``TimeoutError``.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    with pytest.raises(TimeoutError):
        switch.selector(timeout_seconds=0.01)


def test_counter_switch_selector_returns_real_state_after_wait_to_idle() -> None:
    """
    Purpose:
        Verify selector returns actual state, not a synthetic busy code.
    Contract:
        - Follower blocks at pending.
        - External reset to idle wakes follower.
        - Follower returns ``0``.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    done = threading.Event()
    result_holder: dict[str, int] = {}

    def _follower() -> None:
        result_holder["state"] = switch.selector(timeout_seconds=1.0)
        done.set()

    thread = threading.Thread(target=_follower, daemon=True)
    thread.start()
    assert done.wait(timeout=0.05) is False
    switch.reset_idle()
    assert done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    assert result_holder["state"] == 0


def test_counter_switch_close_selector_is_noop_when_not_pending() -> None:
    """
    Purpose:
        Verify close operation only acts on pending state.
    Contract:
        - Close on idle keeps state idle.
        - Close on open keeps state open.
    """
    idle = CounterSwitch(0)
    idle.close_selector()
    assert idle.state == 0

    open_switch = CounterSwitch(2)
    open_switch.close_selector()
    assert open_switch.state == 2


def test_counter_switch_wait_if_pending_exits_after_close_selector() -> None:
    """
    Purpose:
        Verify explicit pending waiter exits after leader close.
    Contract:
        - Waiter blocks while state equals ``1``.
        - Waiter exits once close promotes to ``2``.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    done = threading.Event()
    result_holder: dict[str, int] = {}

    def _waiter() -> None:
        result_holder["state"] = switch.wait_if_pending()
        done.set()

    thread = threading.Thread(target=_waiter, daemon=True)
    thread.start()
    assert done.wait(timeout=0.05) is False
    switch.close_selector()
    assert done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    assert result_holder["state"] >= 2


def test_counter_switch_wait_until_complete_blocks_from_idle() -> None:
    """
    Purpose:
        Verify complete wait blocks below threshold.
    Contract:
        - Idle state blocks completion waiter.
        - Completion publish releases waiter.
    """
    switch = CounterSwitch(0)
    done = threading.Event()

    def _waiter() -> None:
        switch.wait_until_complete()
        done.set()

    thread = threading.Thread(target=_waiter, daemon=True)
    thread.start()
    assert done.wait(timeout=0.05) is False
    switch.set_complete()
    assert done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)


def test_counter_switch_cleanup_wakes_selector_waiters() -> None:
    """
    Purpose:
        Verify cleanup releases selector waiters blocked on pending state.
    Contract:
        - Pending selector follower exits after cleanup.
        - Cleanup tears down condition reference.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    done = threading.Event()
    result_holder: dict[str, int] = {}

    def _follower() -> None:
        result_holder["state"] = switch.selector(timeout_seconds=1.0)
        done.set()

    thread = threading.Thread(target=_follower, daemon=True)
    thread.start()
    assert done.wait(timeout=0.05) is False
    switch.cleanup()
    assert done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    assert result_holder["state"] >= 2
    assert switch._condition is None


def test_counter_switch_mutation_after_cleanup_breaks_fast() -> None:
    """
    Purpose:
        Verify non-defensive post-cleanup usage fails quickly.
    Contract:
        - Methods using torn condition raise.
    """
    switch = CounterSwitch()
    switch.cleanup()
    with pytest.raises(TypeError):
        switch.set_complete()


def test_counter_switch_selector_returns_full_state_value() -> None:
    """
    Purpose:
        Verify selector returns raw state count when above open threshold.
    Contract:
        - State ``3`` is returned as ``3``.
    """
    switch = CounterSwitch(3)
    assert switch.selector() == 3


def test_counter_switch_advance_and_reset_maintain_counter_model() -> None:
    """
    Purpose:
        Verify signed adjustments and explicit resets.
    Contract:
        - Positive advance appends tickets.
        - Reset replaces ticket cardinality exactly.
    """
    switch = CounterSwitch(0)
    assert switch.advance(3) == 3
    assert switch.state == 3
    switch.reset(1)
    assert switch.state == 1
    switch.close_selector()
    assert switch.state == 2


def test_counter_switch_leader_follower_sequence_under_repeated_cycles() -> None:
    """
    Purpose:
        Verify repeated leader/follower cycles preserve latch behavior.
    Contract:
        - Each cycle performs ``0 -> 1 -> 2``.
        - Selector from follower returns open after close.
    """
    switch = CounterSwitch(0)
    for _ in range(5):
        assert switch.selector() == 1
        follower_state: list[int] = []

        def _follower() -> None:
            follower_state.append(switch.selector(timeout_seconds=1.0))

        thread = threading.Thread(target=_follower, daemon=True)
        thread.start()
        time.sleep(0.002)
        switch.close_selector()
        thread.join(timeout=1.0)
        assert follower_state[0] >= 2
        switch.reset_idle()
