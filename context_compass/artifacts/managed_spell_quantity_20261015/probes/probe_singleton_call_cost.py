"""S4: the cost of the singleton call itself - `ReleaseManagedSpell()` against `Aether()`, the shape it copies.

Run: python -X gil=0|1 probe_singleton_call_cost.py [calls] [rounds]
"""
import statistics
import sys
import time

import melder  # importing the package boots Aether, which builds ReleaseManagedSpell
from melder import ReleaseManagedSpell
from melder.aether.aether import Aether


def bench(factory: type, calls: int, rounds: int) -> tuple:
    """Return (min, median) ns per call of `factory()` over `rounds` loops of `calls` calls."""
    samples = []
    for _ in range(rounds):
        start = time.perf_counter_ns()
        for _ in range(calls):
            factory()
        samples.append((time.perf_counter_ns() - start) / calls)
    return min(samples), statistics.median(samples)


def main() -> None:
    calls = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    gil = "enabled" if sys._is_gil_enabled() else "disabled"
    print(f"python {sys.version.split()[0]} gil={gil} melder={melder.__version__} calls={calls} rounds={rounds}")
    for factory in (Aether, ReleaseManagedSpell, Aether, ReleaseManagedSpell):
        low, mid = bench(factory, calls, rounds)
        print(f"{factory.__name__ + '()':22s} min {low:6.1f} ns  median {mid:6.1f} ns")


if __name__ == "__main__":
    main()
