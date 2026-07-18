"""Regression: BUG-073 (2026-07-17 audit) - Existence.many first use is atomic.

Symptom (Critical):
    The lazy `many` bucket initialization performed an unsynchronized
    read / conditional-assign / append sequence. Two threads resolving the
    same key for the first time each observed the missing bucket, each
    created a list, overwrote one another's bucket, and appended their
    distinct creation only to their private list: both resolutions returned
    live objects, but lifetime storage and disposal tracking retained only
    one - the other object escaped lifecycle ownership entirely.

Contract under test:
    First-use bucket creation and both appends run atomically under the
    store lock; every successfully returned managed creation stays
    represented in both the live bucket and the disposal registry, and
    cleanup disposes every returned object.
"""

import threading
from typing import Any, Dict, List, Optional

from melder.aether.conduit.creations.creations import Creations


class DisposalProbe:
    """Creation double whose disposal calls are counted.

    Contract:
        - `dispose()` increments a counter so tests can prove every returned
          creation is reachable by cleanup exactly once.
    """

    def __init__(self, label: str) -> None:
        """Create the probe with a zeroed disposal counter."""
        self.label = label
        self.dispose_calls = 0

    def dispose(self) -> None:
        """Record one disposal invocation."""
        self.dispose_calls += 1


class GatedReadDict(dict):
    """Dict double that parks the first gated read per registered thread.

    Purpose:
        Make the audited first-use interleave deterministic: the read result
        is captured FIRST, then the thread parks, then the captured value is
        returned - modeling the scheduling gap between a thread's read of the
        missing bucket and its later assignment. On the broken code both
        racers therefore observe the missing bucket before either assigns;
        on the fixed code the second racer blocks on the store lock and never
        reads until the first finished.

    Contract:
        - Only reads of `target_key` gate, at most once per thread, for at
          most two distinct threads.
        - `get` and `__contains__` capture their result before parking so
          the returned observation predates the park.
    """

    def __init__(self, target_key: str) -> None:
        """Initialize the gate registry for one contended key."""
        super().__init__()
        self.target_key = target_key
        self.entered_events: List[threading.Event] = [
            threading.Event(), threading.Event(),
        ]
        self.release_events: List[threading.Event] = [
            threading.Event(), threading.Event(),
        ]
        self._registry_lock = threading.Lock()
        self._slot_by_thread: Dict[int, int] = {}

    def _maybe_gate(self, key: object) -> None:
        """Park the calling thread on its per-thread gate for the target key."""
        if key != self.target_key:
            return
        ident = threading.get_ident()
        with self._registry_lock:
            slot = self._slot_by_thread.get(ident)
            if slot is None:
                if len(self._slot_by_thread) >= 2:
                    return
                slot = len(self._slot_by_thread)
                self._slot_by_thread[ident] = slot
            else:
                return
        self.entered_events[slot].set()
        assert self.release_events[slot].wait(timeout=10.0), (
            f"release event {slot} never opened"
        )

    def get(self, key: object, default: Optional[Any] = None) -> Any:
        """Capture the read result, gate, then return the captured value."""
        value = super().get(key, default)
        self._maybe_gate(key)
        return value

    def __contains__(self, key: object) -> bool:
        """Capture the membership result, gate, then return it."""
        result = super().__contains__(key)
        self._maybe_gate(key)
        return result


def test_concurrent_first_use_retains_both_creations_and_disposals() -> None:
    """The audited interleave: two first-use registrations of one many key.

    Choreography:
        1. Thread A reads the missing bucket and parks (post-read).
        2. Thread B starts; on the broken code it also reads the missing
           bucket and parks; on the fixed code it blocks on the store lock.
        3. A is released and completes its registration; then B is released
           and completes its registration.

    Contract assertions:
        - The live bucket retains BOTH creations (broken code kept one).
        - The disposal registry mirrors the live bucket exactly.
        - Cleanup disposes both returned objects exactly once.
    """
    store = Creations(owner_conduit_id="conduit-1", id="conduit-1")
    gated = GatedReadDict("spell-many")
    store._creations = gated
    probe_a = DisposalProbe("a")
    probe_b = DisposalProbe("b")
    errors: List[Exception] = []

    def register(probe: DisposalProbe) -> None:
        """Register one many creation, capturing any failure."""
        try:
            store.add_many_creations(
                "spell-many",
                probe,
                has_disposal_methods=True,
                disposal_methods=["dispose"],
            )
        except Exception as exc:
            errors.append(exc)

    thread_a = threading.Thread(target=register, args=(probe_a,), daemon=True)
    thread_b = threading.Thread(target=register, args=(probe_b,), daemon=True)

    thread_a.start()
    assert gated.entered_events[0].wait(timeout=10.0), (
        "first registrant never reached its bucket read"
    )
    thread_b.start()

    gated.release_events[0].set()
    thread_a.join(timeout=10.0)
    assert not thread_a.is_alive(), "thread A did not finish"

    # On the fixed code B parks at its (lock-serialized) read only now; on
    # the broken code it parked pre-assignment already. Release it either way.
    assert gated.entered_events[1].wait(timeout=10.0), (
        "second registrant never reached its bucket read"
    )
    gated.release_events[1].set()
    thread_b.join(timeout=10.0)
    assert not thread_b.is_alive(), "thread B did not finish"

    assert errors == [], f"registration raised: {errors!r}"
    bucket = store._creations["spell-many"]
    assert sorted(entry.label for entry in bucket) == ["a", "b"], (
        "a successfully returned creation escaped lifetime storage "
        "(the audited BUG-073 loss)"
    )
    disposal_bucket = store._disposable_creations["spell-many"]
    assert len(disposal_bucket) == len(bucket) == 2, (
        "disposal tracking does not mirror the live bucket"
    )

    store.cleanup()
    assert probe_a.dispose_calls == 1
    assert probe_b.dispose_calls == 1


def test_sequential_many_registrations_preserve_order_and_metadata() -> None:
    """Behavior guard: the healthy sequential lane is unchanged.

    Contract assertions:
        - Repeated registrations append in order to one bucket.
        - Disposal metadata is recorded only for disposal-declaring entries.
    """
    store = Creations(owner_conduit_id="conduit-1", id="conduit-1")
    probe = DisposalProbe("tracked")
    plain = object()

    store.add_many_creations(
        "spell-seq", probe,
        has_disposal_methods=True, disposal_methods=["dispose"],
    )
    store.add_many_creations("spell-seq", plain)

    bucket = store._creations["spell-seq"]
    assert bucket == [probe, plain]
    disposal_bucket = store._disposable_creations["spell-seq"]
    assert len(disposal_bucket) == 1
    assert disposal_bucket[0][0] is probe

    store.cleanup()
    assert probe.dispose_calls == 1
