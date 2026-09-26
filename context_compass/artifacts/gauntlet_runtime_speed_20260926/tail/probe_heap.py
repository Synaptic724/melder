"""melder_2 VM probe (no src change): which object types make up a library's GC-tracked world after setup."""
import collections, gc, os, sys
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "combined")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
gc.collect()
base = collections.Counter(type(o).__name__ for o in gc.get_objects())
base_mod = collections.Counter(getattr(type(o), "__module__", "?") for o in gc.get_objects())
import benchmarks.testing_other_di.test_real_world_gauntlet as g
lib = sys.argv[1]
ops = g._build_ops(lib)
ops.spawn_singletons()
os.environ["DI_GAUNTLET_ITERS"] = "2"
cfg = g._GauntletConfig.from_env()
for ix in range(2):
    g._run_gauntlet_once(ops, cfg, ix)
gc.collect()
objs = gc.get_objects()
after = collections.Counter(type(o).__name__ for o in objs)
mods = collections.Counter((getattr(type(o), "__module__", "?") or "?").split(".")[0] for o in objs)
delta = after - base
print(f"== {lib}: tracked after setup+2 turns = {len(objs):,}; before import of the harness = {sum(base.values()):,}; "
      f"added = {sum(delta.values()):,}")
print("   top added types:", ", ".join(f"{k}={v:,}" for k, v in delta.most_common(14)))
print("   tracked objects by top-level module of their type:", ", ".join(f"{k}={v:,}" for k, v in mods.most_common(8)))
