"""melder_2 VM experiment (no src change): does interning the strings reachable from Melder's runtime graph
(spell ids, keys) help on its own, without any refcount deferral? Fresh worker thread per lane after warm-up.

usage: probe_intern.py {base|intern}
"""
import gc, os, statistics, sys, threading, time
import types as _types
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "copy_base")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
mode = sys.argv[1]
ops = g._build_ops("melder"); ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit = rv["conduit"]
lanes = {"request": ops.request_scope_cycle, "worker_a": ops.worker_a_scope_cycle, "worker_b": ops.worker_b_scope_cycle}
for _ in range(3):
    ts = [threading.Thread(target=lambda c=c: [c(i % 3) for i in range(100)]) for c in lanes.values()]
    [t.start() for t in ts]; [t.join() for t in ts]
interned = 0
if mode == "intern":
    user_mod = g.__name__
    seen = set(); stack = [conduit, conduit._spellbook]
    while stack:
        o = stack.pop()
        if id(o) in seen: continue
        seen.add(id(o))
        t = type(o)
        if t is str:
            if not sys._is_immortal(o):
                sys.intern(o); interned += 1
            continue
        if t.__module__ == user_mod or isinstance(o, (type, _types.ModuleType, _types.CodeType)) or t.__module__ in ("threading", "_thread"):
            continue
        if isinstance(o, dict) and "__builtins__" in o:
            continue
        stack.extend(gc.get_referents(o))
    print(f"interned {interned} strings in place")
N = 3000
res = {}
def lane_run(name, call):
    s = []
    for _ in range(3):
        t0 = time.perf_counter_ns()
        for i in range(N): call(i % 3)
        s.append((time.perf_counter_ns() - t0) / N)
    res.setdefault(name, []).append(statistics.median(s))
for rnd in range(3):
    for name, call in lanes.items():
        t = threading.Thread(target=lane_run, args=(name, call)); t.start(); t.join()
print(mode, "threads=1", "  ".join(f"{n}={statistics.median(v):,.0f}ns" for n, v in res.items()))
ops.cleanup()
