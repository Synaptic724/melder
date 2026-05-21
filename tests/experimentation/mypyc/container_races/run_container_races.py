from __future__ import annotations

import csv
import gc
import importlib
import queue
import statistics
import subprocess
import sys
import sysconfig
import threading
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns


ROOT = Path(__file__).resolve().parent

THREAD_COUNTS = (1, 2, 3, 4, 5)
REPEATS = 5

REQUIRE_NOGIL = True
WRITE_CSV = True
CSV_NAME = "comprehensive_container_thread_safety_results.csv"

FAST_ITERATIONS = 100_000
MEDIUM_ITERATIONS = 30_000
SLOW_ITERATIONS = 3_000
VERY_SLOW_ITERATIONS = 1_000


@dataclass(slots=True)
class TrialResult:
    runtime_name: str
    container_name: str
    operation_name: str
    lock_mode: str
    thread_count: int
    iterations_per_thread: int
    expected_final_size: int
    actual_final_size: int
    exception_count: int
    validation_error_count: int
    elapsed_ns: int

    @property
    def total_operations(self) -> int:
        return self.thread_count * self.iterations_per_thread

    @property
    def elapsed_ms(self) -> float:
        return self.elapsed_ns / 1_000_000

    @property
    def ns_per_op(self) -> float:
        return self.elapsed_ns / self.total_operations

    @property
    def ops_per_second(self) -> float:
        return self.total_operations / (self.elapsed_ns / 1_000_000_000)


def print_gil_state(label: str) -> None:
    print()
    print(f"[{label}]")
    print("python:", sys.version.replace("\n", " "))
    print("executable:", sys.executable)
    print("Py_GIL_DISABLED:", sysconfig.get_config_var("Py_GIL_DISABLED"))

    if hasattr(sys, "_is_gil_enabled"):
        print("sys._is_gil_enabled():", sys._is_gil_enabled())
    else:
        print("sys._is_gil_enabled(): unavailable")


def is_gil_enabled() -> bool:
    if hasattr(sys, "_is_gil_enabled"):
        return bool(sys._is_gil_enabled())

    return True


def require_nogil_runtime() -> None:
    if sysconfig.get_config_var("Py_GIL_DISABLED") != 1:
        print_gil_state("invalid runtime")
        raise SystemExit(
            "\nThis is not a free-threaded Python build.\n"
            "Use Python 3.13t / 3.14t or CPython built with --disable-gil.\n"
        )

    if is_gil_enabled():
        print_gil_state("GIL enabled")
        raise SystemExit(
            "\nThis Python build supports free-threading, but the GIL is enabled.\n"
            "Run one of these:\n"
            "  PYTHON_GIL=0 python run_container_races.py\n"
            "  python -X gil=0 run_container_races.py\n"
        )


def build_extension() -> None:
    print()
    print("[build]")
    print("cwd:", ROOT)
    print("cmd:", sys.executable, "setup.py build_ext --inplace")

    proc = subprocess.run(
        [sys.executable, "setup.py", "build_ext", "--inplace"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=600,
    )

    print(proc.stdout)

    if proc.returncode != 0:
        raise SystemExit(f"mypyc build failed: {proc.returncode}")


def import_modules():
    importlib.invalidate_caches()

    print_gil_state("before imports")

    pure_module = importlib.import_module("container_race_py")
    compiled_module = importlib.import_module("container_race_compiled")

    print_gil_state("after compiled import")

    compiled_file = str(compiled_module.__file__)
    print("compiled module file:", compiled_file)

    if not (compiled_file.endswith(".pyd") or compiled_file.endswith(".so")):
        raise SystemExit(
            "\nPython imported container_race_compiled.py instead of the compiled extension.\n"
            "The test is invalid until it imports .pyd/.so.\n"
        )

    if REQUIRE_NOGIL and is_gil_enabled():
        raise SystemExit(
            "\nImporting the mypyc extension enabled the GIL.\n"
            "This run is invalid for true no-GIL testing.\n"
        )

    return pure_module, compiled_module


def get_validation_error_count(target: object) -> int:
    validator = getattr(target, "validation_error_count", None)

    if validator is None:
        return 0

    value = validator()

    if not isinstance(value, int):
        raise TypeError(f"validation_error_count returned non-int: {value!r}")

    return value


def run_trial(
        target_cls: type,
        use_lock: bool,
        thread_count: int,
        iterations_per_thread: int,
) -> tuple[int, int, int, int]:
    target = target_cls(use_lock)
    total_operations = thread_count * iterations_per_thread

    target.prepare(total_operations)

    barrier = threading.Barrier(thread_count + 1)
    errors: queue.SimpleQueue[BaseException] = queue.SimpleQueue()

    def worker(thread_id: int) -> None:
        try:
            barrier.wait()
            target.worker(thread_id, iterations_per_thread)
        except BaseException as exc:
            errors.put(exc)

    threads = [
        threading.Thread(target=worker, args=(thread_id,))
        for thread_id in range(thread_count)
    ]

    for thread in threads:
        thread.start()

    start = perf_counter_ns()
    barrier.wait()

    for thread in threads:
        thread.join()

    elapsed_ns = perf_counter_ns() - start

    exception_count = 0

    while not errors.empty():
        exception_count += 1
        print("worker exception:", repr(errors.get()))

    actual_final_size = target.final_size()
    validation_error_count = get_validation_error_count(target)

    return elapsed_ns, actual_final_size, exception_count, validation_error_count


def run_case(
        runtime_name: str,
        container_name: str,
        operation_name: str,
        lock_mode: str,
        target_cls: type,
        thread_count: int,
        iterations_per_thread: int,
        expected_final_size: int,
) -> list[TrialResult]:
    results: list[TrialResult] = []
    use_lock = lock_mode == "locked"

    for _ in range(REPEATS):
        elapsed_ns, actual_final_size, exception_count, validation_error_count = run_trial(
            target_cls,
            use_lock,
            thread_count,
            iterations_per_thread,
        )

        results.append(
            TrialResult(
                runtime_name=runtime_name,
                container_name=container_name,
                operation_name=operation_name,
                lock_mode=lock_mode,
                thread_count=thread_count,
                iterations_per_thread=iterations_per_thread,
                expected_final_size=expected_final_size,
                actual_final_size=actual_final_size,
                exception_count=exception_count,
                validation_error_count=validation_error_count,
                elapsed_ns=elapsed_ns,
            )
        )

    return results


def summarize_group(results: list[TrialResult]) -> dict[str, float | int | str]:
    elapsed_ms = [result.elapsed_ms for result in results]
    ns_per_op = [result.ns_per_op for result in results]
    ops_per_second = [result.ops_per_second for result in results]

    first = results[0]

    bad_trials = sum(
        1
        for result in results
        if result.actual_final_size != result.expected_final_size
        or result.exception_count != 0
        or result.validation_error_count != 0
    )

    return {
        "runtime": first.runtime_name,
        "container": first.container_name,
        "operation": first.operation_name,
        "lock_mode": first.lock_mode,
        "threads": first.thread_count,
        "iters_per_thread": first.iterations_per_thread,
        "total_ops": first.total_operations,
        "expected_final_size": first.expected_final_size,
        "repeats": len(results),
        "best_ms": min(elapsed_ms),
        "median_ms": statistics.median(elapsed_ms),
        "mean_ms": statistics.mean(elapsed_ms),
        "best_ns_per_op": min(ns_per_op),
        "median_ns_per_op": statistics.median(ns_per_op),
        "mean_ns_per_op": statistics.mean(ns_per_op),
        "mean_ops_per_sec": statistics.mean(ops_per_second),
        "min_final_size": min(result.actual_final_size for result in results),
        "max_final_size": max(result.actual_final_size for result in results),
        "max_exceptions": max(result.exception_count for result in results),
        "max_validation_errors": max(result.validation_error_count for result in results),
        "bad_trials": bad_trials,
    }


def print_summary_table(summary_rows: list[dict[str, float | int | str]]) -> None:
    print()
    print("SUMMARY")
    print(
        f"{'runtime':<12} "
        f"{'container':<14} "
        f"{'op':<14} "
        f"{'mode':<8} "
        f"{'thr':>3} "
        f"{'ops':>10} "
        f"{'expect':>8} "
        f"{'median ms':>10} "
        f"{'median ns/op':>13} "
        f"{'mean ops/s':>14} "
        f"{'min size':>8} "
        f"{'max size':>8} "
        f"{'max exc':>8} "
        f"{'valid err':>9} "
        f"{'bad':>5}"
    )

    for row in summary_rows:
        print(
            f"{str(row['runtime']):<12} "
            f"{str(row['container']):<14} "
            f"{str(row['operation']):<14} "
            f"{str(row['lock_mode']):<8} "
            f"{int(row['threads']):>3} "
            f"{int(row['total_ops']):>10,} "
            f"{int(row['expected_final_size']):>8} "
            f"{float(row['median_ms']):>10.3f} "
            f"{float(row['median_ns_per_op']):>13.1f} "
            f"{float(row['mean_ops_per_sec']):>14,.0f} "
            f"{int(row['min_final_size']):>8} "
            f"{int(row['max_final_size']):>8} "
            f"{int(row['max_exceptions']):>8} "
            f"{int(row['max_validation_errors']):>9} "
            f"{int(row['bad_trials']):>5}"
        )


def write_csv(summary_rows: list[dict[str, float | int | str]]) -> None:
    path = ROOT / CSV_NAME

    fieldnames = [
        "runtime",
        "container",
        "operation",
        "lock_mode",
        "threads",
        "iters_per_thread",
        "total_ops",
        "expected_final_size",
        "repeats",
        "best_ms",
        "median_ms",
        "mean_ms",
        "best_ns_per_op",
        "median_ns_per_op",
        "mean_ns_per_op",
        "mean_ops_per_sec",
        "min_final_size",
        "max_final_size",
        "max_exceptions",
        "max_validation_errors",
        "bad_trials",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for row in summary_rows:
            writer.writerow(row)

    print()
    print("wrote csv:", path)


def add_cases_for_module(runtime_name: str, module) -> list[tuple[str, str, str, type, str, int]]:
    return [
        (runtime_name, "list", "append", module.ListAppendOnly, "add", FAST_ITERATIONS),
        (runtime_name, "list", "pop_end", module.ListPopEndOnly, "remove", FAST_ITERATIONS),
        (runtime_name, "list", "pop_zero", module.ListPopZeroOnly, "remove", SLOW_ITERATIONS),
        (runtime_name, "list", "insert_zero", module.ListInsertZeroOnly, "add", SLOW_ITERATIONS),
        (runtime_name, "list", "remove_unique", module.ListRemoveUniqueOnly, "remove", VERY_SLOW_ITERATIONS),

        (runtime_name, "deque", "append", module.DequeAppendOnly, "add", FAST_ITERATIONS),
        (runtime_name, "deque", "appendleft", module.DequeAppendLeftOnly, "add", FAST_ITERATIONS),
        (runtime_name, "deque", "pop", module.DequePopOnly, "remove", FAST_ITERATIONS),
        (runtime_name, "deque", "popleft", module.DequePopleftOnly, "remove", FAST_ITERATIONS),

        (runtime_name, "dict", "setitem", module.DictSetOnly, "add", FAST_ITERATIONS),
        (runtime_name, "dict", "pop", module.DictPopOnly, "remove", FAST_ITERATIONS),
        (runtime_name, "dict", "delitem", module.DictDelOnly, "remove", FAST_ITERATIONS),

        (runtime_name, "OrderedDict", "setitem", module.OrderedDictSetOnly, "add", MEDIUM_ITERATIONS),
        (runtime_name, "OrderedDict", "pop", module.OrderedDictPopOnly, "remove", MEDIUM_ITERATIONS),
        (runtime_name, "OrderedDict", "popitem", module.OrderedDictPopItemOnly, "remove", MEDIUM_ITERATIONS),
        (runtime_name, "OrderedDict", "move_to_end", module.OrderedDictMoveToEndOnly, "stable", MEDIUM_ITERATIONS),

        (runtime_name, "set", "add", module.SetAddOnly, "add", FAST_ITERATIONS),
        (runtime_name, "set", "remove", module.SetRemoveOnly, "remove", FAST_ITERATIONS),
        (runtime_name, "set", "discard", module.SetDiscardOnly, "remove", FAST_ITERATIONS),
        (runtime_name, "set", "pop", module.SetPopOnly, "remove", FAST_ITERATIONS),

        (runtime_name, "heapq", "heappush", module.HeapPushOnly, "add", MEDIUM_ITERATIONS),
        (runtime_name, "heapq", "heappop", module.HeapPopOnly, "remove", MEDIUM_ITERATIONS),

        (runtime_name, "array", "append", module.ArrayAppendOnly, "add", FAST_ITERATIONS),
        (runtime_name, "array", "pop", module.ArrayPopOnly, "remove", FAST_ITERATIONS),

        (runtime_name, "bytearray", "append", module.BytearrayAppendOnly, "add", FAST_ITERATIONS),
        (runtime_name, "bytearray", "pop", module.BytearrayPopOnly, "remove", FAST_ITERATIONS),

        (runtime_name, "SimpleQueue", "put", module.SimpleQueuePutOnly, "add", MEDIUM_ITERATIONS),
        (runtime_name, "SimpleQueue", "get", module.SimpleQueueGetOnly, "remove", MEDIUM_ITERATIONS),

        (runtime_name, "Queue", "put", module.QueuePutOnly, "add", MEDIUM_ITERATIONS),
        (runtime_name, "Queue", "get", module.QueueGetOnly, "remove", MEDIUM_ITERATIONS),

        (runtime_name, "LifoQueue", "put", module.LifoQueuePutOnly, "add", MEDIUM_ITERATIONS),
        (runtime_name, "LifoQueue", "get", module.LifoQueueGetOnly, "remove", MEDIUM_ITERATIONS),

        (runtime_name, "PriorityQueue", "put", module.PriorityQueuePutOnly, "add", SLOW_ITERATIONS),
        (runtime_name, "PriorityQueue", "get", module.PriorityQueueGetOnly, "remove", SLOW_ITERATIONS),
    ]


def expected_size_for_kind(operation_kind: str, total_ops: int) -> int:
    if operation_kind == "add":
        return total_ops

    if operation_kind == "remove":
        return 0

    if operation_kind == "stable":
        return total_ops

    raise ValueError(f"unknown operation_kind: {operation_kind!r}")


def run_benchmark(pure_module, compiled_module) -> None:
    cases = []
    cases.extend(add_cases_for_module("pure-python", pure_module))
    cases.extend(add_cases_for_module("mypyc", compiled_module))

    summary_rows: list[dict[str, float | int | str]] = []

    gc_was_enabled = gc.isenabled()
    gc.disable()

    try:
        for thread_count in THREAD_COUNTS:
            print()
            print("=" * 100)
            print(f"THREADS = {thread_count}")
            print("=" * 100)

            for runtime_name, container_name, operation_name, target_cls, operation_kind, iterations_per_thread in cases:
                total_ops = thread_count * iterations_per_thread
                expected_final_size = expected_size_for_kind(operation_kind, total_ops)

                for lock_mode in ("unlocked", "locked"):
                    print(
                        f"running: runtime={runtime_name}, "
                        f"container={container_name}, "
                        f"op={operation_name}, "
                        f"mode={lock_mode}, "
                        f"threads={thread_count}, "
                        f"iters/thread={iterations_per_thread}"
                    )

                    results = run_case(
                        runtime_name,
                        container_name,
                        operation_name,
                        lock_mode,
                        target_cls,
                        thread_count,
                        iterations_per_thread,
                        expected_final_size,
                    )

                    summary = summarize_group(results)
                    summary_rows.append(summary)

                    print(
                        f"  median_ms={float(summary['median_ms']):.3f}, "
                        f"median_ns/op={float(summary['median_ns_per_op']):.1f}, "
                        f"min_size={int(summary['min_final_size'])}, "
                        f"max_size={int(summary['max_final_size'])}, "
                        f"max_exceptions={int(summary['max_exceptions'])}, "
                        f"validation_errors={int(summary['max_validation_errors'])}, "
                        f"bad_trials={int(summary['bad_trials'])}"
                    )

    finally:
        if gc_was_enabled:
            gc.enable()

    print_summary_table(summary_rows)

    if WRITE_CSV:
        write_csv(summary_rows)


def main() -> None:
    print_gil_state("startup")

    if REQUIRE_NOGIL:
        require_nogil_runtime()

    build_extension()
    pure_module, compiled_module = import_modules()
    run_benchmark(pure_module, compiled_module)


if __name__ == "__main__":
    main()