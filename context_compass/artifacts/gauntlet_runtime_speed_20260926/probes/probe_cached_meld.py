"""melder_2 VM probe: cost layers of a cached (warm) meld, worker thread, 3.14t.

space.meld(spell_id=X)       public SpellSpace wrapper (keyword)            -> SpellSpaceMeld.meld (4 kwargs)
space._meld.meld(X)          door, positional (the docstring's cheapest call shape)
lesser.meld(spell_id=X)      public Conduit wrapper                          -> ConduitMeld.meld
lesser._meld.meld(X)         door, positional
"""
import statistics, sys, threading, time
from pathlib import Path
import os; ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "copy")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
ops = g._build_ops("melder"); ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit, ids = rv["conduit"], rv["spell_ids"]
outer, marker = ids[g.RequestSession], ids[g.RequestScopeMarker]
N = 100000
res = {}
def body():
    lesser = conduit.create_lesser_conduit()
    lesser.meld(spell_id=outer); lesser.meld(spell_id=outer)
    space = lesser.enter_spellspace().__enter__()
    space.meld(spell_id=marker); space.meld(spell_id=marker); space.meld(spell_id=outer)
    sm, cm = space._meld, lesser._meld
    cases = {
        "space.meld(spell_id=marker)": lambda: [space.meld(spell_id=marker) for _ in range(N)],
        "space._meld.meld(marker)": lambda: [sm.meld(marker) for _ in range(N)],
        "space.meld(spell_id=outer)": lambda: [space.meld(spell_id=outer) for _ in range(N)],
        "space._meld.meld(outer)": lambda: [sm.meld(outer) for _ in range(N)],
        "lesser.meld(spell_id=outer)": lambda: [lesser.meld(spell_id=outer) for _ in range(N)],
        "lesser._meld.meld(outer)": lambda: [cm.meld(outer) for _ in range(N)],
        "empty listcomp": lambda: [None for _ in range(N)],
    }
    for rnd in range(5):
        for name, fn in cases.items():
            t0 = time.perf_counter_ns(); fn(); res.setdefault(name, []).append((time.perf_counter_ns() - t0) / N)
    space.__exit__(None, None, None); lesser.cleanup()
t = threading.Thread(target=body); t.start(); t.join()
base = statistics.median(res["empty listcomp"])
for name, v in res.items():
    m = statistics.median(v); print(f"{name:30s} {m:6.1f} ns  (net {m - base:6.1f})")
ops.cleanup()
