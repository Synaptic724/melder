"""melder_2 VM probe: gauntlet setup cost (build ops = bind + conjure, then spawn_singletons), fresh process."""
import os, sys, time
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "copy")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
t0 = time.perf_counter(); ops = g._build_ops("melder"); t1 = time.perf_counter(); ops.spawn_singletons(); t2 = time.perf_counter()
print(f"build_ops={1e3 * (t1 - t0):.1f} ms spawn={1e3 * (t2 - t1):.1f} ms")
ops.cleanup()
