"""Solo graph cost split: per-call meld vs the benchmark's periodic gc.collect() (owner's test_overrides_all.py).

Run from a tree root with PYTHONPATH=src:. Arg: melder | di. Builds the solo graph exactly as the benchmark does,
then times get_root() and gc.collect() separately; the benchmark collects every 2000 steps (DI_OVERRIDE_GC_EVERY).
"""
import gc, statistics, sys, time
from benchmarks.testing_other_di import test_overrides_all as bench


def per_call_ns(fn, n=200000):
    samples = []
    for _ in range(7):
        s = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - s) / n)
    return statistics.median(samples)


lib = sys.argv[1]
spec = next(g for g in bench._override_graphs() if g.name == "solo")
ops = bench._build_override_melder(spec) if lib == "melder" else bench._build_override_dependency_injector(spec)
get_root = ops.get_root
get_root()
t_root = per_call_ns(get_root)
gcs = []
for _ in range(9):
    s = time.perf_counter_ns()
    gc.collect()
    gcs.append((time.perf_counter_ns() - s) / 1e3)
t_gc_us = statistics.median(gcs)
tracked = len(gc.get_objects())
print(f"{lib:7} gil={sys._is_gil_enabled()} get_root {t_root:7.1f} ns | gc.collect {t_gc_us:8.1f} us "
      f"-> {t_gc_us * 1000 / 2000:7.1f} ns/step at gc_every=2000 | tracked objects {tracked}")
ops.cleanup()
