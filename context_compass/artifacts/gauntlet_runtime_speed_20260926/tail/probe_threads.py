"""melder_2 VM probe (no src change): does a library's import or world change the cost of short-lived threads?

argv: state threads iters
  state: bare | competitors (import dishka + dependency_injector) | melder (import melder) |
         world_<lib> (harness world built for <lib>: melder, dishka, dependency-injector; setup + 2 gauntlet turns) |
         mainwarm_<lib> (as world_<lib>, but every lane and variant runs once on the main thread first)
Each iteration mirrors the gauntlet driver: create and start N threads, barrier, start_event.set(), each thread runs
the same small workload (40 instantiations of a probe-local class), join. Prints medians and means in microseconds of:
  spawn (thread create+start until the barrier releases), wake (set -> last thread's first statement),
  work (longest per-thread workload), exit_join (last thread's final statement -> all joins returned),
  threaded (set -> all joins returned; the harness's threaded phase).
"""
import os, statistics, sys, threading, time
from pathlib import Path

state, nthreads, iters = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
ROOT = Path(os.environ.get("MELDER_ROOT", str(Path.home() / "work" / "combined")))
for p in (ROOT, ROOT / "src"):
    sys.path.insert(0, str(p))
if state == "competitors":
    import dishka
    import dependency_injector.providers
elif state == "melder":
    import melder
elif state.startswith("world_") or state.startswith("mainwarm_"):
    import benchmarks.testing_other_di.test_real_world_gauntlet as g
    lib = state.split("_", 1)[1]
    ops = g._build_ops(lib)
    ops.spawn_singletons()
    if state.startswith("mainwarm_"):
        # First use on the main thread: every lane and variant once, before any worker thread runs.
        for cycle in (ops.request_scope_cycle, ops.worker_a_scope_cycle, ops.worker_b_scope_cycle):
            for v in range(g._VARIANT_COUNT):
                cycle(v)
    os.environ["DI_GAUNTLET_ITERS"] = "2"
    cfg = g._GauntletConfig.from_env()
    for ix in range(2):
        g._run_gauntlet_once(ops, cfg, ix)


class ProbeObj:
    __slots__ = ("a",)

    def __init__(self, a: int) -> None:
        self.a = a


def workload() -> int:
    acc = 0
    for i in range(40):
        acc += ProbeObj(i).a
    return acc


def one_iteration() -> tuple:
    barrier = threading.Barrier(nthreads + 1)
    start = threading.Event()
    wake = [0] * nthreads
    done = [0] * nthreads

    def make(i: int):
        def run() -> None:
            barrier.wait()
            start.wait()
            wake[i] = time.perf_counter_ns()
            workload()
            done[i] = time.perf_counter_ns()
        return run

    t0 = time.perf_counter_ns()
    threads = [threading.Thread(target=make(i), daemon=True) for i in range(nthreads)]
    for t in threads:
        t.start()
    barrier.wait()
    t_set = time.perf_counter_ns()
    start.set()
    for t in threads:
        t.join()
    t_end = time.perf_counter_ns()
    return (t_set - t0, max(wake) - t_set, max(d - w for d, w in zip(done, wake)), t_end - max(done), t_end - t_set)


for _ in range(300):
    one_iteration()
rows = [one_iteration() for _ in range(iters)]
cols = list(zip(*rows))
names = ("spawn", "wake", "work", "exit_join", "threaded")
med = " ".join(f"{n}={statistics.median(c) / 1000:.1f}" for n, c in zip(names, cols))
mean = " ".join(f"{n}={statistics.fmean(c) / 1000:.1f}" for n, c in zip(names, cols))
print(f"{state:28s} threads={nthreads} iters={iters} | median us: {med} | mean us: {mean}")
