"""melder_2 VM probe (no src change): per-step time inside one worker-lane scope cycle, Melder or dishka.

argv: lib (melder | dishka) lane (worker_a | worker_b | request) cycles
Runs on one fresh worker thread, 800 warm-up cycles, then `cycles` timed cycles. Every cycle runs the same steps:
outer scope create, outer meld x2, request scope enter, marker meld x2, inherited outer meld, group build (a
transient group and its leaves), root build (the request-scoped root and everything under it), cached root meld,
request scope exit, outer scope cleanup. Prints the median and mean per step in ns.
"""
import os, statistics, sys, threading, time
from pathlib import Path

ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "tree_0270")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g

lib, lane, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
outer_cls, marker_cls, root_cls, group_cls = {
    "request": (g.RequestSession, g.RequestScopeMarker, g.RequestRoot, g.RequestGroup),
    "worker_a": (g.WorkerASession, g.WorkerAScopeMarker, g.WorkerAJobRoot, g.WorkerAGroup),
    "worker_b": (g.WorkerBSession, g.WorkerBScopeMarker, g.WorkerBJobRoot, g.WorkerBGroup)}[lane]
ops = g._build_ops(lib)
ops.spawn_singletons()


def closure_vars(fn):
    return dict(zip(fn.__code__.co_freevars, (c.cell_contents for c in fn.__closure__)))


pc = time.perf_counter_ns
names = ["outer_create", "outer_1st", "outer_2nd", "req_enter", "marker_1st", "marker_2nd", "outer_inherited",
         "group_build", "root_build", "root_cached", "req_exit", "outer_cleanup"]
if lib == "melder":
    run = closure_vars(ops.request_scope_cycle)["_run_in_lesser_and_spellspace"]
    rv = closure_vars(run)
    conduit, ids = rv["conduit"], rv["spell_ids"]
    o_id, m_id, r_id, gr_id = ids[outer_cls], ids[marker_cls], ids[root_cls], ids[group_cls]

    def cycle():
        t0 = pc(); lesser = conduit.create_lesser_conduit(); t1 = pc()
        lesser.meld(spell_id=o_id); t2 = pc(); lesser.meld(spell_id=o_id); t3 = pc()
        cm = lesser.enter_spellspace(); space = cm.__enter__(); t4 = pc()
        space.meld(spell_id=m_id); t5 = pc(); space.meld(spell_id=m_id); t6 = pc()
        space.meld(spell_id=o_id); t7 = pc()
        space.meld(spell_id=gr_id); t8 = pc()
        space.meld(spell_id=r_id); t9 = pc(); space.meld(spell_id=r_id); t10 = pc()
        cm.__exit__(None, None, None); t11 = pc(); lesser.cleanup(); t12 = pc()
        return (t1 - t0, t2 - t1, t3 - t2, t4 - t3, t5 - t4, t6 - t5, t7 - t6, t8 - t7, t9 - t8, t10 - t9, t11 - t10,
                t12 - t11)
else:
    from dishka import Scope
    run = closure_vars(ops.request_scope_cycle)["_run_in_session_and_request_scopes"]
    container = closure_vars(run)["container"]

    def cycle():
        t0 = pc(); ocm = container(scope=Scope.SESSION); outer = ocm.__enter__(); t1 = pc()
        outer.get(outer_cls); t2 = pc(); outer.get(outer_cls); t3 = pc()
        rcm = outer(scope=Scope.REQUEST); req = rcm.__enter__(); t4 = pc()
        req.get(marker_cls); t5 = pc(); req.get(marker_cls); t6 = pc()
        req.get(outer_cls); t7 = pc()
        req.get(group_cls); t8 = pc()
        req.get(root_cls); t9 = pc(); req.get(root_cls); t10 = pc()
        rcm.__exit__(None, None, None); t11 = pc(); ocm.__exit__(None, None, None); t12 = pc()
        return (t1 - t0, t2 - t1, t3 - t2, t4 - t3, t5 - t4, t6 - t5, t7 - t6, t8 - t7, t9 - t8, t10 - t9, t11 - t10,
                t12 - t11)

acc = {n: [] for n in names}


def body():
    for _ in range(800):
        cycle()
    for _ in range(N):
        for n, d in zip(names, cycle()):
            acc[n].append(d)


t = threading.Thread(target=body)
t.start()
t.join()
meds = {n: statistics.median(acc[n]) for n in names}
tot = sum(meds.values())
print(f"{lib:6s} lane={lane} cycles={N} sum_of_medians={tot:,.0f} ns | " + " ".join(f"{n}={meds[n]:,.0f}" for n in names))
ops.cleanup()
