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


def test_counter_switch_cleanup_is_idempotent() -> None:
    """
    Purpose:
        Verify cleanup is safe to call more than once.
    Contract:
        - The first call tears the switch down and marks it cleaned.
        - A second call is a no-op and does not raise, even though the first
          call already released every slot.
    """
    switch = CounterSwitch(2)
    switch.cleanup()
    assert switch.cleaned is True

    switch.cleanup()
    assert switch.cleaned is True


def test_counter_switch_post_cleanup_use_is_out_of_contract() -> None:
    """
    Purpose:
        Pin the terminal teardown posture: cleanup releases every owned slot
        under normal ``del`` posture, so the switch is not usable afterwards.

    Contract:
        - Cleanup is TERMINAL. Post-cleanup access raises ``AttributeError``
          rather than serving a synthetic idle state.
        - This is deliberate. A ``CounterSwitch`` is cleaned up by its owner
          once its threads are DONE; using one afterwards is out of contract in
          exactly the same way as any other use-after-clean, and failing loudly
          beats quietly answering ``0`` and hiding the misuse.
        - The switch cannot defend this itself: ticket cardinality is the STATE
          value, not a count of callers, so it has no way to observe or drain
          in-flight selectors.
    """
    switch = CounterSwitch()
    switch.cleanup()

    for probe in (
        lambda: switch.selector(timeout_seconds=0.1),
        lambda: len(switch),
        lambda: bool(switch),
        lambda: switch.state,
        lambda: switch.advance(1),
        lambda: switch.fast_state,
    ):
        with pytest.raises(AttributeError):
            probe()


def test_counter_switch_fast_state_mirrors_construction_states() -> None:
    """
    Purpose:
        Verify the fast-state mirror matches deque state after construction.
    Contract:
        - ``fast_state`` equals authoritative ``state`` for idle, pending,
          open, and above-open construction values.
    """
    for initial_state in (0, 1, 2, 3):
        switch = CounterSwitch(initial_state)
        assert switch.fast_state == initial_state
        assert switch.fast_state == switch.state


def test_counter_switch_fast_state_tracks_advance_mutations() -> None:
    """
    Purpose:
        Verify signed advances keep the fast-state mirror exact.
    Contract:
        - Mirror matches authoritative state after each signed mutation.
        - ``advance(0)`` leaves the mirror untouched.
    """
    switch = CounterSwitch(0)
    assert switch.advance(3) == 3
    assert switch.fast_state == 3
    assert switch.advance(-2) == 1
    assert switch.fast_state == 1
    assert switch.advance(0) == 1
    assert switch.fast_state == 1
    assert switch.advance(-1) == 0
    assert switch.fast_state == 0


def test_counter_switch_fast_state_tracks_selector_leader_claim() -> None:
    """
    Purpose:
        Verify the selector leader claim updates the fast-state mirror.
    Contract:
        - Idle leader claim moves the mirror ``0 -> 1`` so hot readers
          cannot observe an open state before publication advances it.
    """
    switch = CounterSwitch(0)
    assert switch.selector() == 1
    assert switch.fast_state == 1
    assert switch.fast_state == switch.state


def test_counter_switch_cleanup_releases_the_mirror_slot() -> None:
    """
    Purpose:
        Verify the fast-state mirror is released with the rest of the owned
        slots under normal ``del`` posture.

    Contract:
        - ``fast_state`` is owned state, not a retained tombstone, so it goes
          away with the deque, event, and lock.
        - Live mirror correctness is covered by the ``advance`` and leader-claim
          mirror tests above; this one pins only the teardown posture.
    """
    switch = CounterSwitch(5)
    assert switch.fast_state == 5

    switch.cleanup()

    with pytest.raises(AttributeError):
        _ = switch.fast_state
