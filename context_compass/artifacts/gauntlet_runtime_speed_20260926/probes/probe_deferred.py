"""melder_2 VM experiment (not a src change): per-cycle cost on worker threads with and without deferred reference
counting enabled (CPython 3.14 PyUnstable_Object_EnableDeferredRefcount via ctypes) on the long-lived Melder kernel
objects reachable from the root conduit and spellbook. User-class instances are excluded.

usage: probe_deferred.py {base|deferred} [threads]
"""
import ctypes, gc, statistics, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
mode = sys.argv[1]
nthreads = int(sys.argv[2]) if len(sys.argv) > 2 else 1
ops = g._build_ops("melder"); ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit = rv["conduit"]
lanes = {"request": ops.request_scope_cycle, "worker_a": ops.worker_a_scope_cycle, "worker_b": ops.worker_b_scope_cycle}
# warm on short-lived threads, like the gauntlet (hydrates executors, builds fast-door entries, pools shells)
for _ in range(3):
    ts = [threading.Thread(target=lambda c=c: [c(i % 3) for i in range(100)]) for c in lanes.values()]
    [t.start() for t in ts]; [t.join() for t in ts]
enabled = 0
if mode == "deferred":
    f = ctypes.pythonapi.PyUnstable_Object_EnableDeferredRefcount
    f.argtypes = [ctypes.py_object]; f.restype = ctypes.c_int
    user_mod = g.__name__
    import types as _types
    scope = sys.argv[3] if len(sys.argv) > 3 else "all"
    kinds = {}
    seen = set(); stack = [conduit, conduit._spellbook]
    t_walk = time.perf_counter()
    while stack:
        o = stack.pop()
        if id(o) in seen: continue
        seen.add(id(o))
        t = type(o)
        if t.__module__ == user_mod or isinstance(o, type) or t.__module__ in ("threading", "_thread"):
            continue
        if isinstance(o, (_types.ModuleType, _types.CodeType)):
            continue
        if scope != "all" and isinstance(o, dict) and "__builtins__" in o:
            continue  # a module globals dict reached through a function: do not escape into module namespaces
        melder_obj = t.__module__.startswith("melder")
        def holds_user(c):
            try:
                vals = c.values() if isinstance(c, dict) else c
                return any(type(v).__module__ == user_mod or (type(v).__module__ not in ("builtins",) and not type(v).__module__.startswith("melder") and not isinstance(v, (type, _types.FunctionType, _types.CellType))) for v in vals)
            except Exception:
                return True
        take = (scope == "all" or (scope == "kernel" and melder_obj)
                or (scope == "kernel+functions+tuples" and (melder_obj or t in (tuple, frozenset, _types.FunctionType, _types.MethodType, _types.CellType)))
                or (scope == "userfree" and (melder_obj or t in (_types.FunctionType, _types.MethodType, _types.CellType)
                                              or (t in (dict, list, tuple, set, frozenset) and not holds_user(o))))
                or (scope == "kernel+containers" and (melder_obj or t in (dict, list, tuple, set, frozenset)))
                or (scope == "kernel+containers+functions" and (melder_obj or t in (dict, list, tuple, set, frozenset,
                    _types.FunctionType, _types.MethodType, _types.CellType))))
        if take and gc.is_tracked(o):
            r = f(o); enabled += r
            if r: kinds[t.__name__] = kinds.get(t.__name__, 0) + 1
        stack.extend(gc.get_referents(o))
    t_walk = time.perf_counter() - t_walk
    top = sorted(kinds.items(), key=lambda kv: -kv[1])[:8]
    print(f"scope={scope} deferred on {enabled} objects (walked {len(seen)}, {t_walk * 1e3:.0f} ms) top={top}")
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
    if nthreads == 1:
        for name, call in lanes.items():
            t = threading.Thread(target=lane_run, args=(name, call)); t.start(); t.join()
    else:
        ts = [threading.Thread(target=lane_run, args=(n, c)) for n, c in list(lanes.items())[:nthreads]]
        [t.start() for t in ts]; [t.join() for t in ts]
print(mode + (":" + sys.argv[3] if len(sys.argv) > 3 else ""), f"threads={nthreads}", "  ".join(f"{n}={statistics.median(v):,.0f}ns" for n, v in res.items()))
ops.cleanup()
