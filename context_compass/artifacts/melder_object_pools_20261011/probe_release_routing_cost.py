"""Per-lease routing cost of three ways a released object finds its pool (scratch probe, not repo code)."""
import os
import sys
import threading
import time


class Pool:
    __slots__ = ("out",)

    def __init__(self) -> None:
        self.out = {}


class Managed:
    __slots__ = ("_managed_pool", "_managed_out", "__weakref__")

    def __init__(self) -> None:
        self._managed_pool = None
        self._managed_out = False


def run_baseline(objs, pool, registry, n):
    for i in range(n):
        o = objs[i & 1023]


def run_mixin(objs, pool, registry, n):
    # the pool is written into the object once, when the pool builds it; per lease only an
    # immortal bool flips (hand-out True, release False) and release loads the pool reference
    for o in objs:
        o._managed_pool = pool
    for i in range(n):
        o = objs[i & 1023]
        o._managed_out = True
        p = o._managed_pool
        if not o._managed_out:
            raise RuntimeError("double release")
        o._managed_out = False


def run_class_map(objs, pool, registry, n):
    # registry written only when a pool is created; release reads it by type(obj)
    for i in range(n):
        o = objs[i & 1023]
        pools = registry.get(type(o))
        if pools is None:
            raise RuntimeError("no pool")
        p = pools[0]


def run_identity_map(objs, pool, registry, n):
    # one shared dict: hand-out inserts id(obj), release pops it
    for i in range(n):
        o = objs[i & 1023]
        registry[id(o)] = pool
        p = registry.pop(id(o))


def measure(fn, threads, n, shared_registry):
    pool = Pool()
    barrier = threading.Barrier(threads + 1)
    def worker():
        objs = [Managed() for _ in range(1024)]
        barrier.wait()
        fn(objs, pool, shared_registry, n)
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    barrier.wait()
    start = time.perf_counter_ns()
    for t in ts:
        t.join()
    elapsed = time.perf_counter_ns() - start
    return elapsed / n  # wall ns per lease per thread (threads run concurrently)


def main():
    n = 2_000_000
    gil = sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
    print(f"python {sys.version.split()[0]} gil_enabled={gil} cpus={os.cpu_count()}")
    for threads in (1, os.cpu_count() or 1):
        rows = {}
        for name, fn in (("baseline", run_baseline), ("mixin_field", run_mixin),
                         ("class_map", run_class_map), ("identity_map", run_identity_map)):
            best = None
            for _ in range(5):
                registry = {Managed: (Pool(),)} if name == "class_map" else {}
                v = measure(fn, threads, n, registry)
                best = v if best is None else min(best, v)
            rows[name] = best
        base = rows["baseline"]
        print(f"threads={threads}: " + ", ".join(
            f"{k}={rows[k]:.1f}ns (+{rows[k] - base:.1f})" for k in rows))


main()
