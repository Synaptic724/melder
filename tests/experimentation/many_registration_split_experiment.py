"""
Many-registration split: what one disposal-bearing `many` creation pays to register, and what a trim would leave.

WHY THIS EXISTS
    On a real application's creation cache (commandops, 2026-09-27) the only plans that run per meld are four
    `many` roots, and every one of them registers for disposal on each creation. Measured live, that registration
    is the largest item of the meld (Worker 853 ns vs 251 without disposal). This file prices the pieces against a
    real `Creations` store so a trim can be judged before it is designed:

    today          `store.add_many_creations(sid, item, has_disposal_methods=True, disposal_methods=dm)` exactly as
                   the plan emits it (bound method, two keyword arguments); and the same call without disposal
    lock only      the `RLock` enter/exit the store takes, and a plain `Lock` for comparison
    trimmed A      per-key disposal methods recorded once, the `RLock` kept, ONE list append per creation
    trimmed B      the same bucket, first use double-checked under the lock, then a lock-free `list.append`

    Trimmed A and B are stand-ins written here, not store code: they show the floor of the two shapes, they do not
    settle the cleaned-store refusal for a lock-free append (an open design question, recorded in the ticket).

RUN (3.14t target)
    python -X gil=0 tests/experimentation/many_registration_split_experiment.py
"""

import statistics
import threading
import time
from typing import Callable, Dict, List, Tuple

from melder.aether.conduit.creations.creations import Creations


class _Item:
    """A creation with one disposal method, as the commandops workers have."""

    def __init__(self) -> None:
        self.state: int = 0

    def cleanup(self) -> None:
        """Disposal method named by the spell."""
        self.state = -1


class TrimmedA:
    """Per-key disposal methods recorded once; the store lock kept; one append per creation."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cleaned: bool = False
        self._many: Dict[str, List[object]] = {}
        self._methods: Dict[str, List[str]] = {}

    def add_many(self, key: str, item: object, methods: List[str]) -> None:
        """Register one creation under the lock; the methods list is stored on first use only."""
        with self._lock:
            bucket = self._many.get(key)
            if bucket is None:
                bucket = self._many[key] = []
                self._methods[key] = methods
            bucket.append(item)


class TrimmedB:
    """First use double-checked under the lock, then a lock-free append into the existing bucket."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cleaned: bool = False
        self._many: Dict[str, List[object]] = {}
        self._methods: Dict[str, List[str]] = {}

    def add_many(self, key: str, item: object, methods: List[str]) -> None:
        """Append lock-free once the bucket exists; create it under the lock the first time."""
        bucket = self._many.get(key)
        if bucket is None:
            with self._lock:
                bucket = self._many.get(key)
                if bucket is None:
                    bucket = self._many[key] = []
                    self._methods[key] = methods
        bucket.append(item)


def time_ns(fn: Callable[[], None], n: int = 200000, reps: int = 5, warm: int = 20000) -> float:
    """Median ns per call of `fn` over `reps` batches of `n` calls after `warm` warm-up calls."""
    for _ in range(warm):
        fn()
    samples: List[float] = []
    for _ in range(reps):
        start = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - start) / n)
    return statistics.median(samples)


def main() -> None:
    """Print the registration price table."""
    methods = ["cleanup"]
    sid = "a" * 64
    rows: List[Tuple[str, float]] = []

    store = Creations(owner_conduit_id="c", id="s")
    item = _Item()
    rows.append(("today: add_many_creations(sid, item, has_disposal_methods=True, disposal_methods=dm)",
                 time_ns(lambda: store.add_many_creations(sid, item, has_disposal_methods=True, disposal_methods=methods))))
    store2 = Creations(owner_conduit_id="c", id="s2")
    rows.append(("today: add_many_creations(sid, item) (no disposal)",
                 time_ns(lambda: store2.add_many_creations(sid, item))))
    store3 = Creations(owner_conduit_id="c", id="s3")
    rows.append(("today: _append_many_locked direct, no lock, disposal (the dict/list work alone)",
                 time_ns(lambda: store3._append_many_locked(sid, item, has_disposal_methods=True, disposal_methods=methods))))
    rlock = threading.RLock()
    lock = threading.Lock()

    def take_rlock() -> None:
        with rlock:
            pass

    def take_lock() -> None:
        with lock:
            pass

    rows.append(("RLock enter/exit alone", time_ns(take_rlock)))
    rows.append(("Lock enter/exit alone", time_ns(take_lock)))
    trimmed_a = TrimmedA()
    rows.append(("trimmed A: per-key methods, RLock kept, one append", time_ns(lambda: trimmed_a.add_many(sid, item, methods))))
    trimmed_b = TrimmedB()
    rows.append(("trimmed B: double-checked first use, lock-free append after", time_ns(lambda: trimmed_b.add_many(sid, item, methods))))
    bucket: List[object] = []
    rows.append(("list.append alone", time_ns(lambda: bucket.append(item))))

    print("| registration shape | ns per creation (VM) |")
    print("| --- | ---: |")
    for label, ns in rows:
        print(f"| {label} | {ns:.0f} |")
    # the lists grow to millions of entries during the run; release them explicitly
    store.cleanup()
    store2.cleanup()
    store3.cleanup()


if __name__ == "__main__":
    main()
