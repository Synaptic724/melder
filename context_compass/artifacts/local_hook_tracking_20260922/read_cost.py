"""Measure scalar hook-state read patterns; no Melder code is imported or modified."""

from statistics import median
from threading import RLock
from timeit import repeat
import json
import sys


class HookReadCost:
    """Own minimal state matching the proposed hook flag/map/lock read choices."""

    __slots__ = ("modified", "hooks", "lock")

    def __init__(self) -> None:
        """Create false/empty hook state and one uncontended reentrant mutex."""
        self.modified = False
        self.hooks: dict[str, tuple[object, ...]] = {}
        self.lock = RLock()

    def read_flag(self) -> bool:
        """Return the scalar without lock acquisition."""
        return self.modified

    def read_empty(self) -> bool:
        """Read map emptiness through an ordinary conditional."""
        if self.hooks:
            return True
        return False

    def read_count(self) -> bool:
        """Compare the O(1) dictionary length with zero."""
        return len(self.hooks) > 0

    def read_locked(self) -> bool:
        """Acquire and release the same mutex around the scalar read."""
        with self.lock:
            return self.modified

    def read_checked_then_locked(self) -> bool:
        """Skip the mutex on the no-change branch; recheck if modified."""
        if not self.modified:
            return False
        with self.lock:
            return self.modified


def main() -> None:
    """Emit repeated per-call timings; includes method overhead and no contention."""
    state = HookReadCost()
    repetitions = 7
    iterations = 1_000_000
    scenarios = {
        "flag": state.read_flag,
        "dict_empty": state.read_empty,
        "dict_len": state.read_count,
        "uncontended_rlock": state.read_locked,
        "flag_false_skips_lock": state.read_checked_then_locked,
    }
    results: dict[str, object] = {}
    for name, callback in scenarios.items():
        samples = repeat(callback, number=iterations, repeat=repetitions)
        results[name] = {
            "median_ns_per_call": median(samples) * 1e9 / iterations,
            "min_ns_per_call": min(samples) * 1e9 / iterations,
        }
    payload = {
        "python": sys.version,
        "gil_enabled": sys._is_gil_enabled(),
        "iterations_per_repeat": iterations,
        "repeats": repetitions,
        "results": results,
    }
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")


if __name__ == "__main__":
    main()
