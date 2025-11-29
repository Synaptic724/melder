import threading
import time
from statistics import mean

from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.data_structures.concurrent_dict import ConcurrentDict


# How hard to beat them up
OPS_PER_THREAD = 100_000
REPEATS = 5


def bench_plain_list(num_threads: int) -> float:
    """
    list + single external RLock to simulate 'safe' shared access.
    Workload:
      - append
      - read last element
    """
    data = []
    lock = threading.RLock()

    def worker(offset: int) -> None:
        local = 0
        for i in range(OPS_PER_THREAD):
            x = i + offset
            with lock:
                data.append(x)
                local += data[-1]
        # prevent local from being optimized away
        if local == -1:  # never true
            print("impossible")

    threads = [
        threading.Thread(target=worker, args=(t * OPS_PER_THREAD,))
        for t in range(num_threads)
    ]

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    end = time.perf_counter()

    return end - start


def bench_concurrent_list(num_threads: int) -> float:
    """
    ConcurrentList with its own internal lock.
    Same workload as plain_list: append + read last element.
    """
    data = ConcurrentList()

    def worker(offset: int) -> None:
        local = 0
        for i in range(OPS_PER_THREAD):
            x = i + offset
            data.append(x)
            local += data[-1]
        if local == -1:
            print("impossible")

    threads = [
        threading.Thread(target=worker, args=(t * OPS_PER_THREAD,))
        for t in range(num_threads)
    ]

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    end = time.perf_counter()

    return end - start


def bench_plain_dict(num_threads: int) -> float:
    """
    dict + single external RLock.
    Workload:
      - set key
      - read key
    """
    data = {}
    lock = threading.RLock()

    def worker(offset: int) -> None:
        local = 0
        base = offset * 2
        for i in range(OPS_PER_THREAD):
            k = base + i
            with lock:
                data[k] = i
                local += data[k]
        if local == -1:
            print("impossible")

    threads = [
        threading.Thread(target=worker, args=(t * OPS_PER_THREAD,))
        for t in range(num_threads)
    ]

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    end = time.perf_counter()

    return end - start


def bench_concurrent_dict(num_threads: int) -> float:
    """
    ConcurrentDict with its own internal lock.
    Same workload as plain_dict: set + get.
    """
    data = ConcurrentDict({})

    def worker(offset: int) -> None:
        local = 0
        base = offset * 2
        for i in range(OPS_PER_THREAD):
            k = base + i
            data[k] = i
            local += data[k]
        if local == -1:
            print("impossible")

    threads = [
        threading.Thread(target=worker, args=(t * OPS_PER_THREAD,))
        for t in range(num_threads)
    ]

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    end = time.perf_counter()

    return end - start


def run_suite() -> None:
    print(f"OPS_PER_THREAD = {OPS_PER_THREAD}, REPEATS = {REPEATS}")

    for num_threads in (5, 10, 15):
        print("\n" + "=" * 60)
        print(f"Threads: {num_threads}")

        list_times = [bench_plain_list(num_threads) for _ in range(REPEATS)]
        clist_times = [bench_concurrent_list(num_threads) for _ in range(REPEATS)]
        dict_times = [bench_plain_dict(num_threads) for _ in range(REPEATS)]
        cdict_times = [bench_concurrent_dict(num_threads) for _ in range(REPEATS)]

        def summary(label: str, samples: list[float]) -> None:
            avg = mean(samples)
            iters = OPS_PER_THREAD * num_threads
            # each iteration does a write + a read = 2 logical ops
            ops = iters * 2
            ops_per_sec = ops / avg if avg > 0 else float("inf")
            print(
                f"{label:<20} avg={avg:0.6f}s  "
                f"~{ops_per_sec:0.0f} ops/sec (2 ops/iter)"
            )

        summary("list+RLock", list_times)
        summary("ConcurrentList", clist_times)
        summary("dict+RLock", dict_times)
        summary("ConcurrentDict", cdict_times)


if __name__ == "__main__":
    run_suite()
