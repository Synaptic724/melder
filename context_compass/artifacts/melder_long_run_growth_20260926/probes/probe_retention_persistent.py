"""Control: same lanes on 3 PERSISTENT threads, samples retained (worker-allocated ints) or discarded.

Isolates thread exit: if retention slows cycles only when worker threads exit each iteration, the
effect needs thread churn (objects left behind by exited threads), not just a bigger heap.
"""
import gc, random, sys, threading, time
sys.path.insert(0, "/home/claude/work/melder")
sys.path.insert(0, "/home/claude/work/melder/src")
sys.path.insert(0, "/home/claude/work/melder/benchmarks/testing_other_di")
import test_real_world_gauntlet as g

lib = sys.argv[1]; mode = sys.argv[2]; iters = int(sys.argv[3]); windows = int(sys.argv[4])
assert mode in ("discard", "retain")
def rss_mb():
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS"):
                return int(line.split()[1]) // 1024
ops = g._build_ops(lib); ops.spawn_singletons()
lanes = [("request", ops.request_scope_cycle, 10, 17), ("worker_a", ops.worker_a_scope_cycle, 25, 29),
         ("worker_b", ops.worker_b_scope_cycle, 30, 41)]
start = threading.Barrier(4); end = threading.Barrier(4)
state = {"ix": 0, "stop": False}
per_iter = {name: g._new_lane_metric_samples() for name, *_ in lanes}
def worker(name, call, reps, off):
    while True:
        start.wait()
        if state["stop"]:
            return
        rng = random.Random(g._LIB_SEEDS[lib] + state["ix"] * 101 + off)
        s = per_iter[name]
        for _ in range(reps):
            m = call(rng.randrange(3))
            s.outer_create_ns.append(m.outer_create_ns); s.outer_cleanup_ns.append(m.outer_cleanup_ns)
            s.outer_total_ns.append(m.outer_total_ns); s.request_create_ns.append(m.request_create_ns)
            s.request_cleanup_ns.append(m.request_cleanup_ns); s.request_total_ns.append(m.request_total_ns)
        end.wait()
ts = [threading.Thread(target=worker, args=l, daemon=True) for l in lanes]
for t in ts: t.start()
kept = {name: g._new_lane_metric_samples() for name, *_ in lanes}
wsize = iters // windows
print(f"lib={lib} threads=persistent mode={mode} iters={iters}", flush=True)
t_w = time.perf_counter(); c_w = time.process_time()
for ix in range(iters):
    ops.bootstrap_fanout()
    for name in per_iter: per_iter[name] = g._new_lane_metric_samples()
    state["ix"] = ix
    start.wait(); end.wait()
    if mode == "retain":
        for name, v in per_iter.items():
            k = kept[name]
            k.outer_create_ns.extend(v.outer_create_ns); k.outer_cleanup_ns.extend(v.outer_cleanup_ns)
            k.outer_total_ns.extend(v.outer_total_ns); k.request_create_ns.extend(v.request_create_ns)
            k.request_cleanup_ns.extend(v.request_cleanup_ns); k.request_total_ns.extend(v.request_total_ns)
    if (ix + 1) % wsize == 0:
        el = time.perf_counter() - t_w; cpu = time.process_time() - c_w
        n = sum(len(x) for k in kept.values() for x in vars(k).values())
        print(f"  w{(ix+1)//wsize:02d} iters<= {ix+1:6d} | cyc/s={wsize*65/el:8.0f} | cpu_us/cycle={cpu/(wsize*65)*1e6:6.1f} "
              f"| rss_mb={rss_mb()} | retained_entries={n}", flush=True)
        t_w = time.perf_counter(); c_w = time.process_time()
state["stop"] = True; start.wait()
ops.cleanup()
