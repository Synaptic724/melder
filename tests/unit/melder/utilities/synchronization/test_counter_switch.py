import threading

import pytest

from melder.utilities.synchronization.counter_switch import CounterSwitch


def test_counter_switch_defaults_to_open_latch() -> None:
    """
    Purpose:
        Verify default construction starts in open state.
    Contract:
        - Default state is ``2``.
        - Bool view is True.
        - Selector returns immediately with ``2``.
    """
    switch = CounterSwitch()
    assert switch.state == 2
    assert bool(switch) is True
    assert switch.selector() == 2


def test_counter_switch_selector_claims_leader_from_idle() -> None:
    """
    Purpose:
        Verify selector performs leader claim from idle.
    Contract:
        - ``0 -> 1`` on first selector call.
        - Returned mode is ``1``.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    assert switch.state == 1
    assert bool(switch) is False


def test_counter_switch_selector_follower_waits_until_open() -> None:
    """
    Purpose:
        Verify follower selector waits while pending.
    Contract:
        - Leader claim sets state ``1``.
        - Follower blocks while pending.
        - Advancing to ``2`` releases follower.
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
    assert switch.advance(1) == 2
    assert done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    assert result_holder["state"] >= 2


def test_counter_switch_selector_timeout_raises_while_pending() -> None:
    """
    Purpose:
        Verify pending follower wait can time out.
    Contract:
        - After leader claim (`1`), follower selector with short timeout
          raises ``TimeoutError`` when state does not change.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    with pytest.raises(TimeoutError):
        switch.selector(timeout_seconds=0.01)


def test_counter_switch_selector_returns_idle_after_pending_dropped() -> None:
    """
    Purpose:
        Verify pending follower observes idle when pending is cleared.
    Contract:
        - Leader claim sets ``1``.
        - Follower waits.
        - ``advance(-1)`` transitions ``1 -> 0`` and releases follower.
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
    assert switch.advance(-1) == 0
    assert done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    assert result_holder["state"] == 0


def test_counter_switch_selector_returns_full_state_value() -> None:
    """
    Purpose:
        Verify selector returns raw state above open threshold.
    Contract:
        - State ``3`` is returned as ``3``.
    """
    switch = CounterSwitch(3)
    assert switch.selector() == 3


def test_counter_switch_advance_updates_counter_and_bool_view() -> None:
    """
    Purpose:
        Verify signed advance updates state and bool view.
    Contract:
        - Positive delta appends tickets.
        - Negative delta pops tickets.
        - Bool is true only for state >= 2.
    """
    switch = CounterSwitch(0)
    assert switch.advance(3) == 3
    assert switch.state == 3
    assert bool(switch) is True
    assert switch.advance(-2) == 1
    assert switch.state == 1
    assert bool(switch) is False
    assert switch.advance(-1) == 0
    assert switch.state == 0
    assert bool(switch) is False


def test_counter_switch_advance_zero_is_noop() -> None:
    """
    Purpose:
        Verify zero delta leaves state unchanged.
    Contract:
        - ``advance(0)`` returns current state.
        - State remains unchanged.
    """
    switch = CounterSwitch(2)
    assert switch.advance(0) == 2
    assert switch.state == 2


def test_counter_switch_repeated_cycles_with_selector_and_advance() -> None:
    """
    Purpose:
        Verify repeated ``0 -> 1 -> 2 -> 0`` cycles.
    Contract:
        - Selector claims leader from idle each cycle.
        - Follower returns open after ``advance(1)``.
        - ``advance(-2)`` returns to idle.
    """
    switch = CounterSwitch(0)
    for _ in range(5):
        assert switch.selector() == 1
        done = threading.Event()
        follower_state: list[int] = []

        def _follower() -> None:
            follower_state.append(switch.selector(timeout_seconds=1.0))
            done.set()

        thread = threading.Thread(target=_follower, daemon=True)
        thread.start()
        assert done.wait(timeout=0.05) is False
        assert switch.advance(1) == 2
        assert done.wait(timeout=1.0) is True
        thread.join(timeout=1.0)
        assert follower_state[0] >= 2
        assert switch.advance(-2) == 0


def test_counter_switch_cleanup_wakes_pending_selector_waiter() -> None:
    """
    Purpose:
        Verify cleanup releases waiters blocked in selector.
    Contract:
        - Pending follower selector exits after cleanup.
        - Internal references are nulled.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1

    done = threading.Event()
    result_holder: dict[str, object] = {}

    def _follower() -> None:
        try:
            result_holder["state"] = switch.selector(timeout_seconds=1.0)
        except Exception as exc:
            result_holder["error"] = exc
        finally:
            done.set()

    thread = threading.Thread(target=_follower, daemon=True)
    thread.start()
    assert done.wait(timeout=0.05) is False
    switch.cleanup()
    assert done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    assert switch._event is None
    assert switch._tickets is None
    assert switch._lock is None
    if "state" in result_holder:
        assert isinstance(result_holder["state"], int)
    else:
        assert isinstance(result_holder.get("error"), TypeError)


def test_counter_switch_post_cleanup_usage_breaks_fast() -> None:
    """
    Purpose:
        Verify non-defensive post-cleanup usage fails.
    Contract:
        - Calling stateful methods after cleanup raises due torn internals.
    """
    switch = CounterSwitch()
    switch.cleanup()
    with pytest.raises(TypeError):
        _ = switch.selector()
