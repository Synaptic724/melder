"""Attribute melder's import footprint and time young vs full collections (run from a tree root, PYTHONPATH=src:.).

Counts GC-tracked functions, code objects and classes per melder subpackage after `import melder`, and times
gc.collect(0) and gc.collect(2) before and after the import (median of 9).
"""
import gc, statistics, sys, time, types, warnings

warnings.simplefilter("ignore")


def timed(gen):
    gc.collect()
    runs = []
    for _ in range(9):
        s = time.perf_counter_ns()
        gc.collect(gen)
        runs.append((time.perf_counter_ns() - s) / 1e3)
    return statistics.median(runs)


print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
print(f"before import: gen0 {timed(0):7.1f} us | full {timed(2):7.1f} us | tracked {len(gc.get_objects())}")
import melder
print(f"after import:  gen0 {timed(0):7.1f} us | full {timed(2):7.1f} us | tracked {len(gc.get_objects())}")
buckets = {}
for obj in gc.get_objects():
    if isinstance(obj, types.FunctionType):
        mod, kind = obj.__module__ or "", "function"
    elif isinstance(obj, types.CodeType):
        mod, kind = "", "code"
        name = obj.co_filename.replace("\\", "/")
        if "/melder/" in name:
            mod = "melder." + name.split("/melder/", 1)[1].replace("/", ".")
    elif isinstance(obj, type):
        mod, kind = obj.__module__ or "", "class"
    else:
        continue
    if not mod.startswith("melder"):
        mod = "(other)"
    parts = mod.split(".")
    key = ".".join(parts[:3]) if len(parts) > 2 else mod
    row = buckets.setdefault(key, {"function": 0, "code": 0, "class": 0})
    row[kind] += 1
rows = sorted(buckets.items(), key=lambda kv: -sum(kv[1].values()))
for key, row in rows[:16]:
    print(f"  {key:52} functions {row['function']:6d} code {row['code']:6d} classes {row['class']:5d}")
melder_mods = [m for m in sys.modules if m == "melder" or m.startswith("melder.")]
print(f"melder modules {len(melder_mods)}; functions total "
      f"{sum(r['function'] for k, r in buckets.items() if k != '(other)')}")
