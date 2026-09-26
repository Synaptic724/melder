"""
Before/after overhead benchmark for creation slot guards (task-owned artifact).

Run from a source copy: PYTHONPATH=src python slot_guard_bench.py <label> <out.json>
Each scenario uses trivial constructors, which is the WORST case for relative
locking overhead (no user work to hide it). Reports ns per operation.
"""

import json
import statistics
import sys
import threading
import time
from typing import Callable, Dict, List

from melder.aether.spellbook.spellbook import Spellbook


class LeafA:
    """Trivial dependency."""


class LeafB:
    """Trivial dependency."""


class LeafC:
    """Trivial dependency."""


class PerConduitRoot:
    """unique_per_conduit root with three unique_per_conduit dependencies."""

    def __init__(self, a: LeafA, b: LeafB, c: LeafC) -> None:
        self.a = a
        self.b = b
        self.c = c


class SpaceA:
    """Trivial space-scoped dependency."""


class SpaceB:
    """Trivial space-scoped dependency."""


class SpaceC:
    """Trivial space-scoped dependency."""


class SpaceRoot:
    """unique_per_spell_space root with three space-scoped dependencies."""

    def __init__(self, a: SpaceA, b: SpaceB, c: SpaceC) -> None:
        self.a = a
        self.b = b
        self.c = c


class UniqueService:
    """unique root with no dependencies (purge/rebuild cycle)."""


class ManyA:
    """Transient dependency."""


class ManyRoot:
    """many root with one many dependency (control: no slot, no guard)."""

    def __init__(self, a: ManyA) -> None:
        self.a = a


def _time(op: Callable[[], None], iterations: int, repeats: int) -> Dict[str, float]:
    for _ in range(min(iterations, 2000)):
        op()
    samples: List[float] = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        for _ in range(iterations):
            op()
        samples.append((time.perf_counter_ns() - start) / iterations)
    return {"min_ns": min(samples), "median_ns": statistics.median(samples)}


def _threaded(op: Callable[[], None], threads: int, iterations: int, repeats: int) -> Dict[str, float]:
    samples: List[float] = []
    for _ in range(repeats):
        barrier = threading.Barrier(threads + 1)

        def worker() -> None:
            barrier.wait()
            for _ in range(iterations):
                op()

        pool = [threading.Thread(target=worker) for _ in range(threads)]
        for thread in pool:
            thread.start()
        barrier.wait()
        start = time.perf_counter_ns()
        for thread in pool:
            thread.join()
        samples.append((time.perf_counter_ns() - start) / (iterations * threads))
    return {"min_ns": min(samples), "median_ns": statistics.median(samples)}


def main() -> None:
    label = sys.argv[1]
    out_path = sys.argv[2]
    book = Spellbook(aetheric_frame="slot-guard-bench")
    for leaf in (LeafA, LeafB, LeafC):
        book.bind(spell=leaf, existence="unique_per_conduit")
    book.bind(spell=PerConduitRoot, existence="unique_per_conduit")
    for leaf in (SpaceA, SpaceB, SpaceC):
        book.bind(spell=leaf, existence="unique_per_spell_space")
    book.bind(spell=SpaceRoot, existence="unique_per_spell_space")
    book.bind(spell=UniqueService, existence="unique")
    book.bind(spell=ManyA, existence="many")
    book.bind(spell=ManyRoot, existence="many")
    root = book.conjure(name="slot-guard-bench-root")
    root.meld(spell=PerConduitRoot)
    root.meld(spell=UniqueService)

    def warm_per_conduit() -> None:
        root.meld(spell=PerConduitRoot)

    def lesser_cycle() -> None:
        lesser = root.create_lesser_conduit()
        lesser.meld(spell=PerConduitRoot)
        lesser.cleanup()

    def space_cycle() -> None:
        with root.enter_spellspace() as space:
            space.meld(spell=SpaceRoot)

    def purge_rebuild_per_conduit() -> None:
        root.purge(spell=PerConduitRoot)
        root.meld(spell=PerConduitRoot)

    def purge_rebuild_unique() -> None:
        root.purge(spell=UniqueService)
        root.meld(spell=UniqueService)

    def many_control() -> None:
        root.meld(spell=ManyRoot)

    results: Dict[str, object] = {
        "label": label,
        "python": sys.version,
        "gil_enabled": sys._is_gil_enabled(),
        "scenarios": {
            "warm_per_conduit_meld": _time(warm_per_conduit, 200_000, 7),
            "many_control_meld": _time(many_control, 100_000, 7),
            "lesser_cycle_4_cold_builds": _time(lesser_cycle, 20_000, 7),
            "spellspace_cycle_4_cold_builds": _time(space_cycle, 50_000, 7),
            "purge_rebuild_per_conduit_root": _time(purge_rebuild_per_conduit, 50_000, 7),
            "purge_rebuild_unique": _time(purge_rebuild_unique, 50_000, 7),
            "threads8_spellspace_cycle": _threaded(space_cycle, 8, 10_000, 5),
            "threads8_lesser_cycle": _threaded(lesser_cycle, 8, 3_000, 5),
        },
    }
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print(json.dumps(results["scenarios"], indent=1))


if __name__ == "__main__":
    main()
