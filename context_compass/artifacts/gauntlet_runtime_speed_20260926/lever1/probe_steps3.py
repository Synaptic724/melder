"""melder_2 probe (no src change): per-step cost of a scope cycle with T concurrent worker threads, Melder or dishka.

argv: lib (melder | dishka) lane (worker_a | worker_b | request) threads cycles
Each of the T threads runs the same lane against the shared root conduit (Melder) or the shared app container
(dishka): 600 warm-up cycles, a barrier, then `cycles` timed cycles. Steps are timed with perf_counter_ns. Windows'
100 ns timer quantization is averaged out by a trimmed mean per step: samples above the step's 95th percentile are
dropped, which also removes preemption spikes. Also prints the wall time per cycle of each thread (its whole timed
loop divided by cycles, per-step timer calls and recording included; nothing GC-tracked is retained), the request-window sum (enter through exit) and the
lifecycle sum (create, enter, exit, cleanup). All values are ns.
"""
import array, os, statistics, sys, threading, time
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


pc = time.perf_counter_ns
names = ["outer_create", "outer_1st", "outer_2nd", "req_enter", "marker_1st", "marker_2nd", "outer_inherited",
         "group_build", "root_build", "root_cached", "req_exit", "outer_cleanup"]
if lib == "melder":
    rv = closure_vars(closure_vars(ops.request_scope_cycle)["_run_in_lesser_and_spellspace"])
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
    container = closure_vars(closure_vars(ops.request_scope_cycle)["_run_in_session_and_request_scopes"])["container"]

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

barrier = threading.Barrier(T)
samples = [None] * T
walls = [0.0] * T


def body(ix):
    for _ in range(600):
        cycle()
    # One preallocated int64 array per step: the timed loop retains no GC-tracked objects, so the probe itself
    # does not trigger collections inside the measurement.
    cols_ix = [array.array("q", bytes(8 * N)) for _ in names]
    barrier.wait()
    w0 = pc()
    for i in range(N):
        for col, value in zip(cols_ix, cycle()):
            col[i] = value
    walls[ix] = (pc() - w0) / N
    samples[ix] = cols_ix


threads = [threading.Thread(target=body, args=(i,)) for i in range(T)]
for t in threads:
    t.start()
for t in threads:
    t.join()
cols = [[v for per_thread in samples for v in per_thread[k]] for k in range(len(names))]


def trimmed_mean(values):
    s = sorted(values)
    return statistics.fmean(s[: max(1, int(len(s) * 0.95))])


tm = {n: trimmed_mean(c) for n, c in zip(names, cols)}
window = sum(tm[n] for n in names[3:11])
lifecycle = tm["outer_create"] + tm["req_enter"] + tm["req_exit"] + tm["outer_cleanup"]
print(f"{lib:6s} lane={lane} threads={T} cycles={N} | wall/cycle " + " ".join(f"{w:,.0f}" for w in walls)
      + f" | window={window:,.0f} lifecycle={lifecycle:,.0f} | " + " ".join(f"{n}={tm[n]:,.0f}" for n in names))
ops.cleanup()
