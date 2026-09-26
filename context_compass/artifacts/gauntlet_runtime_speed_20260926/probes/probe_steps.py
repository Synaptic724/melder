"""melder_2 VM probe: per-step time inside one Melder request-lane scope cycle (worker thread, no profiler)."""
import statistics, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
lane = sys.argv[1] if len(sys.argv) > 1 else "request"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
outer_cls, marker_cls, root_cls, group_cls = {
    "request": (g.RequestSession, g.RequestScopeMarker, g.RequestRoot, g.RequestGroup),
    "worker_a": (g.WorkerASession, g.WorkerAScopeMarker, g.WorkerAJobRoot, g.WorkerAGroup),
    "worker_b": (g.WorkerBSession, g.WorkerBScopeMarker, g.WorkerBJobRoot, g.WorkerBGroup)}[lane]
ops = g._build_ops("melder"); ops.spawn_singletons()
# reach the conduit and ids the harness closed over
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit, ids = rv["conduit"], rv["spell_ids"]
names = ["lesser_create", "lesser_meld_1st", "lesser_meld_2nd", "space_enter", "space_meld_marker_1st", "space_meld_marker_2nd", "space_meld_outer",
         "root_meld(variant)", "space_exit", "lesser_cleanup"]
acc = {n: [] for n in names}
pc = time.perf_counter_ns
def cycle(v):
    t0 = pc(); lesser = conduit.create_lesser_conduit(); t1 = pc()
    lesser.meld(spell_id=ids[outer_cls]); t1b = pc(); lesser.meld(spell_id=ids[outer_cls]); t2 = pc()
    cm = lesser.enter_spellspace(); space = cm.__enter__(); t3 = pc()
    space.meld(spell_id=ids[marker_cls]); t3b = pc(); space.meld(spell_id=ids[marker_cls]); t4 = pc()
    space.meld(spell_id=ids[outer_cls]); t5 = pc()
    if v == 0: space.meld(spell_id=ids[root_cls])
    elif v == 1: space.meld(spell_id=ids[group_cls]); space.meld(spell_id=ids[root_cls])
    else: space.meld(spell_id=ids[root_cls]); space.meld(spell_id=ids[root_cls])
    t6 = pc(); cm.__exit__(None, None, None); t7 = pc(); lesser.cleanup(); t8 = pc()
    return (t1 - t0, t1b - t1, t2 - t1b, t3 - t2, t3b - t3, t4 - t3b, t5 - t4, t6 - t5, t7 - t6, t8 - t7)
def body():
    for i in range(800): cycle(i % 3)
    for i in range(N):
        for n, d in zip(names, cycle(i % 3)): acc[n].append(d)
t = threading.Thread(target=body); t.start(); t.join()
tot = sum(statistics.median(v) for v in acc.values())
print(f"melder lane={lane} cycles={N} sum_of_step_medians={tot:,.0f} ns")
for n in names:
    m = statistics.median(acc[n]); print(f"  {n:22s} median={m:7,.0f} ns  ({m / tot:5.1%})  mean={statistics.fmean(acc[n]):7,.0f}")
ops.cleanup()
