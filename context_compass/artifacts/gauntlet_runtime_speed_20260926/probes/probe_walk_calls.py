"""melder_2 VM probe (P3 copy): how often defer_graph runs during a real gauntlet run, and what it costs."""
import collections, os, sys, time, traceback
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "copy")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
from melder.utilities.helpers.refcount_deferral import RefcountDeferral as R
stats = collections.defaultdict(lambda: [0, 0.0, 0])
orig = R.defer_graph.__func__
def timed(cls, *roots):
    t0 = time.perf_counter()
    n = orig(cls, *roots)
    dt = time.perf_counter() - t0
    caller = traceback.extract_stack(limit=3)[0]
    key = f"{Path(caller.filename).name}:{caller.name}"
    s = stats[key]; s[0] += 1; s[1] += dt; s[2] += n
    return n
R.defer_graph = classmethod(timed)
import benchmarks.testing_other_di.test_real_world_gauntlet as g
cfg = g._GauntletConfig.from_env()
t0 = time.perf_counter()
r = g._run_gauntlet_benchmark("melder", cfg)
total = time.perf_counter() - t0
for k, (calls, dt, n) in sorted(stats.items(), key=lambda kv: -kv[1][1]):
    print(f"{k:60s} calls={calls:6d} total={dt * 1e3:8.2f} ms deferred={n}")
print(f"run total {total:.1f} s")
