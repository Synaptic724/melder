"""melder_2 VM probe (no src change): time each piece of the anonymous scope lifecycle, plus primitives.

Replicates Conduit.create_lesser_conduit (root, no hooks, unnamed) and Conduit.cleanup (pooled lesser, unnamed)
call for call, timing each internal call on one worker thread. Stores stay empty (no melds), so the numbers are
bookkeeping only. Timer overhead (an empty perf_counter_ns pair) is subtracted. Medians in ns.
"""
import collections, os, statistics, sys, threading, time
from pathlib import Path

ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "tree_0270")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
from melder.aether.conduit.conduit_state.conduit_state import ConduitState

ops = g._build_ops("melder")
ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
root = rv["conduit"]
pc = time.perf_counter_ns
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
names = ["full_create", "full_cleanup", "c_check_cleaned", "c_pool_pop", "c_state_sets", "c_link_under_lock",
         "s_acquire", "s_push", "s_pop_expected", "s_reset_unlocked", "s_release",
         "k_lock_pair", "k_spaces_for_pool", "k_creations_reset", "k_detach", "k_state_hooks", "k_pool_return",
         "p_timer", "p_rlock_pair", "p_local_read", "p_deque_pop_append", "p_dict_set_pop", "p_method_call",
         "p_is_attached"]
acc = {n: [] for n in names}


class Dummy:
    def m(self):
        return None


def one():
    r = {}
    t0 = pc(); t1 = pc(); r["p_timer"] = t1 - t0
    # full create + full cleanup (reference)
    t0 = pc(); lesser = root.create_lesser_conduit(); t1 = pc(); r["full_create"] = t1 - t0
    t0 = pc(); lesser.cleanup(); t1 = pc(); r["full_cleanup"] = t1 - t0
    # create, piece by piece (same calls as create_lesser_conduit's no-hook branch)
    t0 = pc(); root.check_cleaned(); t1 = pc(); r["c_check_cleaned"] = t1 - t0
    t0 = pc(); new = root._conduit_pool.create_object(); t1 = pc(); r["c_pool_pop"] = t1 - t0
    assert new is not None
    t0 = pc()
    new._conduit_state = ConduitState.lesser
    new._conduit_ward._conduit_type = ConduitState.lesser
    new._nexus_publish_enabled = root._nexus_publish_enabled
    t1 = pc(); r["c_state_sets"] = t1 - t0
    t0 = pc(); root._link_new_lesser_under_lock(new, name=None); t1 = pc(); r["c_link_under_lock"] = t1 - t0
    # spellspace enter/exit pieces
    t0 = pc(); space = new._spellspace_pool.acquire_untracked(); t1 = pc(); r["s_acquire"] = t1 - t0
    t0 = pc(); new._spellspace_stack.push(space); t1 = pc(); r["s_push"] = t1 - t0
    t0 = pc(); space._spellspace_stack_state.pop_expected(space); t1 = pc(); r["s_pop_expected"] = t1 - t0
    t0 = pc(); space._creations.reset_for_pool_unlocked(); t1 = pc(); r["s_reset_unlocked"] = t1 - t0
    t0 = pc(); space._spellspace_pool.release(space); t1 = pc(); r["s_release"] = t1 - t0
    # cleanup, piece by piece (same calls as cleanup -> _prepare_for_pool for an unnamed pooled lesser)
    t0 = pc()
    with new._lock:
        pass
    t1 = pc(); r["k_lock_pair"] = t1 - t0
    t0 = pc(); new._cleanup_spellspaces_for_pool(); t1 = pc(); r["k_spaces_for_pool"] = t1 - t0
    t0 = pc(); new._creations.reset_for_pool(); t1 = pc(); r["k_creations_reset"] = t1 - t0
    t0 = pc(); new._conduit_ward._detach_for_pool(); t1 = pc(); r["k_detach"] = t1 - t0
    t0 = pc()
    new._conduit_state = ConduitState.pooled_lesser
    new._conduit_ward._conduit_type = ConduitState.pooled_lesser
    if new._local_conduit_hooks is not None:
        new._local_conduit_hooks.clear()
    if new._meld._meld_hooks_modified:
        new._meld._reset_pooled_meld_hooks()
    t1 = pc(); r["k_state_hooks"] = t1 - t0
    t0 = pc(); new._conduit_pool.return_lesser_conduit(new); t1 = pc(); r["k_pool_return"] = t1 - t0
    # primitives
    t0 = pc()
    with PRIM_LOCK:
        pass
    t1 = pc(); r["p_rlock_pair"] = t1 - t0
    t0 = pc(); PRIM_LOCAL.stack; t1 = pc(); r["p_local_read"] = t1 - t0
    t0 = pc(); PRIM_DEQUE.append(PRIM_DEQUE.pop()); t1 = pc(); r["p_deque_pop_append"] = t1 - t0
    t0 = pc(); PRIM_DICT["k"] = 1; PRIM_DICT.pop("k", None); t1 = pc(); r["p_dict_set_pop"] = t1 - t0
    t0 = pc(); PRIM_OBJ.m(); t1 = pc(); r["p_method_call"] = t1 - t0
    t0 = pc(); root._logger.is_attached; t1 = pc(); r["p_is_attached"] = t1 - t0
    return r


PRIM_LOCK = threading.RLock()
PRIM_DEQUE = collections.deque([object()])
PRIM_DICT = {}
PRIM_OBJ = Dummy()


def body():
    global PRIM_LOCAL
    PRIM_LOCAL = threading.local()
    PRIM_LOCAL.stack = []
    for _ in range(2000):
        one()
    for _ in range(N):
        for k, v in one().items():
            acc[k].append(v)


t = threading.Thread(target=body)
t.start()
t.join()
timer = statistics.median(acc["p_timer"])
print(f"worker thread, N={N}, timer pair median={timer:.0f} ns (subtracted below)")
for n in names[:17] + names[18:]:
    print(f"  {n:20s} {statistics.median(acc[n]) - timer:7.0f}")
ops.cleanup()
