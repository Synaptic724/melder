"""melder_2 VM experiment: run the shared gauntlet (dishka + melder) with Melder's kernel objects switched to deferred
reference counting after conjure (mode=deferred) or unchanged (mode=base). Not a src change.

usage: DI_GAUNTLET_ITERS=... python -X gil=0 gauntlet_deferred.py {base|deferred}
"""
import ctypes, gc, sys
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
mode = sys.argv[1]
orig_build = g._build_ops
def enable_deferred(ops):
    import types as _types
    f = ctypes.pythonapi.PyUnstable_Object_EnableDeferredRefcount
    f.argtypes = [ctypes.py_object]; f.restype = ctypes.c_int
    user_mod = g.__name__
    def holds_user(c):
        try:
            vals = c.values() if isinstance(c, dict) else c
            return any(type(v).__module__ == user_mod or (type(v).__module__ != "builtins" and not type(v).__module__.startswith("melder") and not isinstance(v, (type, _types.FunctionType, _types.CellType))) for v in vals)
        except Exception:
            return True
    fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
    run = fv["_run_in_lesser_and_spellspace"]
    rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
    conduit = rv["conduit"]
    seen, stack, n = set(), [conduit, conduit._spellbook], 0
    while stack:
        o = stack.pop()
        if id(o) in seen: continue
        seen.add(id(o))
        t = type(o)
        if t.__module__ == g.__name__ or isinstance(o, type) or t.__module__ in ("threading", "_thread"):
            continue
        if isinstance(o, (_types.ModuleType, _types.CodeType)) or (isinstance(o, dict) and "__builtins__" in o):
            continue
        melder_obj = t.__module__.startswith("melder")
        take = melder_obj or t in (_types.FunctionType, _types.MethodType, _types.CellType) or (
            t in (dict, list, tuple, set, frozenset) and not holds_user(o))
        if take and gc.is_tracked(o):
            n += f(o)
        stack.extend(gc.get_referents(o))
    return n
def build(lib):
    ops = orig_build(lib)
    if lib == "melder" and mode == "deferred":
        spawn = ops.spawn_singletons
        def spawn_then_defer():
            spawn()
            print(f"[melder_2 experiment] deferred refcount enabled on {enable_deferred(ops)} objects")
        import dataclasses
        calls = [0]
        boot = ops.bootstrap_fanout
        def boot_then_defer():
            calls[0] += 1
            if calls[0] == 2:  # after iteration 1: hydrated executors and pooled shells now exist
                print(f"[melder_2 experiment] deferred refcount enabled on {enable_deferred(ops)} more objects")
            boot()
        return dataclasses.replace(ops, spawn_singletons=spawn_then_defer, bootstrap_fanout=boot_then_defer)
    return ops
g._build_ops = build
cfg = g._GauntletConfig.from_env()
for lib in (sys.argv[2].split(",") if len(sys.argv) > 2 else ("dishka", "melder")):
    r = g._run_gauntlet_benchmark(lib, cfg)
    g._print_benchmark_result(r)
