"""melder_2 VM probe: cost of a cached lesser meld and of a full scope cycle on a worker thread, by who created the
pooled lesser shell: the same thread (own), the live main thread (main), or a thread that has exited (dead)."""
import statistics, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
lane = sys.argv[1] if len(sys.argv) > 1 else "request"
ops = g._build_ops("melder"); ops.spawn_singletons()
cyc = {"request": ops.request_scope_cycle, "worker_a": ops.worker_a_scope_cycle, "worker_b": ops.worker_b_scope_cycle}[lane]
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit, ids = rv["conduit"], rv["spell_ids"]
outer = ids[g.RequestSession]
pool = conduit._conduit_pool
def drain_pool():
    while True:
        try:
            c = pool._idle.pop()
        except IndexError:
            return
        c.permanent_cleanup()
def warm(n=200):
    for i in range(n): cyc(i)
M, NC = 50000, 3000
res = {}
def measure(tag):
    lesser = conduit.create_lesser_conduit()
    lesser.meld(spell_id=outer)
    t0 = time.perf_counter_ns()
    for _ in range(M): lesser.meld(spell_id=outer)
    res.setdefault((tag, "cached lesser meld"), []).append((time.perf_counter_ns() - t0) / M)
    lesser.cleanup()
    t0 = time.perf_counter_ns()
    for i in range(NC): cyc(i)
    res.setdefault((tag, f"{lane} cycle"), []).append((time.perf_counter_ns() - t0) / NC)
def in_thread(fn, *a):
    t = threading.Thread(target=fn, args=a); t.start(); t.join()
for rnd in range(5):
    drain_pool(); in_thread(warm); in_thread(measure, "dead")
    drain_pool(); warm(); in_thread(measure, "main")
    drain_pool()
    def own():
        warm(); measure("own")
    in_thread(own)
for what in ("cached lesser meld", f"{lane} cycle"):
    row = {tag: statistics.median(res[(tag, what)]) for tag in ("own", "main", "dead")}
    print(f"{what:20s} own={row['own']:8,.0f} ns  main={row['main']:8,.0f} ({row['main'] / row['own'] - 1:+.1%})  "
          f"dead={row['dead']:8,.0f} ({row['dead'] / row['own'] - 1:+.1%})")
ops.cleanup()
