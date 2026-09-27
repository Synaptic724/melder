"""Same call timed on the main thread and on a worker thread (objects built by the main thread).

Run from a tree root with PYTHONPATH=src:. Arg: graph name. Times melder's and dependency-injector's
benchmark get_root(); median of 7 x 200k calls, ns.
"""
import statistics, sys, threading, time, warnings
warnings.simplefilter("ignore")
from benchmarks.testing_other_di import test_overrides_all as bench


def per_call_ns(fn, n=200000):
    samples = []
    for _ in range(7):
        s = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - s) / n)
    return statistics.median(samples)


def in_worker(fn):
    out = []
    t = threading.Thread(target=lambda: out.append(per_call_ns(fn)))
    t.start()
    t.join()
    return out[0]


graph = sys.argv[1]
spec = {g.name: g for g in bench._override_graphs()}[graph]
print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()} graph={graph}")
for lib in ("dependency-injector", "melder"):
    ops = bench._build_override_ops(lib, spec)
    ops.get_root()
    main_ns = per_call_ns(ops.get_root)
    worker_ns = in_worker(ops.get_root)
    print(f"  {lib:20} main thread {main_ns:7.1f} ns | worker thread {worker_ns:7.1f} ns")
    ops.cleanup()
