"""Tracked objects and full gc.collect() time at three stages: bare interpreter, `import melder`, conjured solo world.

Run from a tree root with PYTHONPATH=src:. Median of 9 collections per stage.
"""
import gc, statistics, sys, time


def stage(label):
    gc.collect()
    runs = []
    for _ in range(9):
        s = time.perf_counter_ns()
        gc.collect()
        runs.append((time.perf_counter_ns() - s) / 1e3)
    print(f"{label:28} tracked {len(gc.get_objects()):7d} | gc.collect {statistics.median(runs):8.1f} us | "
          f"modules {len(sys.modules)}")


print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
stage("bare interpreter")
import melder
stage("after import melder")
from benchmarks.testing_other_di import test_overrides_all as bench
stage("after importing benchmark")
spec = next(g for g in bench._override_graphs() if g.name == "solo")
ops = bench._build_override_melder(spec)
ops.get_root()
stage("solo world conjured")
melder_mods = [m for m in sys.modules if m == "melder" or m.startswith("melder.")]
print(f"melder modules loaded: {len(melder_mods)}")
by_type = {}
for o in gc.get_objects():
    by_type[type(o).__name__] = by_type.get(type(o).__name__, 0) + 1
print("top tracked types:", sorted(by_type.items(), key=lambda kv: -kv[1])[:10])
