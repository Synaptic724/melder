"""melder_2 VM probe (no src change): per-cycle CPU cost with 1 vs 2 concurrent worker threads (2 vCPUs, so two
threads run in parallel without oversubscription). Each thread runs full scope cycles of one lane against the
shared root (Melder) or the shared app container (dishka): outer scope, outer meld x2, request scope, marker meld x2,
inherited outer meld, group, root, cached root, exits. argv: lib lane threads cycles. Prints the per-cycle thread CPU
time (median over 5 blocks, per thread) in ns.
"""
import os, statistics, sys, threading, time
from pathlib import Path

ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "tree_0270")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g

lib, lane, T, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
outer_cls, marker_cls, root_cls, group_cls = {
    "request": (g.RequestSession, g.RequestScopeMarker, g.RequestRoot, g.RequestGroup),
    "worker_a": (g.WorkerASession, g.WorkerAScopeMarker, g.WorkerAJobRoot, g.WorkerAGroup),
    "worker_b": (g.WorkerBSession, g.WorkerBScopeMarker, g.WorkerBJobRoot, g.WorkerBGroup)}[lane]
ops = g._build_ops(lib)
ops.spawn_singletons()


def closure_vars(fn):
    return dict(zip(fn.__code__.co_freevars, (c.cell_contents for c in fn.__closure__)))


if lib == "melder":
    rv = closure_vars(closure_vars(ops.request_scope_cycle)["_run_in_lesser_and_spellspace"])
    conduit, ids = rv["conduit"], rv["spell_ids"]
    o_id, m_id, r_id, gr_id = ids[outer_cls], ids[marker_cls], ids[root_cls], ids[group_cls]

    def cycle():
        lesser = conduit.create_lesser_conduit()
        lesser.meld(spell_id=o_id); lesser.meld(spell_id=o_id)
        cm = lesser.enter_spellspace(); space = cm.__enter__()
        space.meld(spell_id=m_id); space.meld(spell_id=m_id); space.meld(spell_id=o_id)
        space.meld(spell_id=gr_id); space.meld(spell_id=r_id); space.meld(spell_id=r_id)
        cm.__exit__(None, None, None); lesser.cleanup()
else:
    from dishka import Scope
    container = closure_vars(closure_vars(ops.request_scope_cycle)["_run_in_session_and_request_scopes"])["container"]

    def cycle():
        ocm = container(scope=Scope.SESSION); outer = ocm.__enter__()
        outer.get(outer_cls); outer.get(outer_cls)
        rcm = outer(scope=Scope.REQUEST); req = rcm.__enter__()
        req.get(marker_cls); req.get(marker_cls); req.get(outer_cls)
        req.get(group_cls); req.get(root_cls); req.get(root_cls)
        rcm.__exit__(None, None, None); ocm.__exit__(None, None, None)

barrier = threading.Barrier(T)
results = [None] * T


def body(ix):
    for _ in range(1000):
        cycle()
    barrier.wait()
    blocks = []
    for _ in range(5):
        c0 = time.thread_time_ns()
        for _ in range(N):
            cycle()
        blocks.append((time.thread_time_ns() - c0) / N)
    results[ix] = statistics.median(blocks)


threads = [threading.Thread(target=body, args=(i,)) for i in range(T)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"{lib:6s} lane={lane} threads={T} cycles/block={N} | cpu ns/cycle per thread: " + " ".join(f"{r:,.0f}" for r in results))
ops.cleanup()
