"""melder_2 VM long-run gate: gauntlet-shaped soak (3 new threads per iteration: request x10, worker_a x25,
worker_b x30), reporting per 1,000-iteration window: per-thread CPU time per cycle per lane, wall per
iteration, process RSS and GC collections. A change passes when its windows stay flat and its RSS does not
drift beyond the unmodified tree's.

usage: MELDER_ROOT=<copy> probe_soak.py [iterations] [window]
"""
import collections, gc, os, statistics, sys, threading, time
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "copy_base")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
ITERS = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
WINDOW = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
def rss_mb():
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024.0
    return float("nan")
ops = g._build_ops("melder"); ops.spawn_singletons()
lanes = [("request", ops.request_scope_cycle, 10), ("worker_a", ops.worker_a_scope_cycle, 25), ("worker_b", ops.worker_b_scope_cycle, 30)]
cpu = collections.defaultdict(list)
def worker(name, call, reps, barrier):
    barrier.wait()
    tt = time.thread_time_ns
    for i in range(reps):
        t0 = tt(); call(i % 3); cpu[name].append(tt() - t0)
wall = []
t_start = time.perf_counter()
print(f"root={ROOT.name} iterations={ITERS} window={WINDOW}")
for it in range(1, ITERS + 1):
    ops.bootstrap_fanout()
    barrier = threading.Barrier(len(lanes))
    ts = [threading.Thread(target=worker, args=(n, c, r, barrier)) for n, c, r in lanes]
    t0 = time.perf_counter_ns()
    [t.start() for t in ts]; [t.join() for t in ts]
    wall.append(time.perf_counter_ns() - t0)
    if it % WINDOW == 0:
        collections_total = sum(s["collections"] for s in gc.get_stats())
        print(f"win={it // WINDOW:3d} " + " ".join(f"{n}={statistics.fmean(v):6,.0f}ns" for n, v in sorted(cpu.items()))
              + f" wall/iter={statistics.median(wall) / 1e3:6,.0f}us rss={rss_mb():6.1f}MB gc_collections={collections_total}", flush=True)
        cpu.clear(); wall.clear()
print(f"total {time.perf_counter() - t_start:.1f}s")
ops.cleanup()
