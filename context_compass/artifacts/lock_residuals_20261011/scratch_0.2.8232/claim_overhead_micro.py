"""Isolated cost of the work 0.2.8232 adds to one cleanup_spell: a set probe and add inside a held RLock, and one more
RLock section that discards the id (python -X gil=0 claim_overhead_micro.py)."""
import sys
import threading
import time

lock = threading.RLock()
marks: set = set()
spell_id = "e65dacd29e5b1c340d3a4a1781adaeaa03e0fdda9f7549dc86cfd139f86731d2"
n = 1_000_000


def added() -> None:
    with lock:
        if spell_id in marks:
            raise RuntimeError
        marks.add(spell_id)
    try:
        pass
    finally:
        with lock:
            marks.discard(spell_id)


def baseline() -> None:
    with lock:
        pass


for name, call in (("baseline (one RLock section)", baseline), ("with the claim", added)):
    best = None
    for _ in range(5):
        start = time.perf_counter_ns()
        for _ in range(n):
            call()
        per = (time.perf_counter_ns() - start) / n
        best = per if best is None else min(best, per)
    print(f"gil={sys._is_gil_enabled()} {name:30s} {best:6.1f} ns per call")
