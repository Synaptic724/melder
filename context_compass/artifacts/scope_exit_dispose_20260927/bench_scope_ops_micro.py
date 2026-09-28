"""Tight-loop cost of the scope operations the scope-exit change touches, for A/B runs of two trees.

melder_0, 2026-09-27. Same gauntlet world as bench_scope_cycle_steps.py; each operation runs N times in one loop
timed as a whole (timer cost amortized), five repeats, median reported in ns per operation.

Usage: python -X gil=0 bench_scope_ops_micro.py <tree root> [scale]
"""
import statistics
import sys
import threading
import time
from pathlib import Path

assert sys.version_info >= (3, 14), sys.version
ROOT = Path(sys.argv[1]).resolve()
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g

ops = g._build_ops("melder")
ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit, ids = rv["conduit"], rv["spell_ids"]
outer_id, marker_id = ids[g.RequestSession], ids[g.RequestScopeMarker]
pc = time.perf_counter_ns
results = {}


def timed(name, n, body):
    """Run `body(n)` five times and record the median ns per operation."""
    body(max(1, n // 10))
    samples = []
    for _ in range(5):
        t0 = pc(); body(n); samples.append((pc() - t0) / n)
    results[name] = statistics.median(samples)


def space_enter_exit(n):
    """Managed space scope with nothing inside."""
    lesser = conduit.create_lesser_conduit()
    enter = lesser.enter_spellspace
    for _ in range(n):
        with enter():
            pass
    lesser.cleanup()


def space_warm_meld(n):
    """Warm melds of a space-scoped object inside one managed space."""
    lesser = conduit.create_lesser_conduit()
    with lesser.enter_spellspace() as space:
        space.meld(spell_id=marker_id)
        meld = space.meld
        for _ in range(n):
            meld(spell_id=marker_id)
    lesser.cleanup()


def lesser_create_cleanup(n):
    """Lesser acquisition and soft cleanup with nothing inside."""
    create = conduit.create_lesser_conduit
    for _ in range(n):
        create().cleanup()


def lesser_warm_meld(n):
    """Control: warm Conduit.meld on a lesser (a path the change does not touch)."""
    lesser = conduit.create_lesser_conduit()
    lesser.meld(spell_id=outer_id)
    meld = lesser.meld
    for _ in range(n):
        meld(spell_id=outer_id)
    lesser.cleanup()


def body():
    """Measure every operation on one worker thread."""
    timed("space_enter_exit", int(100_000 * SCALE), space_enter_exit)
    timed("space_warm_meld", int(200_000 * SCALE), space_warm_meld)
    timed("lesser_create_cleanup", int(60_000 * SCALE), lesser_create_cleanup)
    timed("lesser_warm_meld(control)", int(200_000 * SCALE), lesser_warm_meld)


t = threading.Thread(target=body)
t.start()
t.join()
print(f"tree={ROOT.name} gil={sys._is_gil_enabled()} " + " ".join(f"{k}={v:.1f}" for k, v in results.items()))
ops.cleanup()
