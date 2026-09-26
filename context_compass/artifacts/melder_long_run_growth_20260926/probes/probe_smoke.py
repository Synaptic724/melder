import gc, sys, time, os
sys.path.insert(0, "/home/claude/work/melder")
sys.path.insert(0, "/home/claude/work/melder/src")
sys.path.insert(0, "/home/claude/work/melder/benchmarks/testing_other_di")
import test_real_world_gauntlet as g
from benchmarks.testing_other_di import test_melder_gauntlet as mg
print(sys.version, "gil", sys._is_gil_enabled())
cfg = g._GauntletConfig(iterations=200, threads=3, request_scope_runs=10, worker_a_jobs=25, worker_b_jobs=30)
t0 = time.perf_counter()
ops = mg._build_runtime_melder()
ops.spawn_singletons()
print("setup s", time.perf_counter() - t0)
t0 = time.perf_counter()
for i in range(200):
    g._run_gauntlet_once(ops, cfg, i)
el = time.perf_counter() - t0
print("200 iters s", el, "cycles/s", 200*65/el)
ops.cleanup()
