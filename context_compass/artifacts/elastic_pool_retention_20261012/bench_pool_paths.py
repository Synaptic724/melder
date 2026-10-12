"""
Micro-benchmark: the kernel pools' own acquire/return paths, single thread, in ns per cycle.

Run once per tree (PYTHONPATH=<tree>/src). Measures:
  - lesser cycle: `root.create_lesser_conduit()` + `cleanup()` (the gauntlet's outer scope, no melds);
  - spellspace cycle: `with root.enter_spellspace(): pass`;
  - raw ConduitPool take + return with N shells idle (N=5: within baseline; N=40: the elastic band, which on
    the candidate reads the clock and returns early, and on the base would trim to 20 - so N=40 runs only
    where the pool can keep 40);
  - raw SpellSpacePool acquire_untracked + release with N spaces idle (same N values).
Each figure is the median of 9 repeats of 100,000 cycles.

Usage: PYTHONPATH=<tree>/src python -X gil=0 bench_pool_paths.py <label>
"""
import json
import statistics
import sys
import time
from typing import Any, Callable, Dict, List

from melder import Spellbook


def timed(cycle: Callable[[], None], loops: int = 100_000, repeats: int = 9) -> float:
    """Return the median ns per call of `cycle` over `repeats` runs of `loops` calls."""
    results: List[float] = []
    for _ in range(repeats):
        t0 = time.perf_counter_ns()
        for _ in range(loops):
            cycle()
        results.append((time.perf_counter_ns() - t0) / loops)
    return statistics.median(results)


def preload(take: Callable[[], Any], give: Callable[[Any], None], count: int) -> None:
    """Leave `count` objects idle in the pool by taking that many at once and returning them."""
    held = [take() for _ in range(count)]
    for obj in held:
        give(obj)


def main() -> int:
    """Run the four measurements and print one JSON line."""
    label = sys.argv[1]
    book = Spellbook()
    root = book.conjure(name="pool_path_bench")
    out: Dict[str, Any] = {"label": label}
    try:
        def lesser_cycle() -> None:
            root.create_lesser_conduit().cleanup()

        def space_cycle() -> None:
            with root.enter_spellspace():
                pass

        out["lesser_cycle_ns"] = round(timed(lesser_cycle, loops=50_000), 1)
        out["spellspace_cycle_ns"] = round(timed(space_cycle), 1)

        conduits = root._conduit_pool
        spaces = root._spellspace_pool
        out["max_idle"] = conduits.max_idle
        for idle in (5, 40):
            if idle > conduits.max_idle:
                continue
            preload(root.create_lesser_conduit, lambda lesser: lesser.cleanup(), idle)
            take, give = conduits.create_object, conduits.return_lesser_conduit

            def raw_conduit() -> None:
                give(take())

            out[f"raw_conduit_idle{idle}_ns"] = round(timed(raw_conduit), 1)
            out[f"conduit_pool_idle_after_{idle}"] = conduits.idle_count
            preload(spaces.acquire_untracked, spaces.release, idle)
            acquire, release = spaces.acquire_untracked, spaces.release

            def raw_space() -> None:
                release(acquire())

            out[f"raw_space_idle{idle}_ns"] = round(timed(raw_space), 1)
            out[f"space_pool_idle_after_{idle}"] = spaces.idle_count
    finally:
        root.permanent_cleanup()
    sys.stdout.write(json.dumps(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
