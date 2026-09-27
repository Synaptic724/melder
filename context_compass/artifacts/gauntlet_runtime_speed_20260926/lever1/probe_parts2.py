"""melder_2 probe (no src change): distribution of each piece of the anonymous scope lifecycle, stores populated.

argv: cycles (default 20000)
One worker thread. Even cycles run the public calls (create_lesser_conduit, enter_spellspace, SpellSpace.__exit__,
cleanup) and time each whole call. Odd cycles run the same internal calls those methods make (read from the source,
no-hook and unnamed branches) and time each piece. Every cycle melds the worker_a session into the lesser and the
marker into the spellspace (untimed), so the store resets free real entries. Prints p50, p90 and the 95% trimmed
mean per item in ns. On Windows the timer ticks every 100 ns, so p50/p90 are multiples of 100 and the mean carries
the resolution.
"""
import array, os, statistics, sys, threading, time
from pathlib import Path

ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "tree_0270")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
from melder.aether.conduit.conduit_state.conduit_state import ConduitState

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
ops = g._build_ops("melder")
ops.spawn_singletons()
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
rv = dict(zip(fv["_run_in_lesser_and_spellspace"].__code__.co_freevars,
              (c.cell_contents for c in fv["_run_in_lesser_and_spellspace"].__closure__)))
root, ids = rv["conduit"], rv["spell_ids"]
o_id, m_id = ids[g.WorkerASession], ids[g.WorkerAScopeMarker]
pc = time.perf_counter_ns
full_names = ["FULL_create", "FULL_enter", "FULL_exit", "FULL_cleanup"]
part_names = ["c_check_cleaned", "c_pool_pop", "c_state_sets", "c_link_under_lock",
              "s_acquire", "s_push", "s_pop_expected", "s_reset_unlocked", "s_release",
              "k_lock_pair", "k_spaces_for_pool", "k_creations_reset", "k_detach", "k_state_hooks", "k_pool_return"]
names = full_names + part_names
store = {n: array.array("q", bytes(8 * (N // 2 + 1))) for n in names}
count = {"full": 0, "part": 0}


def full_cycle():
    i = count["full"]
    t0 = pc(); lesser = root.create_lesser_conduit(); t1 = pc()
    lesser.meld(spell_id=o_id)
    t2 = pc(); space = lesser.enter_spellspace(); t3 = pc()
    space.meld(spell_id=m_id)
    t4 = pc(); space.__exit__(None, None, None); t5 = pc()
    t6 = pc(); lesser.cleanup(); t7 = pc()
    for n, v in zip(full_names, (t1 - t0, t3 - t2, t5 - t4, t7 - t6)):
        store[n][i] = v
    count["full"] = i + 1


def part_cycle():
    i = count["part"]
    r = {}
    t0 = pc(); root.check_cleaned(); t1 = pc(); r["c_check_cleaned"] = t1 - t0
    t0 = pc(); new = root._conduit_pool.create_object(); t1 = pc(); r["c_pool_pop"] = t1 - t0
    t0 = pc()
    new._conduit_state = ConduitState.lesser
    new._conduit_ward._conduit_type = ConduitState.lesser
    new._nexus_publish_enabled = root._nexus_publish_enabled
    t1 = pc(); r["c_state_sets"] = t1 - t0
    t0 = pc(); root._link_new_lesser_under_lock(new, name=None); t1 = pc(); r["c_link_under_lock"] = t1 - t0
    new.meld(spell_id=o_id)
    t0 = pc(); space = new._spellspace_pool.acquire_untracked(); t1 = pc(); r["s_acquire"] = t1 - t0
    t0 = pc(); new._spellspace_stack.push(space); t1 = pc(); r["s_push"] = t1 - t0
    space.meld(spell_id=m_id)
    t0 = pc(); space._spellspace_stack_state.pop_expected(space); t1 = pc(); r["s_pop_expected"] = t1 - t0
    t0 = pc(); space._creations.reset_for_pool_unlocked(); t1 = pc(); r["s_reset_unlocked"] = t1 - t0
    t0 = pc(); space._spellspace_pool.release(space); t1 = pc(); r["s_release"] = t1 - t0
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
    for n in part_names:
        store[n][i] = r[n]
    count["part"] = i + 1


def body():
    for _ in range(1000):
        full_cycle(); part_cycle()
    count["full"] = count["part"] = 0
    for _ in range(N // 2):
        full_cycle(); part_cycle()


t = threading.Thread(target=body)
t.start()
t.join()
print(f"melder parts2 cycles={N} (worker thread; p50 / p90 / 95% trimmed mean, ns)")
for n in names:
    s = sorted(store[n][: count["full" if n.startswith("FULL") else "part"]])
    k = len(s)
    tm = statistics.fmean(s[: int(k * 0.95)])
    print(f"  {n:18s} p50={s[k // 2]:6d} p90={s[int(k * 0.9)]:6d} mean={tm:7.0f}")
ops.cleanup()
