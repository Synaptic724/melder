"""Probe B2: the warm door cycle (acquire + the two releases) per mode, locked shell, one idle object."""
import gc
import os
import statistics
import sys
import time
from typing import Callable, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import managed_shell as ms


class Thing:
    def __init__(self) -> None:
        self.state = 0

    def reset(self) -> None:
        self.state = 0

    def close(self) -> None:
        self.state = -1


def timed(fn: Callable[[], object], n: int = 40000, reps: int = 5, warm: int = 10000) -> float:
    for _ in range(warm):
        fn()
    samples: List[float] = []
    for _ in range(reps):
        t0 = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - t0) / n)
    return statistics.median(samples)


def main() -> int:
    ms.LOCKFREE_WARM = False
    release = ms.ReleaseManagedSpell.release
    gc.disable()
    try:
        for label, quantity, reset in (
                ("elastic, no reset", ms.ManagedQuantity.elastic(), []),
                ("elastic, reset()", ms.ManagedQuantity.elastic(), ["reset"]),
                ("limited_quantity(4), no reset", ms.ManagedQuantity.limited_quantity(4), []),
                ("queue(4, 1.0s), no reset", ms.ManagedQuantity.queue(4, 1.0), [])):
            ms.ReleaseManagedSpell.reset_for_tests()
            sh = ms.ManagedShell("thing", quantity, reset, ["close"])
            ms.ReleaseManagedSpell.register(Thing, sh)
            obj = ms.ReleaseManagedSpell.dispense(sh, lambda: (Thing(), []))
            release(obj)

            def shell_cycle() -> object:
                m = sh.acquire()
                sh.put_back(m, sh._out[id(m)])
                return m

            def singleton_cycle() -> object:
                m = sh.acquire()
                release(m)
                return m

            def with_cycle() -> object:
                with ms.ReleaseManagedSpell.managed(sh.acquire()) as m:
                    return m

            a = timed(shell_cycle)
            b = timed(singleton_cycle)
            c = timed(with_cycle)
            print(f"{label}: acquire+shell put_back {a:.0f} ns; acquire+ReleaseManagedSpell.release {b:.0f} ns; "
                  f"acquire+with managed() {c:.0f} ns; {sh.describe()}")
    finally:
        gc.enable()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
