"""melder_2 VM probe (no src change): capture the generated site-plan source compiled at the first meld of chosen spells."""
import os, sys
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "tree_0270")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
captured = []
def hook(event, args):
    if event == "compile" and len(args) >= 2 and isinstance(args[0], (str, bytes)) and "site_plan" in str(args[1]):
        captured.append((str(args[1]), args[0] if isinstance(args[0], str) else args[0].decode()))
sys.addaudithook(hook)
ops = g._build_ops("melder")
ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
rv = dict(zip(fv["_run_in_lesser_and_spellspace"].__code__.co_freevars, (c.cell_contents for c in fv["_run_in_lesser_and_spellspace"].__closure__)))
root, ids = rv["conduit"], rv["spell_ids"]
lesser = root.create_lesser_conduit()
n0 = len(captured); lesser.meld(spell_id=ids[g.WorkerASession]); s_session = captured[n0:]
with lesser.enter_spellspace() as space:
    n1 = len(captured); space.meld(spell_id=ids[g.WorkerAScopeMarker]); s_marker = captured[n1:]
lesser.cleanup()
for title, srcs in (("WorkerASession (unique_per_conduit)", s_session), ("WorkerAScopeMarker (unique_per_spell_space)", s_marker)):
    print(f"===== {title}: {len(srcs)} compiled unit(s)")
    for fname, src in srcs:
        print(f"----- {fname}")
        print(src)
ops.cleanup()
