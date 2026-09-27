"""melder_2 VM probe: how much of space exit / lesser cleanup is deallocation of the scope's objects.

Modes per cycle (request lane, worker thread):
  empty  - no melds (pure lifecycle)
  held   - melds, but the caller keeps references to every melded object until after cleanup (no dealloc in steps)
  normal - melds, references dropped before exit (the gauntlet's shape: stores own the last references)
"""
import statistics, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
N = 6000
ops = g._build_ops("melder"); ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit, ids = rv["conduit"], rv["spell_ids"]
outer, marker, root = ids[g.RequestSession], ids[g.RequestScopeMarker], ids[g.RequestRoot]
pc = time.perf_counter_ns
def cycle(mode, keep):
    lesser = conduit.create_lesser_conduit()
    if mode != "empty":
        keep.append(lesser.meld(spell_id=outer))
    space = lesser.enter_spellspace().__enter__()
    if mode != "empty":
        keep.append(space.meld(spell_id=marker)); keep.append(space.meld(spell_id=root))
        if mode == "normal":
            keep.clear()
    t0 = pc(); space.__exit__(None, None, None); t1 = pc(); lesser.cleanup(); t2 = pc()
    keep.clear()
    return t1 - t0, t2 - t1
res = {}
def body():
    for mode in ("empty", "held", "normal", "empty", "held", "normal"):
        keep = []
        for _ in range(600): cycle(mode, keep)
        ex, cl = [], []
        for _ in range(N):
            a, b = cycle(mode, keep); ex.append(a); cl.append(b)
        res.setdefault(mode, []).append((statistics.median(ex), statistics.median(cl)))
t = threading.Thread(target=body); t.start(); t.join()
for mode, rows in res.items():
    print(f"{mode:7s} space_exit={statistics.median(r[0] for r in rows):6,.0f} ns  lesser_cleanup={statistics.median(r[1] for r in rows):6,.0f} ns  (rounds: {rows})")
ops.cleanup()
