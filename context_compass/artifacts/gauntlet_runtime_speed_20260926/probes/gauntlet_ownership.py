"""melder_2 VM probe: in the real 3-thread gauntlet, how often does a scope cycle run on a lesser shell (and a
spellspace shell) whose owning thread (ob_tid, free-threaded object header) is not the running thread?"""
import collections, ctypes, sys, threading
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
import dataclasses
def ob_tid(o):
    return ctypes.c_uint64.from_address(id(o)).value
stats = collections.Counter()
orig_build = g._build_ops
def build(lib):
    ops = orig_build(lib)
    fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
    run = fv["_run_in_lesser_and_spellspace"]
    rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
    conduit = rv["conduit"]
    main_tid = threading.get_ident()
    pool = conduit._conduit_pool
    def wrap(name, fn):
        def cycle(variant):
            me = threading.get_ident()
            # the shell this cycle will pop is the pool's top (LIFO); None means a new shell gets built
            try:
                top = pool._idle[-1]
            except IndexError:
                top = None
            if top is None:
                stats[(name, "new shell")] += 1
            else:
                owner = ob_tid(top)
                stats[(name, "own shell" if owner == me else ("main shell" if owner == main_tid else "foreign shell"))] += 1
                try:
                    sp_top = top._spellspace_pool._idle[-1]
                    stats[(name, "own space" if ob_tid(sp_top) == me else "foreign space")] += 1
                except (IndexError, AttributeError):
                    pass
            return fn(variant)
        return cycle
    return dataclasses.replace(ops, request_scope_cycle=wrap("request", ops.request_scope_cycle),
                               worker_a_scope_cycle=wrap("worker_a", ops.worker_a_scope_cycle),
                               worker_b_scope_cycle=wrap("worker_b", ops.worker_b_scope_cycle))
g._build_ops = build
cfg = g._GauntletConfig.from_env()
r = g._run_gauntlet_benchmark("melder", cfg)
for lane in ("request", "worker_a", "worker_b"):
    tot = sum(v for (l, k), v in stats.items() if l == lane and "shell" in k)
    print(lane, {k: f"{v / tot:.0%}" for (l, k), v in sorted(stats.items()) if l == lane and "shell" in k},
          {k: v for (l, k), v in sorted(stats.items()) if l == lane and "space" in k})
