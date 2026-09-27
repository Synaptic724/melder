"""melder_2 VM experiment (no src change): gauntlet-shaped run (3 new threads per iteration: request x10,
worker_a x25, worker_b x30 cycles) measuring per-thread CPU time per cycle, with the shared lesser/spellspace
pools either as shipped (base) or made thread-affine in-process (affine: each thread reuses shells returned by
threads with its own identity first, then the shared pool). Also counts how often the leased lesser shell was
built by another thread (object-header ob_tid, read with ctypes for measurement only).

usage: probe_affine.py {base|affine} [iterations]
"""
import collections, ctypes, os, statistics, sys, threading, time
from pathlib import Path
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "copy_base")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
from melder.aether.conduit.conduit_pool import ConduitPool
from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool
mode = sys.argv[1]
ITERS = int(sys.argv[2]) if len(sys.argv) > 2 else 300
get_ident = threading.get_ident
census = collections.Counter()
def ob_tid(o):
    return ctypes.c_uint64.from_address(id(o)).value
if mode == "affine":
    by_thread = {}
    orig_create, orig_return = ConduitPool.create_object, ConduitPool.return_lesser_conduit
    orig_acq, orig_rel = SpellSpacePool.acquire_untracked, SpellSpacePool.release
    def create_object(self, *a, **k):
        stack = by_thread.get((id(self), get_ident()))
        if stack:
            return stack.pop()
        return orig_create(self, *a, **k)
    def return_lesser_conduit(self, conduit):
        key = (id(self), get_ident())
        stack = by_thread.get(key)
        if stack is None:
            stack = by_thread.setdefault(key, [])
        if len(stack) < 4:
            stack.append(conduit)
            return
        orig_return(self, conduit)
    def acquire_untracked(self, *a, **k):
        stack = by_thread.get((id(self), get_ident()))
        if stack:
            space = stack.pop()
            if self._conduit_meld._meld_hooks_modified:
                space._meld._inherit_meld_hooks(self._conduit_meld)
            return space
        return orig_acq(self, *a, **k)
    def release(self, obj):
        key = (id(self), get_ident())
        stack = by_thread.get(key)
        if stack is None:
            stack = by_thread.setdefault(key, [])
        if len(stack) < 4:
            stack.append(obj)
            return
        orig_rel(self, obj)
    ConduitPool.create_object = create_object
    ConduitPool.return_lesser_conduit = return_lesser_conduit
    SpellSpacePool.acquire_untracked = acquire_untracked
    SpellSpacePool.release = release
# census: wrap create_object once more (after the optional patch) to see the leased shell's owner
inner_create = ConduitPool.create_object
def census_create(self, *a, **k):
    shell = inner_create(self, *a, **k)
    if shell is None:
        census["new"] += 1
    else:
        census["own" if ob_tid(shell) == get_ident() else "foreign"] += 1
    return shell
ConduitPool.create_object = census_create
ops = g._build_ops("melder"); ops.spawn_singletons()
lanes = [("request", ops.request_scope_cycle, 10), ("worker_a", ops.worker_a_scope_cycle, 25), ("worker_b", ops.worker_b_scope_cycle, 30)]
cpu = collections.defaultdict(list)
def worker(name, call, reps, barrier):
    barrier.wait()
    tt = time.thread_time_ns
    for i in range(reps):
        t0 = tt(); call(i % 3); cpu[name].append(tt() - t0)
wall = []
for it in range(ITERS):
    if it == 20:
        cpu.clear(); census.clear()   # warm-up iterations excluded
    ops.bootstrap_fanout()
    barrier = threading.Barrier(len(lanes))
    ts = [threading.Thread(target=worker, args=(n, c, r, barrier)) for n, c, r in lanes]
    t0 = time.perf_counter_ns()
    [t.start() for t in ts]; [t.join() for t in ts]
    wall.append(time.perf_counter_ns() - t0)
tot = sum(census.values()) or 1
print(mode, f"iters={ITERS}", "  ".join(f"{n}={statistics.fmean(v):,.0f}ns" for n, v in cpu.items()),
      f"| shells own={census['own'] / tot:.0%} foreign={census['foreign'] / tot:.0%} new={census['new']}",
      f"| wall/iter median={statistics.median(wall[20:]) / 1e3:,.0f}us")
ops.cleanup()
