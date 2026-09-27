"""melder_2 VM probe: cost of a full request-lane scope cycle when the pooled lesser (and its spellspace) was
created by ANOTHER thread vs by the running thread (3.14t biased refcounting; no concurrency, one thread runs)."""
import statistics, sys, threading, time
from pathlib import Path
ROOT = Path.home() / "work" / "copy"
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
import benchmarks.testing_other_di.test_real_world_gauntlet as g
lane = sys.argv[1] if len(sys.argv) > 1 else "request"
N = 4000
ops = g._build_ops("melder"); ops.spawn_singletons()
cyc = {"request": ops.request_scope_cycle, "worker_a": ops.worker_a_scope_cycle, "worker_b": ops.worker_b_scope_cycle}[lane]
fv = dict(zip(ops.request_scope_cycle.__code__.co_freevars, (c.cell_contents for c in ops.request_scope_cycle.__closure__)))
run = fv["_run_in_lesser_and_spellspace"]
rv = dict(zip(run.__code__.co_freevars, (c.cell_contents for c in run.__closure__)))
conduit = rv["conduit"]
pool = conduit._conduit_pool
def drain_pool():
    # retire every idle pooled lesser so the next acquisition constructs a fresh shell on the calling thread
    while True:
        try:
            c = pool._idle.pop()
        except IndexError:
            return
        c.permanent_cleanup()
def warm(n):
    for i in range(n): cyc(i)
res = {"own": [], "foreign": []}
def timed(tag):
    s = []
    for _ in range(3):
        t0 = time.perf_counter_ns()
        for i in range(N): cyc(i)
        s.append((time.perf_counter_ns() - t0) / N)
    res[tag].append(statistics.median(s))
for rnd in range(4):
    # foreign: another thread builds the pooled shell, then exits; the measuring thread reuses it
    drain_pool()
    t = threading.Thread(target=warm, args=(300,)); t.start(); t.join()
    t = threading.Thread(target=timed, args=("foreign",)); t.start(); t.join()
    # own: the measuring thread builds the shell itself, then reuses it
    drain_pool()
    def own():
        warm(300); timed("own")
    t = threading.Thread(target=own); t.start(); t.join()
o, f = statistics.median(res["own"]), statistics.median(res["foreign"])
print(f"lane={lane} own={o:,.0f} ns/cycle foreign={f:,.0f} ns/cycle delta={f - o:+,.0f} ({f / o - 1:+.1%})  rounds own={[round(x) for x in res['own']]} foreign={[round(x) for x in res['foreign']]}")
ops.cleanup()
