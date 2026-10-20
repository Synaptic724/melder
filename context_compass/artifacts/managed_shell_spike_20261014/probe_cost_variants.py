"""Probe A2: the warm dispense+release cycle, locked (A) vs lock-free warm path (B), 1 and 4 threads."""
import gc
import os
import statistics
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import managed_shell as ms


class Logger:
    def __init__(self) -> None:
        self.lines = ["x"]

    def reset(self) -> None:
        self.lines.clear()

    def close(self) -> None:
        pass


def measure(label: str, lockfree: bool) -> None:
    ms.LOCKFREE_WARM = lockfree
    ms.ReleaseManagedSpell.reset_for_tests()
    sh = ms.ManagedShell("logger", ms.ManagedQuantity.elastic(), ["reset"], ["close"])
    ms.ReleaseManagedSpell.register(Logger, sh)
    build = lambda: (Logger(), [])
    first = ms.ReleaseManagedSpell.dispense(sh, build)
    ms.ReleaseManagedSpell.release(first)
    acquire = sh.acquire
    release = ms.ReleaseManagedSpell.release
    def cycle():
        release(acquire())
    for _ in range(20000):
        cycle()
    gc.disable()
    try:
        samples = []
        for _ in range(7):
            t0 = time.perf_counter_ns()
            for _ in range(50000):
                cycle()
            samples.append((time.perf_counter_ns() - t0) / 50000)
        # 4 threads, each with its own object in flight (4 objects idle at the start)
        objs = [ms.ReleaseManagedSpell.dispense(sh, build) for _ in range(4)]
        for o in objs:
            release(o)
        def threaded():
            for _ in range(50000):
                cycle()
        t0 = time.perf_counter_ns()
        ts = [threading.Thread(target=threaded) for _ in range(4)]
        [t.start() for t in ts]; [t.join() for t in ts]
        four = (time.perf_counter_ns() - t0) / 200000
    finally:
        gc.enable()
    print(f"{label}: cycle median {statistics.median(samples):.0f} ns (min {min(samples):.0f}) single thread; "
          f"{four:.0f} ns per cycle amortized over 4 threads; {sh.describe()}")
    # stress check for B: limited never exceeds N under threads (count is cold-path only)
    sh2 = ms.ManagedShell("lim", ms.ManagedQuantity.limited_quantity(3), ["reset"], ["close"])
    ms.ReleaseManagedSpell.register(Logger, sh2)
    peak = [0]; lk = threading.Lock(); exhausted = [0]
    def worker():
        for _ in range(3000):
            try:
                o = ms.ReleaseManagedSpell.dispense(sh2, build)
            except ms.ManagedQuantityExhausted:
                exhausted[0] += 1
                continue
            with lk:
                peak[0] = max(peak[0], sh2.describe()["count"])
            ms.ReleaseManagedSpell.release(o)
    ts = [threading.Thread(target=worker) for _ in range(8)]
    [t.start() for t in ts]; [t.join() for t in ts]
    print(f"   limited(3) under 8 threads: peak count {peak[0]}, exhausted {exhausted[0]}, {sh2.describe()}")


for _ in range(2):
    measure("A locked warm path", False)
    measure("B lock-free warm path", True)
