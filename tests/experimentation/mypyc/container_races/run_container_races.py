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
ITERATIONS_PER_THREAD = 100_000
REPEATS = 5

REQUIRE_NOGIL = True
WRITE_CSV = True
CSV_NAME = "container_thread_safety_results.csv"


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
        timeout=240,
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


def run_trial(
        target_cls: type,
        thread_count: int,
        iterations_per_thread: int,
        expected_final_size: int,
) -> tuple[int, int, int]:
    target = target_cls()
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

    return elapsed_ns, actual_final_size, exception_count


def run_case(
        runtime_name: str,
        container_name: str,
        operation_name: str,
        lock_mode: str,
        target_cls: type,
        thread_count: int,
        expected_final_size: int,
) -> list[TrialResult]:
    results: list[TrialResult] = []

    for _ in range(REPEATS):
        elapsed_ns, actual_final_size, exception_count = run_trial(
            target_cls,
            thread_count,
            ITERATIONS_PER_THREAD,
            expected_final_size,
        )

        results.append(
            TrialResult(
                runtime_name=runtime_name,
                container_name=container_name,
                operation_name=operation_name,
                lock_mode=lock_mode,
                thread_count=thread_count,
                iterations_per_thread=ITERATIONS_PER_THREAD,
                expected_final_size=expected_final_size,
                actual_final_size=actual_final_size,
                exception_count=exception_count,
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
        "bad_trials": bad_trials,
    }


def print_summary_table(summary_rows: list[dict[str, float | int | str]]) -> None:
    print()
    print("SUMMARY")
    print(
        f"{'runtime':<12} "
        f"{'container':<8} "
        f"{'op':<8} "
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
        f"{'bad':>5}"
    )

    for row in summary_rows:
        print(
            f"{str(row['runtime']):<12} "
            f"{str(row['container']):<8} "
            f"{str(row['operation']):<8} "
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
        "bad_trials",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for row in summary_rows:
            writer.writerow(row)

    print()
    print("wrote csv:", path)


def run_benchmark(pure_module, compiled_module) -> None:
    cases = [
        ("pure-python", "list", "append", "unlocked", pure_module.UnlockedListAppendOnly, "add"),
        ("pure-python", "list", "append", "locked", pure_module.LockedListAppendOnly, "add"),
        ("pure-python", "list", "pop", "unlocked", pure_module.UnlockedListPopOnly, "remove"),
        ("pure-python", "list", "pop", "locked", pure_module.LockedListPopOnly, "remove"),

        ("pure-python", "deque", "append", "unlocked", pure_module.UnlockedDequeAppendOnly, "add"),
        ("pure-python", "deque", "append", "locked", pure_module.LockedDequeAppendOnly, "add"),
        ("pure-python", "deque", "popleft", "unlocked", pure_module.UnlockedDequePopOnly, "remove"),
        ("pure-python", "deque", "popleft", "locked", pure_module.LockedDequePopOnly, "remove"),

        ("pure-python", "dict", "set", "unlocked", pure_module.UnlockedDictSetOnly, "add"),
        ("pure-python", "dict", "set", "locked", pure_module.LockedDictSetOnly, "add"),
        ("pure-python", "dict", "pop", "unlocked", pure_module.UnlockedDictPopOnly, "remove"),
        ("pure-python", "dict", "pop", "locked", pure_module.LockedDictPopOnly, "remove"),

        ("mypyc", "list", "append", "unlocked", compiled_module.UnlockedListAppendOnly, "add"),
        ("mypyc", "list", "append", "locked", compiled_module.LockedListAppendOnly, "add"),
        ("mypyc", "list", "pop", "unlocked", compiled_module.UnlockedListPopOnly, "remove"),
        ("mypyc", "list", "pop", "locked", compiled_module.LockedListPopOnly, "remove"),

        ("mypyc", "deque", "append", "unlocked", compiled_module.UnlockedDequeAppendOnly, "add"),
        ("mypyc", "deque", "append", "locked", compiled_module.LockedDequeAppendOnly, "add"),
        ("mypyc", "deque", "popleft", "unlocked", compiled_module.UnlockedDequePopOnly, "remove"),
        ("mypyc", "deque", "popleft", "locked", compiled_module.LockedDequePopOnly, "remove"),

        ("mypyc", "dict", "set", "unlocked", compiled_module.UnlockedDictSetOnly, "add"),
        ("mypyc", "dict", "set", "locked", compiled_module.LockedDictSetOnly, "add"),
        ("mypyc", "dict", "pop", "unlocked", compiled_module.UnlockedDictPopOnly, "remove"),
        ("mypyc", "dict", "pop", "locked", compiled_module.LockedDictPopOnly, "remove"),
    ]

    summary_rows: list[dict[str, float | int | str]] = []

    gc_was_enabled = gc.isenabled()
    gc.disable()

    try:
        for thread_count in THREAD_COUNTS:
            print()
            print("=" * 80)
            print(f"THREADS = {thread_count}")
            print("=" * 80)

            total_ops = thread_count * ITERATIONS_PER_THREAD

            for runtime_name, container_name, operation_name, lock_mode, target_cls, operation_kind in cases:
                if operation_kind == "add":
                    expected_final_size = total_ops
                else:
                    expected_final_size = 0

                print(
                    f"running: runtime={runtime_name}, "
                    f"container={container_name}, "
                    f"op={operation_name}, "
                    f"mode={lock_mode}, "
                    f"threads={thread_count}"
                )

                results = run_case(
                    runtime_name,
                    container_name,
                    operation_name,
                    lock_mode,
                    target_cls,
                    thread_count,
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