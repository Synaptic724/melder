"""melder_2 VM probe: per-scope-cycle timing and call counts over the real-world gauntlet's own lane callables.

Not part of the repo. Builds a library's runtime through the harness (_build_ops), then runs one lane's scope
cycles on a single worker thread (the gauntlet's hot path runs on worker threads) with variants rotating 0,1,2.
"""
import argparse, cProfile, gc, io, pstats, statistics, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g

ap = argparse.ArgumentParser()
ap.add_argument("--lib", default="melder")
ap.add_argument("--lane", default="request")
ap.add_argument("--cycles", type=int, default=3000)
ap.add_argument("--repeats", type=int, default=7)
ap.add_argument("--warmup", type=int, default=600)
ap.add_argument("--mode", default="time", choices=("time", "profile"))
ap.add_argument("--top", type=int, default=45)
ap.add_argument("--thread", default="worker", choices=("worker", "main"))
a = ap.parse_args()

ops = g._build_ops(a.lib)
ops.spawn_singletons()
call = {"request": ops.request_scope_cycle, "worker_a": ops.worker_a_scope_cycle,
        "worker_b": ops.worker_b_scope_cycle}[a.lane]

def loop(n):
    for i in range(n):
        call(i % 3)

out = {}
def body():
    loop(a.warmup)
    if a.mode == "time":
        samples = []
        for _ in range(a.repeats):
            t0 = time.perf_counter_ns(); loop(a.cycles); samples.append((time.perf_counter_ns() - t0) / a.cycles)
        out["samples"] = samples
    else:
        prof = cProfile.Profile(); prof.enable(); loop(a.cycles); prof.disable(); out["prof"] = prof

if a.thread == "worker":
    t = threading.Thread(target=body); t.start(); t.join()
else:
    body()
if a.mode == "time":
    s = out["samples"]
    print(f"{a.lib} lane={a.lane} ns/cycle median={statistics.median(s):,.0f} min={min(s):,.0f} max={max(s):,.0f} "
          f"reps={a.repeats}x{a.cycles} thread={a.thread}")
else:
    st = pstats.Stats(out["prof"]); st.sort_stats("tottime")
    total_calls = sum(v[1] for v in st.stats.values())
    print(f"{a.lib} lane={a.lane} cycles={a.cycles} python_calls/cycle={total_calls / a.cycles:.1f}")
    rows = sorted(st.stats.items(), key=lambda kv: kv[1][2], reverse=True)[: a.top]
    print(f"{'calls/cyc':>9} {'tot_us/cyc':>10} {'cum_us/cyc':>10}  function")
    for (fn, ln, name), (cc, nc, tt, ct, _) in rows:
        short = fn.replace(str(ROOT) + "/", "")
        print(f"{nc / a.cycles:9.2f} {tt * 1e6 / a.cycles:10.2f} {ct * 1e6 / a.cycles:10.2f}  {short}:{ln}({name})")
ops.cleanup()
