"""melder_2 VM probe: does lesser.meld(spell_id=...) take Conduit.meld's inlined fast door, and what does each arm cost."""
import statistics, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
ops = g._build_ops("melder"); ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit, ids = rv["conduit"], rv["spell_ids"]
outer = ids[g.RequestSession]
def body(tag):
    lesser = conduit.create_lesser_conduit()
    lesser.meld(spell_id=outer); lesser.meld(spell_id=outer)
    m = lesser._meld
    print(tag, "dynamic_env:", lesser.__dynamic_environment__, "| meld_hooks:", bool(m._meld_hooks),
          "| entry:", outer in m._fast_meld_doors, "| validation_required:", m._spellbook._spellbook_validation_required)
    N = 100000
    for name, fn in (("lesser.meld(spell_id=outer)", lambda: [lesser.meld(spell_id=outer) for _ in range(N)]),
                     ("door m.meld(outer)", lambda: [m.meld(outer) for _ in range(N)])):
        s = []
        for _ in range(5):
            t0 = time.perf_counter_ns(); fn(); s.append((time.perf_counter_ns() - t0) / N)
        print(tag, f"{name:28s} {statistics.median(s):6.1f} ns")
    lesser.cleanup()
body("main")
t = threading.Thread(target=body, args=("worker",)); t.start(); t.join()
ops.cleanup()
