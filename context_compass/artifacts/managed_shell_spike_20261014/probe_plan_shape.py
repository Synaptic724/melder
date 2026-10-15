"""
Probe B: a managed site inside a REAL emitted plan, and the door shapes, on the 0.2.8238 working copy.

The harness (codegen_strategy_certification) captures the normal plan of the worker shape - Manager (unique,
disposal) -> Worker (many, disposal) - as the lowering emits it. This probe executes that body unchanged (plain),
then a transformed body whose Manager site reads a ManagedShell instead of the owner store:

    v0 = c0._creations.get(sid0)          ->      v0 = sh0.acquire()
    if v0 is None:                                if v0 is None:
        v0 = _miss0(meld, c0)                         v0 = _mdispense0(meld, sh0)

and times one creation of a Worker: plain (no release owed) against managed plus the release the user owes
(through ReleaseManagedSpell, and through the shell that dispensed it). Then the door shapes alone.
RUN: python -X gil=0 probe_plan_shape.py   (cwd $HOME/work/pgo_run, PYTHONPATH src:repo:tests/experimentation)
"""
import gc
import os
import statistics
import sys
import threading
import time
from typing import Any, Callable, Dict, List, Tuple

import codegen_strategy_certification as cert  # the harness: patches SitePlanLowering.emit to capture plans

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import managed_shell as ms

SITE_OLD = "    v0 = c0._creations.get(sid0)\n    if v0 is None:\n        v0 = _miss0(meld, c0)\n"
SITE_NEW = "    v0 = sh0.acquire()\n    if v0 is None:\n        v0 = _mdispense0(meld, sh0)\n"
MISS_NEW = (
    "def _mdispense0(meld, sh0):\n"
    "    try:\n"
    "        entry = sh0.reserve()\n"
    "    except _ServedFromIdle as served:\n"
    "        return served.item\n"
    "    try:\n"
    "        v0 = t0()\n"
    "    except Exception as exc:\n"
    "        sh0.cancel(entry)\n"
    "        _raise_meld_construction_error(spells[0], exc)\n"
    "    sh0.publish_out(entry, v0, [])\n"
    "    return v0\n"
)


def timed(fn: Callable[[], object], n: int, reps: int, warm: int, between: Callable[[], None]) -> float:
    for _ in range(warm):
        fn()
    between()
    samples: List[float] = []
    for _ in range(reps):
        t0 = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - t0) / n)
        between()
    return statistics.median(samples)


def main() -> int:
    ms.LOCKFREE_WARM = False
    ms.ReleaseManagedSpell.reset_for_tests()
    shape = cert.shapes()[0]
    cert.captured.clear()
    book, conduit = cert.build_world(shape, "probe-b")
    lines: List[str] = []
    try:
        assert type(conduit.meld("Worker")) is shape.root
        root_id = None
        for sid, (_src, ns) in cert.captured.items():
            if any(s.spell is shape.root and s.spell_id == ns.get("root_spell_id") for s in ns.get("spells", ())):
                root_id = sid
        source, namespace = cert.captured[root_id]
        assert source.count(SITE_OLD) == 1, source
        managed_src = MISS_NEW + source.replace(SITE_OLD, SITE_NEW)
        meld = conduit._meld
        manager_cls = namespace["t0"]
        sh0 = ms.ManagedShell(namespace["sid0"], ms.ManagedQuantity.elastic(), [], ["cleanup"])
        ms.ReleaseManagedSpell.register(manager_cls, sh0)
        plain = cert.compile_variant(source, namespace, {}, "plain")
        managed = cert.compile_variant(managed_src, namespace, {"sh0": sh0, "_ServedFromIdle": ms._ServedFromIdle}, "managed")
        store = meld._conduit_creations
        release = ms.ReleaseManagedSpell.release

        def drain() -> None:
            for key, bucket in list(store._creations.items()):
                if isinstance(bucket, list):
                    bucket.clear()
            for key, bucket in list(store._disposable_creations.items()):
                if isinstance(bucket, list):
                    bucket.clear()
                elif hasattr(bucket, "entries") and isinstance(bucket.entries, list):
                    bucket.entries.clear()

        def plain_cycle() -> object:
            return plain(meld)

        def managed_cycle_singleton() -> object:
            w = managed(meld)
            release(w.d0)
            return w

        def managed_cycle_shell() -> object:
            w = managed(meld)
            m = w.d0
            sh0.put_back(m, sh0._out[id(m)])
            return w

        w = managed(meld)
        assert type(w) is shape.root and type(w.d0) is manager_cls and sh0.describe()["out"] == 1
        release(w.d0)
        assert sh0.describe() == {"mode": "elastic", "count": 1, "idle": 1, "out": 0, "dead_pending": 0}
        gc.disable()
        try:
            for label, fn in (("plain plan (unique site)", plain_cycle),
                              ("managed plan + ReleaseManagedSpell.release", managed_cycle_singleton),
                              ("managed plan + release through the shell", managed_cycle_shell)):
                ns_per = timed(fn, 40000, 5, 10000, drain)
                py, c = cert.call_counts(fn)
                drain()
                lines.append(f"{label}: {ns_per:.0f} ns per Worker creation; py calls {py}, C calls {c}")
            # 4 threads, four idle managers, each thread cycling the managed plan + singleton release
            for _ in range(4):
                objs = [managed(meld) for _ in range(4)]
                for o in objs:
                    release(o.d0)
            assert sh0.describe()["idle"] == 4, sh0.describe()

            def worker(n: int = 30000) -> None:
                for _ in range(n):
                    w = managed(meld)
                    release(w.d0)

            t0 = time.perf_counter_ns()
            ts = [threading.Thread(target=worker) for _ in range(4)]
            [t.start() for t in ts]
            [t.join() for t in ts]
            four = (time.perf_counter_ns() - t0) / 120000
            drain()
            lines.append(f"managed plan + singleton release, 4 threads x 30k: {four:.0f} ns per Worker creation amortized; "
                         f"shell {sh0.describe()}")

            def plain_worker(n: int = 30000) -> None:
                for _ in range(n):
                    plain(meld)

            t0 = time.perf_counter_ns()
            ts = [threading.Thread(target=plain_worker) for _ in range(4)]
            [t.start() for t in ts]
            [t.join() for t in ts]
            four_plain = (time.perf_counter_ns() - t0) / 120000
            drain()
            lines.append(f"plain plan, 4 threads x 30k: {four_plain:.0f} ns per Worker creation amortized")
            # door shapes alone
            c0, sid0 = namespace["c0"], namespace["sid0"]
            idle_manager = sh0.acquire()
            release(idle_manager)

            def store_read() -> object:
                return c0._creations.get(sid0)

            def shell_cycle() -> object:
                m = sh0.acquire()
                sh0.put_back(m, sh0._out[id(m)])
                return m

            def singleton_cycle() -> object:
                m = sh0.acquire()
                release(m)
                return m

            def build_only() -> object:
                return manager_cls()

            def whole_meld() -> object:
                return conduit.meld("Worker")

            for label, fn in (("door: owner-store read c0._creations.get(sid0)", store_read),
                              ("door: sh0.acquire() + put_back through the shell", shell_cycle),
                              ("door: sh0.acquire() + ReleaseManagedSpell.release", singleton_cycle),
                              ("reference: Manager() construction alone", build_only),
                              ("reference: conduit.meld(\"Worker\") whole, plain world", whole_meld)):
                ns_per = timed(fn, 40000, 5, 10000, drain)
                lines.append(f"{label}: {ns_per:.0f} ns")
        finally:
            gc.enable()
        errors = sh0.destroy_all()
        lines.append(f"destroy_all: {len(errors)} errors; shell {sh0.describe()}")
        ms.ReleaseManagedSpell.unregister(manager_cls, sh0)
    finally:
        conduit.cleanup()
        book.cleanup()
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
