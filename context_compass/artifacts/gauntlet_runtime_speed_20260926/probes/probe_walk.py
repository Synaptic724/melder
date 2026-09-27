"""melder_2 VM probe: RefcountDeferral.defer_graph over the gauntlet world after warm-up: count, time, dict-based types."""
import collections, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
from melder.utilities.helpers.refcount_deferral import RefcountDeferral as R
ops = g._build_ops("melder"); ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit = rv["conduit"]
for c in (ops.request_scope_cycle, ops.worker_a_scope_cycle, ops.worker_b_scope_cycle):
    t = threading.Thread(target=lambda c=c: [c(i % 3) for i in range(50)]); t.start(); t.join()
dict_based = collections.Counter()
orig = R._slot_names.__func__ if hasattr(R._slot_names, "__func__") else R._slot_names
def spy(obj_type):
    r = orig(obj_type)
    if r[1]: dict_based[obj_type.__qualname__] += 1
    return r
R._slot_names = staticmethod(spy)
t0 = time.perf_counter(); n = R.defer_graph(conduit._spellbook, conduit); t1 = time.perf_counter()
print(f"deferred {n} objects in {(t1 - t0) * 1e3:.1f} ms; dict-based melder types: {dict(dict_based)}")
t0 = time.perf_counter(); n2 = R.defer_graph(conduit._spellbook, conduit); t1 = time.perf_counter()
print(f"second walk deferred {n2} in {(t1 - t0) * 1e3:.2f} ms")
ops.cleanup()
