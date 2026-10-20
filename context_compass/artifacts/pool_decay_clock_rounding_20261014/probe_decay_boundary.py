"""
Replays test_quiet_root_pool_decays_to_baseline_and_burst_restretches against the real AbstractElasticPool for many
fake-clock origins and counts the origins at which each of its assertions would fail.

The pool is built the way the kernel pools are (baseline 20, max 256, default settle 1800 s, 10% decay every 600 s,
stretch 0) on a clock reading taken just before the fake clock's origin, as the root's ConduitPool is in the test.
The test's sequence, as pool operations: a burst of 40 (40 misses, 40 returns); advance `settle - 1.0` and cycle
(target 40); advance `1.0` and cycle (target 36, idle 36, 4 destroyed); advance `interval` and cycle (32); advance
ten hours and cycle (20), four more cycles (idle 20); a burst of 40 (target 40, idle 40).

Variants:
  real_two_adds   - origin = a real-valued reading (as the test does today), two additions to the settle time
  real_one_add    - same origin, one addition `origin + settle` (shows the two additions are not the only hazard)
  whole_two_adds  - origin = math.ceil(reading) (the fix), the test's own two additions

Run: PYTHONPATH=<repo>/src python probe_decay_boundary.py [origins]
"""
import math
import random
import sys
from typing import Callable, Dict, List

from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool


class _Shell:
    """Stand-in pooled object that records its destruction."""

    __slots__ = ["destroyed"]

    def __init__(self) -> None:
        self.destroyed = False


class _ShellPool(AbstractElasticPool[_Shell]):
    """Minimal concrete pool: builds shells and marks them destroyed."""

    __slots__: List[str] = []

    def create_object(self, *args: object, **kwargs: object) -> _Shell:
        return _Shell()

    def destroy_object(self, obj: _Shell) -> None:
        obj.destroyed = True


class _Clock:
    """Hand-advanced clock."""

    __slots__ = ["value"]

    def __init__(self, value: float) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


def _replay(origin: float, construction_reading: float, one_add: bool) -> List[str]:
    """Run the test's sequence; return the names of the assertions that fail."""
    failures: List[str] = []
    construction_clock = _Clock(construction_reading)
    pool = _ShellPool(baseline_idle=20, max_idle=256, time_func=construction_clock)
    clock = _Clock(origin)
    pool._time_func = clock
    held = [pool.acquire() for _ in range(40)]
    for shell in held:
        pool.release(shell)
    settle = pool.describe()["settle_time_seconds"]
    interval = pool.describe()["decay_interval_seconds"]

    def cycle() -> None:
        pool.release(pool.acquire())

    clock.value += settle - 1.0
    cycle()
    if pool.target_idle != 40:
        failures.append("before_settle_target_40")
    if one_add:
        clock.value = origin + settle
    else:
        clock.value += 1.0
    cycle()
    if pool.target_idle != 36:
        failures.append("at_settle_target_36")
    if pool.idle_count != 36:
        failures.append("at_settle_idle_36")
    if sum(1 for shell in held if shell.destroyed) != 4:
        failures.append("at_settle_destroyed_4")
    clock.value += interval
    cycle()
    if pool.target_idle != 32:
        failures.append("next_interval_target_32")
    clock.value += 10 * 3600.0
    cycle()
    if pool.target_idle != 20:
        failures.append("long_quiet_target_20")
    for _ in range(4):
        cycle()
    if pool.idle_count != 20:
        failures.append("long_quiet_idle_20")
    burst = [pool.acquire() for _ in range(40)]
    for shell in burst:
        pool.release(shell)
    if pool.target_idle != 40 or pool.idle_count != 40:
        failures.append("restretch_40")
    pool.cleanup()
    return failures


def main() -> int:
    origins = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    random.seed(20261014)
    variants: Dict[str, Callable[[float], float]] = {
        "real_two_adds": lambda reading: reading,
        "real_one_add": lambda reading: reading,
        "whole_two_adds": lambda reading: float(math.ceil(reading)),
    }
    for name, make_origin in variants.items():
        failed_origins = 0
        by_assertion: Dict[str, int] = {}
        for _ in range(origins):
            # Monotonic readings of a machine up from minutes to about a month.
            reading = random.uniform(60.0, 3.0e6)
            construction_reading = reading - random.uniform(0.0, 0.5)
            failures = _replay(make_origin(reading), construction_reading, one_add=(name == "real_one_add"))
            if failures:
                failed_origins += 1
                for failure in failures:
                    by_assertion[failure] = by_assertion.get(failure, 0) + 1
        print(f"{name}: failing origins {failed_origins}/{origins} = {failed_origins / origins:.4f} {by_assertion}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
