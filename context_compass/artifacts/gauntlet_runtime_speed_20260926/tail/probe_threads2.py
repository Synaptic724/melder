"""melder_2 VM probe (no src change): is short-lived thread exit cost driven by live objects left behind by exited threads?

argv: state threads iters
  state: bare | main_<N> (main thread allocates N live instances) | abandoned_<N> (a worker thread allocates N live
         instances, hands them to main and exits) | abandoned4_<N> (four workers each allocate N/4 and exit)
Same per-iteration shape as probe_threads.py; prints medians/means in microseconds.
"""
import statistics, sys, threading, time

state, nthreads, iters = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])


class Held:
    __slots__ = ("a", "b")

    def __init__(self, a: int) -> None:
        self.a = a
        self.b = [a]


keep: list = []


def alloc(n: int) -> None:
    keep.append([Held(i) for i in range(n)])


if state.startswith("main_"):
    alloc(int(state.split("_")[1]))
elif state.startswith("abandoned_") or state.startswith("abandoned4_"):
    n = int(state.split("_")[1])
    parts = 4 if state.startswith("abandoned4_") else 1
    for _ in range(parts):
        t = threading.Thread(target=alloc, args=(n // parts,))
        t.start()
        t.join()


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
print(f"{state:22s} threads={nthreads} iters={iters} | median us: {med}")
