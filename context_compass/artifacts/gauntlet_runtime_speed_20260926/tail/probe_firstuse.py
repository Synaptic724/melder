"""melder_2 VM probe (no src change): what a library's first scope cycle pays, and how big a GC pause is.

For one library: build the gauntlet world, then (a) count GC-tracked objects and time one full gc.collect(),
(b) time the harness's turn 0 with Melder's hydration pieces wrapped (site-plan runtime construction, executor
compile), and (c) with MODE=warm, run every lane once on a throwaway thread before turn 0 is timed.

usage: probe_firstuse.py <lib> [cold|warm]
"""
import gc, os, sys, threading, time
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "combined")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g

lib = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "cold"
timers = {}


def wrap(owner, name, label):
    original = getattr(owner, name)

    def timed(*args, **kwargs):
        t0 = time.perf_counter_ns()
        try:
            return original(*args, **kwargs)
        finally:
            dt = time.perf_counter_ns() - t0
            n, s = timers.get(label, (0, 0))
            timers[label] = (n + 1, s + dt)

    setattr(owner, name, timed)


if lib == "melder":
    import melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.site_plan_override_runtime as rt
    import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_hydrator as gh
    wrap(rt, "get_or_compile_executor_code", "compile executor (site plan)")
    wrap(rt.SitePlanOverrideRuntime, "__init__", "SitePlanOverrideRuntime build (incl. compile)")
    wrap(gh, "hydrate_creation_executors", "generalized hydrate_creation_executors (incl. above)")

os.environ["DI_GAUNTLET_ITERS"] = "3"
cfg = g._GauntletConfig.from_env()
ops = g._build_ops(lib)
ops.spawn_singletons()
gc.collect()
tracked = len(gc.get_objects())
t0 = time.perf_counter_ns()
gc.collect()
full_gc_ms = (time.perf_counter_ns() - t0) / 1e6
if mode == "warm":
    lanes = [ops.request_scope_cycle, ops.worker_a_scope_cycle, ops.worker_b_scope_cycle]
    ts = [threading.Thread(target=lambda c=c: [c(v) for v in range(3)]) for c in lanes]
    [t.start() for t in ts]
    [t.join() for t in ts]
    timers.clear()
rows = []
for ix in range(3):
    r = g._run_gauntlet_once(ops, cfg, ix)
    firsts = {n: (m.outer_total_ns[0] / 1e6, m.request_total_ns[0] / 1e6) for n, m in r.lane_metrics.items() if len(m.outer_total_ns)}
    rows.append((ix, r.total_ns / 1e6, r.threaded_ns / 1e6, firsts))
print(f"== {lib} mode={mode} gc_tracked_objects={tracked:,} full_gc_collect={full_gc_ms:.2f}ms")
for ix, tot, thr, firsts in rows:
    f = " ".join(f"{n}:outer={v[0]:.3f}/req={v[1]:.3f}" for n, v in firsts.items())
    print(f"   turn {ix}: total={tot:.3f} threaded={thr:.3f} | first cycles (ms) {f}")
for label, (n, s) in timers.items():
    print(f"   {label}: calls={n} total={s / 1e6:.3f}ms")
