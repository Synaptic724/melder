"""Isolate the harness's sample retention as the only variable (sandbox diagnostic).

Runs the shared gauntlet's real Melder lane through test_real_world_gauntlet._run_gauntlet_once
(3 fresh threads per iteration). retain=1 extends the same 21 run-long int lists the harness keeps
(iteration/bootstrap/threaded + 3 lanes x 6 metrics); retain=0 drops them. Reports per window:
scope cycles/s, GC collections, GC pause total/max (gc.callbacks), and retained list entries.
"""
import gc, sys, threading, time
sys.path.insert(0, "/home/claude/work/melder")
sys.path.insert(0, "/home/claude/work/melder/src")
sys.path.insert(0, "/home/claude/work/melder/benchmarks/testing_other_di")
import test_real_world_gauntlet as g
from benchmarks.testing_other_di import test_melder_gauntlet as mg

lib = sys.argv[1]
mode = sys.argv[2]  # discard | retain | copy
assert mode in ("discard", "retain", "copy")
retain = mode != "discard"
copy = mode == "copy"
iters = int(sys.argv[3])
windows = int(sys.argv[4])

def rss_mb():
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS"):
                return int(line.split()[1]) // 1024
    return -1

class Probe:
    def __init__(self):
        self.lock = threading.Lock(); self.start = {}
        self.n = 0; self.total = 0; self.max = 0
    def cb(self, phase, info):
        tid = threading.get_ident()
        if phase == "start":
            self.start[tid] = time.perf_counter_ns(); return
        t0 = self.start.pop(tid, None)
        if t0 is None: return
        d = time.perf_counter_ns() - t0
        with self.lock:
            self.n += 1; self.total += d; self.max = max(self.max, d)
    def take(self):
        with self.lock:
            out = (self.n, self.total, self.max); self.n = 0; self.total = 0; self.max = 0
        return out

cfg = g._GauntletConfig(iterations=iters, threads=3, request_scope_runs=10, worker_a_jobs=25, worker_b_jobs=30)
ops = g._build_ops(lib)
ops.spawn_singletons()
lists = [[] for _ in range(3)]
lane_lists = {n: [[] for _ in range(6)] for n in ("request", "worker_a", "worker_b")}
probe = Probe(); gc.callbacks.append(probe.cb)
wsize = iters // windows
print(f"lib={lib} mode={mode} iters={iters} windows={windows} py={sys.version.split()[0]}", flush=True)
t_w = time.perf_counter(); c_w = time.process_time(); cycles_w = 0
for ix in range(iters):
    it = g._run_gauntlet_once(ops, cfg, ix)
    cycles_w += 65
    if retain:
        lists[0].append(it.total_ns); lists[1].append(it.bootstrap_ns); lists[2].append(it.threaded_ns)
        for name, v in it.lane_metrics.items():
            L = lane_lists[name]
            for dst, src in ((L[0], v.outer_create_ns), (L[1], v.outer_cleanup_ns), (L[2], v.outer_total_ns),
                             (L[3], v.request_create_ns), (L[4], v.request_cleanup_ns), (L[5], v.request_total_ns)):
                if copy:
                    dst.extend([x + 0 for x in src])  # new int objects allocated on the main thread
                else:
                    dst.extend(src)                    # harness-identical: ints allocated on worker threads
    if (ix + 1) % wsize == 0:
        el = time.perf_counter() - t_w
        cpu = time.process_time() - c_w
        n, tot, mx = probe.take()
        entries = sum(len(x) for x in lists) + sum(len(x) for L in lane_lists.values() for x in L)
        print(f"  w{(ix+1)//wsize:02d} iters<= {ix+1:6d} | cyc/s={cycles_w/el:8.0f} | gc_coll={n:5d} "
              f"| pause_tot={tot/1e6:9.1f}ms max={mx/1e6:7.2f}ms avg={(tot/n/1e6 if n else 0):6.2f}ms "
              f"| cpu_us/cycle={cpu/cycles_w*1e6:6.1f} | rss_mb={rss_mb()} | retained_entries={entries}", flush=True)
        t_w = time.perf_counter(); c_w = time.process_time(); cycles_w = 0
gc.callbacks.remove(probe.cb)
ops.cleanup()
