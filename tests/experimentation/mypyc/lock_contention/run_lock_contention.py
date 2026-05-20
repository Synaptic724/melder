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
REPEATS = 7

REQUIRE_NOGIL = True
WRITE_CSV = True
CSV_NAME = "lock_contention_results.csv"


@dataclass(slots=True)
class TrialResult:
    runtime_name: str
    lock_name: str
    thread_count: int
    iterations_per_thread: int
    total_operations: int
    final_counter: int
    elapsed_ns: int

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
            "  PYTHON_GIL=0 python run_lock_contention.py\n"
            "  python -X gil=0 run_lock_contention.py\n"
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

    pure_module = importlib.import_module("lock_contention_py")
    compiled_module = importlib.import_module("lock_contention_compiled")

    print_gil_state("after compiled import")

    compiled_file = str(compiled_module.__file__)
    print("compiled module file:", compiled_file)

    if not (compiled_file.endswith(".pyd") or compiled_file.endswith(".so")):
        raise SystemExit(
            "\nPython imported lock_contention_compiled.py instead of the compiled extension.\n"
            "The test is invalid until it imports .pyd/.so.\n"
        )

    if REQUIRE_NOGIL and is_gil_enabled():
        raise SystemExit(
            "\nImporting the mypyc extension enabled the GIL.\n"
            "This run is invalid for true no-GIL contention testing.\n"
        )

    return pure_module, compiled_module


def run_counter_trial(
        counter_cls: type,
        thread_count: int,
        iterations_per_thread: int,
) -> tuple[int, int]:
    counter = counter_cls()
    barrier = threading.Barrier(thread_count + 1)
    errors: queue.SimpleQueue[BaseException] = queue.SimpleQueue()

    def worker() -> None:
        try:
            barrier.wait()
            counter.increment_many(iterations_per_thread)
        except BaseException as exc:
            errors.put(exc)

    threads = [
        threading.Thread(target=worker)
        for _ in range(thread_count)
    ]

    for thread in threads:
        thread.start()

    start = perf_counter_ns()
    barrier.wait()

    for thread in threads:
        thread.join()

    elapsed_ns = perf_counter_ns() - start

    if not errors.empty():
        raise errors.get()

    return elapsed_ns, counter.current_value()


def run_case(
        runtime_name: str,
        lock_name: str,
        counter_cls: type,
        thread_count: int,
) -> list[TrialResult]:
    results: list[TrialResult] = []
    total_operations = thread_count * ITERATIONS_PER_THREAD

    for _ in range(REPEATS):
        elapsed_ns, final_counter = run_counter_trial(
            counter_cls,
            thread_count,
            ITERATIONS_PER_THREAD,
        )

        if final_counter != total_operations:
            raise RuntimeError(
                f"counter mismatch: runtime={runtime_name}, "
                f"lock={lock_name}, threads={thread_count}, "
                f"expected={total_operations}, actual={final_counter}"
            )

        results.append(
            TrialResult(
                runtime_name=runtime_name,
                lock_name=lock_name,
                thread_count=thread_count,
                iterations_per_thread=ITERATIONS_PER_THREAD,
                total_operations=total_operations,
                final_counter=final_counter,
                elapsed_ns=elapsed_ns,
            )
        )

    return results


def summarize_group(results: list[TrialResult]) -> dict[str, float | int | str]:
    elapsed_ms = [result.elapsed_ms for result in results]
    ns_per_op = [result.ns_per_op for result in results]
    ops_per_second = [result.ops_per_second for result in results]

    first = results[0]

    return {
        "runtime": first.runtime_name,
        "lock": first.lock_name,
        "threads": first.thread_count,
        "iters_per_thread": first.iterations_per_thread,
        "total_ops": first.total_operations,
        "repeats": len(results),
        "best_ms": min(elapsed_ms),
        "median_ms": statistics.median(elapsed_ms),
        "mean_ms": statistics.mean(elapsed_ms),
        "best_ns_per_op": min(ns_per_op),
        "median_ns_per_op": statistics.median(ns_per_op),
        "mean_ns_per_op": statistics.mean(ns_per_op),
        "best_ops_per_sec": max(ops_per_second),
        "median_ops_per_sec": statistics.median(ops_per_second),
        "mean_ops_per_sec": statistics.mean(ops_per_second),
    }


def print_summary_table(summary_rows: list[dict[str, float | int | str]]) -> None:
    print()
    print("SUMMARY")
    print(
        f"{'runtime':<12} "
        f"{'lock':<8} "
        f"{'thr':>3} "
        f"{'ops':>10} "
        f"{'best ms':>10} "
        f"{'median ms':>10} "
        f"{'mean ms':>10} "
        f"{'best ns/op':>12} "
        f"{'median ns/op':>13} "
        f"{'mean ns/op':>12} "
        f"{'mean ops/s':>14}"
    )

    for row in summary_rows:
        print(
            f"{str(row['runtime']):<12} "
            f"{str(row['lock']):<8} "
            f"{int(row['threads']):>3} "
            f"{int(row['total_ops']):>10,} "
            f"{float(row['best_ms']):>10.3f} "
            f"{float(row['median_ms']):>10.3f} "
            f"{float(row['mean_ms']):>10.3f} "
            f"{float(row['best_ns_per_op']):>12.1f} "
            f"{float(row['median_ns_per_op']):>13.1f} "
            f"{float(row['mean_ns_per_op']):>12.1f} "
            f"{float(row['mean_ops_per_sec']):>14,.0f}"
        )


def write_csv(summary_rows: list[dict[str, float | int | str]]) -> None:
    path = ROOT / CSV_NAME

    fieldnames = [
        "runtime",
        "lock",
        "threads",
        "iters_per_thread",
        "total_ops",
        "repeats",
        "best_ms",
        "median_ms",
        "mean_ms",
        "best_ns_per_op",
        "median_ns_per_op",
        "mean_ns_per_op",
        "best_ops_per_sec",
        "median_ops_per_sec",
        "mean_ops_per_sec",
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
        ("pure-python", "Lock", pure_module.LockCounter),
        ("pure-python", "RLock", pure_module.RLockCounter),
        ("mypyc", "Lock", compiled_module.LockCounter),
        ("mypyc", "RLock", compiled_module.RLockCounter),
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

            for runtime_name, lock_name, counter_cls in cases:
                print(
                    f"running: runtime={runtime_name}, "
                    f"lock={lock_name}, "
                    f"threads={thread_count}"
                )

                results = run_case(
                    runtime_name,
                    lock_name,
                    counter_cls,
                    thread_count,
                )

                summary = summarize_group(results)
                summary_rows.append(summary)

                print(
                    f"  median_ms={float(summary['median_ms']):.3f}, "
                    f"median_ns/op={float(summary['median_ns_per_op']):.1f}, "
                    f"mean_ops/s={float(summary['mean_ops_per_sec']):,.0f}"
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