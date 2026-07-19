"""
Live-path guard for `CounterSwitch`.

HISTORY (2026-07-19): this file previously held four BUG-007 regressions that
pinned the "retained terminal surface" (LoadGate tombstone) cleanup contract -
they asserted that a follower parked in `selector()` could be woken by
`cleanup()` and would exit with a terminal ``0``, and that every slot stayed
alive after teardown.

That contract was REVERSED by owner ruling. `CounterSwitch.cleanup()` now uses
normal ``del`` posture and releases all four owned slots. The rationale: a
switch is cleaned up by its owner once its threads are DONE, so a selector
in flight during teardown is out-of-contract use in the same category as any
other use-after-clean. The switch cannot defend against it anyway - ticket
cardinality is the STATE value, not a count of callers, so it has no way to
observe or drain in-flight selectors.

Those four regressions were removed rather than inverted; the terminal posture
they used to forbid is now pinned directly in
`test_counter_switch.py::test_counter_switch_post_cleanup_use_is_out_of_contract`.

What remains here is the live-path guard, which the cleanup ruling does not
touch: while the switch is alive, leader election, follower parking, and
advance-driven release must behave exactly as before.
"""

import threading
from typing import Dict

from melder.utilities.synchronization.counter_switch import CounterSwitch


def test_live_switch_behavior_is_unchanged_by_the_cleanup_ruling() -> None:
    """
    Purpose:
        Guard the lockless live-path contract across the cleanup change: the
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
