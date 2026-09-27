"""Retained-state probe for the gauntlet's Melder lane (sandbox, diagnostic only).

Modes:
  churn       - exact harness path: test_real_world_gauntlet._run_gauntlet_once
                (3 fresh threads per iteration).
  persistent  - same 65 cycles per iteration on 3 long-lived threads.
At every checkpoint: gc.collect(), then count GC-tracked objects by type,
allocated blocks and RSS; report deltas vs the first checkpoint.
"""
import collections, gc, os, random, sys, threading, time
sys.path.insert(0, "/home/claude/work/melder")
sys.path.insert(0, "/home/claude/work/melder/src")
sys.path.insert(0, "/home/claude/work/melder/benchmarks/testing_other_di")
import test_real_world_gauntlet as g
from benchmarks.testing_other_di import test_melder_gauntlet as mg

mode = sys.argv[1]
iters = int(sys.argv[2])
every = int(sys.argv[3])
warm = int(sys.argv[4]) if len(sys.argv) > 4 else 500

def rss_kb():
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS"):
                return int(line.split()[1])
    return -1

def type_counts():
    c = collections.Counter()
    for o in gc.get_objects():
        t = type(o)
        c[f"{t.__module__}.{t.__qualname__}"] += 1
    return c

cfg = g._GauntletConfig(iterations=iters, threads=3, request_scope_runs=10, worker_a_jobs=25, worker_b_jobs=30)
ops = mg._build_runtime_melder()
ops.spawn_singletons()
lanes = [("request", ops.request_scope_cycle, 10, 17),
         ("worker_a", ops.worker_a_scope_cycle, 25, 29),
         ("worker_b", ops.worker_b_scope_cycle, 30, 41)]

class Persistent:
    def __init__(self):
        self.start = threading.Barrier(4)
        self.end = threading.Barrier(4)
        self.ix = 0
        self.stop = False
        self.threads = []
        for name, call, reps, off in lanes:
            t = threading.Thread(target=self.run, args=(call, reps, off), daemon=True)
            t.start(); self.threads.append(t)
    def run(self, call, reps, off):
        while True:
            self.start.wait()
            if self.stop:
                return
            rng = random.Random(330_011 + self.ix * 101 + off)
            for _ in range(reps):
                call(rng.randrange(3))
            self.end.wait()
    def iteration(self, ix):
        ops.bootstrap_fanout()
        self.ix = ix
        self.start.wait(); self.end.wait()

pers = Persistent() if mode == "persistent" else None
def one(ix):
    if pers is None:
        g._run_gauntlet_once(ops, cfg, ix)
    else:
        pers.iteration(ix)

for i in range(warm):
    one(i)
gc.collect()
base_counts = type_counts(); base_blocks = sys.getallocatedblocks(); base_rss = rss_kb()
print(f"mode={mode} warm={warm} base_objs={sum(base_counts.values())} blocks={base_blocks} rss_kb={base_rss} threads={threading.active_count()}", flush=True)
done = 0
while done < iters:
    t0 = time.perf_counter()
    for i in range(every):
        one(warm + done + i)
    el = time.perf_counter() - t0
    done += every
    gc.collect()
    c = type_counts()
    diff = c - base_counts
    objs = sum(c.values())
    print(f"after {done:6d} iters | cyc/s={every*65/el:8.0f} | objs={objs} (+{objs-sum(base_counts.values())}) "
          f"| blocks +{sys.getallocatedblocks()-base_blocks} | rss +{rss_kb()-base_rss} kB | thr={threading.active_count()}", flush=True)
    top = diff.most_common(8)
    if top:
        print("    grew:", ", ".join(f"{k}+{v}" for k, v in top), flush=True)
if pers is not None:
    pers.stop = True; pers.start.wait()
ops.cleanup()
