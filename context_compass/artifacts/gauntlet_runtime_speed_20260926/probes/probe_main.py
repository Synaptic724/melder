"""melder_2 VM probe: full scope cycles on the MAIN thread (everything owned by the running thread)."""
import os, statistics, sys, time
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "copy")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
ops = g._build_ops("melder"); ops.spawn_singletons()
lanes = {"request": ops.request_scope_cycle, "worker_a": ops.worker_a_scope_cycle, "worker_b": ops.worker_b_scope_cycle}
for c in lanes.values():
    for i in range(300): c(i % 3)
out = {}
for rnd in range(3):
    for n, c in lanes.items():
        t0 = time.perf_counter_ns()
        for i in range(3000): c(i % 3)
        out.setdefault(n, []).append((time.perf_counter_ns() - t0) / 3000)
print("main-thread " + "  ".join(f"{n}={statistics.median(v):,.0f}ns" for n, v in out.items()))
ops.cleanup()
