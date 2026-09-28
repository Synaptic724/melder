"""Per-step time inside one Melder request-lane scope cycle, for A/B runs of two trees. melder_0, 2026-09-27.

Adapted from melder_2's probes/probe_steps.py (artifacts/gauntlet_runtime_speed_20260926/): same gauntlet harness,
same steps, a worker thread and no profiler; the tree under test is the first argument instead of a fixed path.

Usage: python -X gil=0 bench_scope_cycle_steps.py <tree root> [lane] [cycles] [mode]
    mode "exit_protocol" (default) drives the managed space with `__enter__`/`__exit__` and the lesser with
    create_lesser_conduit()/cleanup(), exactly as the original probe; mode "with_lesser" (new tree only) drives
    the lesser through `with conduit.enter_lesser_conduit() as lesser:` and reports its exit as lesser_cleanup.
"""
import statistics
import sys
import threading
import time
from pathlib import Path

assert sys.version_info >= (3, 14), sys.version
ROOT = Path(sys.argv[1]).resolve()
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g

lane = sys.argv[2] if len(sys.argv) > 2 else "request"
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
mode = sys.argv[4] if len(sys.argv) > 4 else "exit_protocol"
outer_cls, marker_cls, root_cls, group_cls = {
    "request": (g.RequestSession, g.RequestScopeMarker, g.RequestRoot, g.RequestGroup),
    "worker_a": (g.WorkerASession, g.WorkerAScopeMarker, g.WorkerAJobRoot, g.WorkerAGroup),
    "worker_b": (g.WorkerBSession, g.WorkerBScopeMarker, g.WorkerBJobRoot, g.WorkerBGroup)}[lane]
ops = g._build_ops("melder")
ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit, ids = rv["conduit"], rv["spell_ids"]
names = ["lesser_create", "lesser_meld_1st", "lesser_meld_2nd", "space_enter", "space_meld_marker_1st",
         "space_meld_marker_2nd", "space_meld_outer", "root_meld(variant)", "space_exit", "lesser_cleanup"]
acc = {n: [] for n in names}
pc = time.perf_counter_ns


def body_steps(lesser, v, t0, t1):
    """Run the scope body on one lesser and return the step timings after lesser creation."""
    lesser.meld(spell_id=ids[outer_cls]); t1b = pc(); lesser.meld(spell_id=ids[outer_cls]); t2 = pc()
    cm = lesser.enter_spellspace(); space = cm.__enter__(); t3 = pc()
    space.meld(spell_id=ids[marker_cls]); t3b = pc(); space.meld(spell_id=ids[marker_cls]); t4 = pc()
    space.meld(spell_id=ids[outer_cls]); t5 = pc()
    if v == 0: space.meld(spell_id=ids[root_cls])
    elif v == 1: space.meld(spell_id=ids[group_cls]); space.meld(spell_id=ids[root_cls])
    else: space.meld(spell_id=ids[root_cls]); space.meld(spell_id=ids[root_cls])
    t6 = pc(); cm.__exit__(None, None, None); t7 = pc()
    return [t1 - t0, t1b - t1, t2 - t1b, t3 - t2, t3b - t3, t4 - t3b, t5 - t4, t6 - t5, t7 - t6], t7


def cycle_exit_protocol(v):
    """One cycle with create_lesser_conduit() and cleanup(), as the original probe."""
    t0 = pc(); lesser = conduit.create_lesser_conduit(); t1 = pc()
    steps, t7 = body_steps(lesser, v, t0, t1)
    lesser.cleanup(); t8 = pc()
    return steps + [t8 - t7]


def cycle_with_lesser(v):
    """One cycle with `with conduit.enter_lesser_conduit() as lesser:`; the block exit is lesser_cleanup."""
    t0 = pc()
    with conduit.enter_lesser_conduit() as lesser:
        t1 = pc()
        steps, t7 = body_steps(lesser, v, t0, t1)
    t8 = pc()
    return steps + [t8 - t7]


cycle = cycle_with_lesser if mode == "with_lesser" else cycle_exit_protocol


def body():
    """Warm up, then record every step of N cycles."""
    for i in range(800):
        cycle(i % 3)
    for i in range(N):
        for n, d in zip(names, cycle(i % 3)):
            acc[n].append(d)


t = threading.Thread(target=body)
t.start()
t.join()
tot = sum(statistics.median(v) for v in acc.values())
print(f"tree={ROOT.name} mode={mode} lane={lane} cycles={N} gil={sys._is_gil_enabled()} sum_of_step_medians={tot:,.0f} ns")
for n in names:
    m = statistics.median(acc[n])
    print(f"  {n:22s} median={m:7,.0f} ns  ({m / tot:5.1%})  mean={statistics.fmean(acc[n]):7,.0f}")
ops.cleanup()
