"""melder_2 VM probe: scope lifecycle only (create lesser, enter/exit spellspace, cleanup), optional cProfile."""
import cProfile, pstats, statistics, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
mode = sys.argv[1] if len(sys.argv) > 1 else "time"
with_meld = len(sys.argv) > 2 and sys.argv[2] == "meld"
ops = g._build_ops("melder"); ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit, ids = rv["conduit"], rv["spell_ids"]
marker = ids[g.RequestScopeMarker]; outer = ids[g.RequestSession]
N = 20000
def cycle():
    lesser = conduit.create_lesser_conduit()
    if with_meld:
        lesser.meld(spell_id=outer)
    cm = lesser.enter_spellspace(); space = cm.__enter__()
    if with_meld:
        space.meld(spell_id=marker)
    cm.__exit__(None, None, None)
    lesser.cleanup()
out = {}
def body():
    for _ in range(2000): cycle()
    if mode == "time":
        s = []
        for _ in range(5):
            t0 = time.perf_counter_ns()
            for _ in range(N): cycle()
            s.append((time.perf_counter_ns() - t0) / N)
        out["s"] = s
    else:
        pr = cProfile.Profile(); pr.enable()
        for _ in range(N): cycle()
        pr.disable(); out["p"] = pr
t = threading.Thread(target=body); t.start(); t.join()
if mode == "time":
    print(f"lifecycle{'+2 melds' if with_meld else ''} ns/cycle median={statistics.median(out['s']):,.0f} min={min(out['s']):,.0f}")
else:
    st = pstats.Stats(out["p"])
    rows = sorted(st.stats.items(), key=lambda kv: kv[1][2], reverse=True)[:40]
    print(f"python calls/cycle={sum(v[1] for v in st.stats.values()) / N:.1f}")
    for (fn, ln, name), (cc, nc, tt, ct, _) in rows:
        print(f"{nc / N:6.2f} {tt * 1e6 / N:7.2f} {ct * 1e6 / N:7.2f}  {fn.replace(str(ROOT) + '/', '')}:{ln}({name})")
ops.cleanup()
