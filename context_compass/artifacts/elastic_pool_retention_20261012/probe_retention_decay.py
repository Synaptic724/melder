"""
Probe: the root ConduitPool's retained target over time - a burst, a quiet period, decay, a second burst.

Swaps the pool's clock for a fake one (`_time_func`, the same seam the unit tests use) so 30-minute settle and
10-minute decay steps run in milliseconds, and counts lesser builds and destructions. On the base tree the target is
pinned at 20 (baseline 20, max 20); on the candidate it follows the burst and decays back.

Usage: PYTHONPATH=<tree>/src python -X gil=0 probe_retention_decay.py
"""
import sys
import time
from typing import Any, Dict, List

from melder import Spellbook
from melder.aether.conduit.conduit_pool import ConduitPool


class FakeClock:
    """Monotonic clock the probe advances by hand."""

    def __init__(self) -> None:
        """Start at the real monotonic time so the pool's construction-time stamps stay consistent."""
        self.now = time.monotonic()

    def __call__(self) -> float:
        """Return the current fake time."""
        return self.now


def install_counters(counters: Dict[str, int]) -> None:
    """Count lesser builds (pool misses) and destructions."""
    take, destroy = ConduitPool.create_object, ConduitPool.destroy_object

    def counted_take(self: Any) -> Any:
        shell = take(self)
        if shell is None:
            counters["built"] += 1
        return shell

    def counted_destroy(self: Any, obj: Any) -> None:
        counters["destroyed"] += 1
        destroy(self, obj)

    ConduitPool.create_object = counted_take
    ConduitPool.destroy_object = counted_destroy


def report(label: str, pool: Any, counters: Dict[str, int]) -> None:
    """Write the pool's target, idle count and the running build/destroy counts."""
    state = pool.describe()
    sys.stdout.write(f"{label:<44} target={state['target_idle']:>3} idle={state['idle_count']:>3} "
                     f"built={counters['built']:>3} destroyed={counters['destroyed']:>3}\n")


def burst(root: Any, size: int) -> None:
    """Hold `size` lessers at once, then return them all."""
    held: List[Any] = [root.create_lesser_conduit() for _ in range(size)]
    for lesser in held:
        lesser.cleanup()


def one_cycle(root: Any) -> None:
    """One ordinary scope cycle: take one lesser and return it."""
    root.create_lesser_conduit().cleanup()


def main() -> int:
    """Run the timeline and return 0."""
    counters = {"built": 0, "destroyed": 0}
    install_counters(counters)
    book = Spellbook()
    root = book.conjure(name="retention_decay_probe")
    pool = root._conduit_pool
    clock = FakeClock()
    pool._time_func = clock
    try:
        sys.stdout.write(f"settle={pool.describe()['settle_time_seconds']}s "
                         f"decay={pool.describe()['decay_percent_per_interval']}%/"
                         f"{pool.describe()['decay_interval_seconds']}s max={pool.max_idle}\n")
        burst(root, 50)
        report("burst of 50, all returned", pool, counters)
        burst(root, 50)
        report("second burst of 50 (t=0)", pool, counters)
        for minutes in (29, 31, 41, 51):
            clock.now += (minutes * 60) - getattr(main, "_elapsed", 0)
            main._elapsed = minutes * 60
            one_cycle(root)
            report(f"t=+{minutes} min, one scope cycle", pool, counters)
        clock.now += 3 * 3600
        for cycle in range(1, 8):
            one_cycle(root)
            report(f"t=+3h51m, scope cycle {cycle}", pool, counters)
        burst(root, 50)
        report("burst of 50 after the decay", pool, counters)
    finally:
        root.permanent_cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
