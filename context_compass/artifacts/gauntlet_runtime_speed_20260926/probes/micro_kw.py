import sys, time, threading, statistics
from pathlib import Path
sys.path[:0] = [str(Path.home()/"work"/"copy"), str(Path.home()/"work"/"copy"/"src")]
import benchmarks.testing_other_di.test_real_world_gauntlet as g
import inspect
# RequestRoot has 7 params; RequestGroup many
for cls in (g.Layer2Scope, g.RequestGroup, g.RequestRoot):
    print(cls.__name__, list(inspect.signature(cls).parameters))
N = 200000
def bench(fn):
    s = []
    for _ in range(7):
        t0 = time.perf_counter_ns(); fn(); s.append((time.perf_counter_ns() - t0) / N)
    return statistics.median(s)
a = object(); b = object()
L2 = g.Layer2Scope
def kw():
    for _ in range(N): L2(prior=a, branch=b)
def pos():
    for _ in range(N): L2(a, b)
def kw_try():
    for _ in range(N):
        try:
            x = L2(prior=a, branch=b)
        except Exception as exc:
            raise
out = {}
def run():
    out["kw"] = bench(kw); out["pos"] = bench(pos); out["kw_try"] = bench(kw_try)
t = threading.Thread(target=run); t.start(); t.join()
print({k: round(v, 1) for k, v in out.items()}, "ns per construction (worker thread, 3.14t)")
