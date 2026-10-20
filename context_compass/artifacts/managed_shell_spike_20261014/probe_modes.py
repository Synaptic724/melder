"""Probe A: the three modes, the way back, the weak out-record and the destroy paths, under threads."""
import gc
import statistics
import sys
import threading
import time
import weakref

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from managed_shell import (
    ManagedQuantity, ManagedQuantityExhausted, ManagedReleaseError, ManagedShell, ReleaseManagedSpell,
)


class Logger:
    built = 0
    alive = 0

    def __init__(self) -> None:
        Logger.built += 1
        Logger.alive += 1
        self.lines = ["hello"]
        self.closed = False

    def reset(self) -> None:
        self.lines.clear()

    def close(self) -> None:
        self.closed = True
        Logger.alive -= 1


class Child:
    disposed = 0

    def close(self) -> None:
        Child.disposed += 1


def build():
    return Logger(), [(Child(), ["close"])]


def shell(quantity, reset=("reset",), disposal=("close",)):
    sh = ManagedShell("logger-id", quantity, list(reset), list(disposal))
    ReleaseManagedSpell.register(Logger, sh)
    return sh


def check(label, cond):
    print(f"{'ok ' if cond else 'FAIL'} {label}")
    return cond


results = []
ReleaseManagedSpell.reset_for_tests()

# --- limited_quantity ---
Logger.built = Logger.alive = 0
sh = shell(ManagedQuantity.limited_quantity(3))
taken = [ReleaseManagedSpell.dispense(sh, build) for _ in range(3)]
try:
    ReleaseManagedSpell.dispense(sh, build)
    results.append(check("limited: 4th dispense raises", False))
except ManagedQuantityExhausted:
    results.append(check("limited: 4th dispense raises", True))
ReleaseManagedSpell.release(taken[0])
again = ReleaseManagedSpell.dispense(sh, build)
results.append(check("limited: a released object is reused, not rebuilt", again is taken[0] and Logger.built == 3))
results.append(check("limited: reset ran on release", taken[0].lines == []))
try:
    ReleaseManagedSpell.release(taken[1]); ReleaseManagedSpell.release(taken[1])
    results.append(check("double release raises", False))
except ManagedReleaseError:
    results.append(check("double release raises", True))
try:
    ReleaseManagedSpell.release(object())
    results.append(check("foreign release raises", False))
except ManagedReleaseError:
    results.append(check("foreign release raises", True))
with ReleaseManagedSpell.managed(ReleaseManagedSpell.dispense(sh, build)) as lg:
    inside = sh.describe()["out"]
results.append(check("with-statement releases on exit", inside == 3 and sh.describe()["out"] == 2))
# stress: 8 threads, 2000 cycles each, never more than 3 alive
peak = [0]
peak_lock = threading.Lock()
def limited_worker():
    for _ in range(2000):
        try:
            obj = ReleaseManagedSpell.dispense(sh, build)
        except ManagedQuantityExhausted:
            continue
        with peak_lock:
            peak[0] = max(peak[0], sh.describe()["count"])
        ReleaseManagedSpell.release(obj)
threads = [threading.Thread(target=limited_worker) for _ in range(8)]
[t.start() for t in threads]; [t.join() for t in threads]
results.append(check(f"limited: peak count {peak[0]} <= 3 under 8 threads, built {Logger.built}", peak[0] <= 3))
errs = sh.destroy_all()
results.append(check(f"limited: destroy_all disposes everything (alive {Logger.alive}, children {Child.disposed})",
                     Logger.alive == 0 and not errs))

# --- queue ---
ReleaseManagedSpell.reset_for_tests(); Logger.built = Logger.alive = 0; Child.disposed = 0
sh = shell(ManagedQuantity.queue(2, timeout_seconds=0.25))
a = ReleaseManagedSpell.dispense(sh, build); b = ReleaseManagedSpell.dispense(sh, build)
t0 = time.perf_counter()
try:
    ReleaseManagedSpell.dispense(sh, build)
    results.append(check("queue: waits then raises at the timeout", False))
except ManagedQuantityExhausted:
    waited = time.perf_counter() - t0
    results.append(check(f"queue: waits then raises at the timeout ({waited:.2f}s)", 0.2 <= waited < 1.0))
got = []
def waiter():
    got.append(ReleaseManagedSpell.dispense(sh, build))
w = threading.Thread(target=waiter); w.start()
time.sleep(0.05); ReleaseManagedSpell.release(a); w.join(2.0)
results.append(check("queue: a waiter is served by a release (same object, no build)", got and got[0] is a and Logger.built == 2))
sh.destroy_all()

# --- elastic ---
ReleaseManagedSpell.reset_for_tests(); Logger.built = Logger.alive = 0; Child.disposed = 0
sh = shell(ManagedQuantity.elastic(baseline_idle=2, max_idle=4))
leased = [ReleaseManagedSpell.dispense(sh, build) for _ in range(20)]
results.append(check("elastic: 20 concurrent leases build 20", Logger.built == 20 and sh.describe()["out"] == 20))
for obj in leased:
    ReleaseManagedSpell.release(obj)
d = sh.describe()
results.append(check(f"elastic: idle capped at max_idle (idle {d['idle']}, alive {Logger.alive}, children disposed {Child.disposed})",
                     d["idle"] == 4 and Logger.alive == 4 and Child.disposed == 16))
sh.destroy_all()

# --- a lease nobody returns ---
ReleaseManagedSpell.reset_for_tests(); Logger.built = Logger.alive = 0; Child.disposed = 0
sh = shell(ManagedQuantity.limited_quantity(1))
obj = ReleaseManagedSpell.dispense(sh, build)
ref = weakref.ref(obj)
del obj
gc.collect()
d = sh.describe()
results.append(check(f"forgotten lease: object collected ({ref() is None}), place freed (count {d['count']})",
                     ref() is None and d["count"] == 0))
nxt = ReleaseManagedSpell.dispense(sh, build)   # the next verb drains the dead entry: its child is disposed
results.append(check(f"forgotten lease: a new object fits the freed place and the dead child was disposed ({Child.disposed})",
                     Logger.built == 2 and Child.disposed == 1))
sh.destroy_all()

# --- failing reset destroys ---
ReleaseManagedSpell.reset_for_tests(); Logger.built = Logger.alive = 0
class BadReset(Logger):
    def reset(self) -> None:
        raise ValueError("cannot reset")
sh = ManagedShell("bad", ManagedQuantity.limited_quantity(1), ["reset"], ["close"])
ReleaseManagedSpell.register(BadReset, sh)
obj = ReleaseManagedSpell.dispense(sh, lambda: (BadReset(), []))
try:
    ReleaseManagedSpell.release(obj)
    results.append(check("failing reset raises", False))
except ValueError:
    results.append(check(f"failing reset raises, destroys (closed {obj.closed}) and frees the place (count {sh.describe()['count']})",
                         obj.closed and sh.describe()["count"] == 0))

# --- costs ---
ReleaseManagedSpell.reset_for_tests()
sh = shell(ManagedQuantity.elastic())
first = ReleaseManagedSpell.dispense(sh, build); ReleaseManagedSpell.release(first)
def cycle():
    o = ReleaseManagedSpell.dispense(sh, build)
    ReleaseManagedSpell.release(o)
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
finally:
    gc.enable()
single = statistics.median(samples)
# acquire-only and release-only split
acq = []; rel = []
for _ in range(5):
    t0 = time.perf_counter_ns(); o = sh.acquire(); t1 = time.perf_counter_ns()
    ReleaseManagedSpell.release(o); t2 = time.perf_counter_ns()
    acq.append(t1 - t0); rel.append(t2 - t1)
def threaded():
    for _ in range(50000):
        cycle()
t0 = time.perf_counter_ns()
ts = [threading.Thread(target=threaded) for _ in range(4)]
[t.start() for t in ts]; [t.join() for t in ts]
four = (time.perf_counter_ns() - t0) / 200000
print(f"\ncost: dispense+release cycle median {single:.0f} ns single thread "
      f"(acquire ~{statistics.median(acq):.0f} ns, release ~{statistics.median(rel):.0f} ns); "
      f"{four:.0f} ns per cycle amortized over 4 threads x 50k cycles (idle contention); "
      f"shell afterwards: {sh.describe()}")
print("\nALL OK" if all(results) else "\nSOME FAILED")
