"""S4 routing-cost probe: `ReleaseManagedSpell().release(obj)` against the pool's own `put_back(obj)`.

Each cycle gives one object back and takes it out again with `_idle.pop()` (the lease S5 emits inline), so the pool
stays at one idle object and never rebalances. Arms, interleaved per round to spread drift:
  A  pool.put_back(obj)                  - the pool call itself
  B  registry.release(obj)               - the singleton bound once, then the class-keyed fast path
  C  ReleaseManagedSpell().release(obj)  - the documented call shape, singleton lookup included
B - A and C - A are the routing costs. Run: python -X gil=0|1 probe_release_routing_cost.py [cycles] [rounds]
"""
import statistics
import sys
import time

import melder  # importing the package boots Aether, which builds ReleaseManagedSpell
from melder import Existence, ReleaseManagedSpell, Spellbook


class Worker:
    """A resetless managed class."""

    def __init__(self) -> None:
        self.value = 0


def main() -> None:
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    book = Spellbook()
    book.bind(spell=Worker, existence=Existence.managed_spell_quantity, permissions="create")
    root = book.conjure(name="probe_root")
    registry = ReleaseManagedSpell()
    pools = registry._pools_by_class[Worker]
    assert len(pools) == 1
    pool = pools[0]
    pop = pool._idle.pop
    obj = Worker()

    def arm_a() -> float:
        put_back = pool.put_back
        start = time.perf_counter_ns()
        for _ in range(cycles):
            put_back(obj)
            pop()
        return (time.perf_counter_ns() - start) / cycles

    def arm_b() -> float:
        release = registry.release
        start = time.perf_counter_ns()
        for _ in range(cycles):
            release(obj)
            pop()
        return (time.perf_counter_ns() - start) / cycles

    def arm_c() -> float:
        start = time.perf_counter_ns()
        for _ in range(cycles):
            ReleaseManagedSpell().release(obj)
            pop()
        return (time.perf_counter_ns() - start) / cycles

    for arm in (arm_a, arm_b, arm_c):
        arm()  # warm
    results = {"A put_back": [], "B registry.release": [], "C ReleaseManagedSpell().release": []}
    for _ in range(rounds):
        results["A put_back"].append(arm_a())
        results["B registry.release"].append(arm_b())
        results["C ReleaseManagedSpell().release"].append(arm_c())
    gil = "unknown"
    if hasattr(sys, "_is_gil_enabled"):
        gil = "enabled" if sys._is_gil_enabled() else "disabled"
    print(f"python {sys.version.split()[0]} gil={gil} melder={melder.__version__} cycles={cycles} rounds={rounds}")
    base_min = min(results["A put_back"])
    base_med = statistics.median(results["A put_back"])
    for name, values in results.items():
        low, mid = min(values), statistics.median(values)
        print(f"{name:34s} min {low:7.1f} ns  median {mid:7.1f} ns  routing +{low - base_min:6.1f} (min) "
              f"+{mid - base_med:6.1f} (median)")
    root.cleanup()
    book.cleanup()


if __name__ == "__main__":
    main()
