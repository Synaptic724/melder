"""melder_2 VM probe (no src change): capture creation-context template sources compiled while the gauntlet world is built and melded."""
import os, sys
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "tree_0270")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
captured = {}
def hook(event, args):
    if event == "compile" and len(args) >= 2 and isinstance(args[0], (str, bytes)) and "creation_context" in str(args[1]):
        captured.setdefault(str(args[1]), args[0] if isinstance(args[0], str) else args[0].decode())
sys.addaudithook(hook)
import benchmarks.testing_other_di.test_real_world_gauntlet as g
ops = g._build_ops("melder")
ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
rv = dict(zip(fv["_run_in_lesser_and_spellspace"].__code__.co_freevars, (c.cell_contents for c in fv["_run_in_lesser_and_spellspace"].__closure__)))
root, ids = rv["conduit"], rv["spell_ids"]
lesser = root.create_lesser_conduit()
lesser.meld(spell_id=ids[g.WorkerASession])
with lesser.enter_spellspace() as space:
    space.meld(spell_id=ids[g.WorkerAScopeMarker])
lesser.cleanup()
for name in sorted(captured):
    if "unique_per_conduit:0:0" in name or "spellspace:0:0" in name:
        print("-----", name)
        print(captured[name])
print("all template names:", sorted(captured))
ops.cleanup()
