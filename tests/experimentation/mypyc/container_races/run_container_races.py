from __future__ import annotations

import argparse
import csv
import gc
import importlib
import json
import queue
import statistics
import subprocess
import sys
import sysconfig
import threading
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter_ns
from typing import Any


ROOT = Path(__file__).resolve().parent

THREAD_COUNTS = (1, 2, 3, 4, 5)

# Lower than the previous mega-run so this finishes.
# Increase later if you want to stress harder.
FAST_ITERATIONS = 50_000
MEDIUM_ITERATIONS = 10_000
SLOW_ITERATIONS = 1_000
VERY_SLOW_ITERATIONS = 300

REPEATS = 3

CASE_TIMEOUT_SECONDS = 25.0

REQUIRE_NOGIL = True
WRITE_CSV = True
CSV_NAME = "isolated_container_thread_safety_results.csv"

RESULT_PREFIX = "__CONTAINER_RACE_RESULT__:"


@dataclass(slots=True)
class CaseSpec:
    runtime_name: str
    container_name: str
    operation_name: str
    class_name: str
    operation_kind: str
    iterations_per_thread: int
    lock_mode: str
    thread_count: int


@dataclass(slots=True)
class TrialResult:
    actual_final_size: int
    exception_count: int
    validation_error_count: int
    elapsed_ns: int

    @property
    def elapsed_ms(self) -> float:
        return self.elapsed_ns / 1_000_000


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


def import_modules_for_check() -> None:
    importlib.invalidate_caches()

    print_gil_state("before imports")

    importlib.import_module("container_race_py")
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


def get_module(runtime_name: str):
    if runtime_name == "pure-python":
        return importlib.import_module("container_race_py")

    if runtime_name == "mypyc":
        return importlib.import_module("container_race_compiled")

    raise ValueError(f"unknown runtime_name: {runtime_name!r}")


def get_validation_error_count(target: object) -> int:
    validator = getattr(target, "validation_error_count", None)

    if validator is None:
        return 0

    value = validator()

    if not isinstance(value, int):
        raise TypeError(f"validation_error_count returned non-int: {value!r}")

    return value


def expected_size_for_kind(operation_kind: str, total_ops: int) -> int:
    if operation_kind == "add":
        return total_ops

    if operation_kind == "remove":
        return 0

    if operation_kind == "stable":
        return total_ops

    raise ValueError(f"unknown operation_kind: {operation_kind!r}")


def run_trial(
        target_cls: type,
        use_lock: bool,
        thread_count: int,
        iterations_per_thread: int,
) -> TrialResult:
    target = target_cls(use_lock)
    total_operations = thread_count * iterations_per_thread

    target.prepare(total_operations)

    barrier = threading.Barrier(thread_count + 1)
    errors: queue.SimpleQueue[BaseException] = queue.SimpleQueue()

    def thread_worker(thread_id: int) -> None:
        try:
            barrier.wait()
            target.worker(thread_id, iterations_per_thread)
        except BaseException as exc:
            errors.put(exc)

    threads = [
        threading.Thread(target=thread_worker, args=(thread_id,))
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
        exc = errors.get()
        print("worker exception:", repr(exc), file=sys.stderr)

    actual_final_size = target.final_size()
    validation_error_count = get_validation_error_count(target)

    return TrialResult(
        actual_final_size=actual_final_size,
        exception_count=exception_count,
        validation_error_count=validation_error_count,
        elapsed_ns=elapsed_ns,
    )


def run_worker_case(args: argparse.Namespace) -> None:
    if REQUIRE_NOGIL:
        require_nogil_runtime()

    sys.path.insert(0, str(ROOT))
    importlib.invalidate_caches()

    module = get_module(args.runtime_name)

    if args.runtime_name == "mypyc":
        module_file = str(module.__file__)

        if not (module_file.endswith(".pyd") or module_file.endswith(".so")):
            raise SystemExit(
                f"worker imported non-compiled module for mypyc: {module_file}"
            )

        if REQUIRE_NOGIL and is_gil_enabled():
            raise SystemExit("GIL enabled after importing compiled module in worker")

    target_cls = getattr(module, args.class_name)
    use_lock = args.lock_mode == "locked"
    expected_final_size = expected_size_for_kind(
        args.operation_kind,
        args.thread_count * args.iterations_per_thread,
        )

    trial_results: list[TrialResult] = []

    gc_was_enabled = gc.isenabled()
    gc.disable()

    try:
        for _ in range(args.repeats):
            trial_results.append(
                run_trial(
                    target_cls=target_cls,
                    use_lock=use_lock,
                    thread_count=args.thread_count,
                    iterations_per_thread=args.iterations_per_thread,
                )
            )
    finally:
        if gc_was_enabled:
            gc.enable()

    elapsed_ms_values = [result.elapsed_ms for result in trial_results]
    ns_per_op_values = [
        result.elapsed_ns / (args.thread_count * args.iterations_per_thread)
        for result in trial_results
    ]
    ops_per_second_values = [
        (args.thread_count * args.iterations_per_thread) / (result.elapsed_ns / 1_000_000_000)
        for result in trial_results
    ]

    bad_trials = sum(
        1
        for result in trial_results
        if result.actual_final_size != expected_final_size
        or result.exception_count != 0
        or result.validation_error_count != 0
    )

    payload: dict[str, Any] = {
        "status": "ok" if bad_trials == 0 else "bad",
        "runtime": args.runtime_name,
        "container": args.container_name,
        "operation": args.operation_name,
        "lock_mode": args.lock_mode,
        "threads": args.thread_count,
        "iters_per_thread": args.iterations_per_thread,
        "total_ops": args.thread_count * args.iterations_per_thread,
        "expected_final_size": expected_final_size,
        "repeats": args.repeats,
        "best_ms": min(elapsed_ms_values),
        "median_ms": statistics.median(elapsed_ms_values),
        "mean_ms": statistics.mean(elapsed_ms_values),
        "best_ns_per_op": min(ns_per_op_values),
        "median_ns_per_op": statistics.median(ns_per_op_values),
        "mean_ns_per_op": statistics.mean(ns_per_op_values),
        "mean_ops_per_sec": statistics.mean(ops_per_second_values),
        "min_final_size": min(result.actual_final_size for result in trial_results),
        "max_final_size": max(result.actual_final_size for result in trial_results),
        "max_exceptions": max(result.exception_count for result in trial_results),
        "max_validation_errors": max(result.validation_error_count for result in trial_results),
        "bad_trials": bad_trials,
    }

    print(RESULT_PREFIX + json.dumps(payload, sort_keys=True))


def base_cases_for_module(runtime_name: str) -> list[tuple[str, str, str, str, int]]:
    return [
        ("list", "append", "ListAppendOnly", "add", FAST_ITERATIONS),
        ("list", "pop_end", "ListPopEndOnly", "remove", FAST_ITERATIONS),
        ("list", "pop_zero", "ListPopZeroOnly", "remove", SLOW_ITERATIONS),
        ("list", "insert_zero", "ListInsertZeroOnly", "add", SLOW_ITERATIONS),
        ("list", "remove_unique", "ListRemoveUniqueOnly", "remove", VERY_SLOW_ITERATIONS),

        ("deque", "append", "DequeAppendOnly", "add", FAST_ITERATIONS),
        ("deque", "appendleft", "DequeAppendLeftOnly", "add", FAST_ITERATIONS),
        ("deque", "pop", "DequePopOnly", "remove", FAST_ITERATIONS),
        ("deque", "popleft", "DequePopleftOnly", "remove", FAST_ITERATIONS),

        ("dict", "setitem", "DictSetOnly", "add", FAST_ITERATIONS),
        ("dict", "pop", "DictPopOnly", "remove", FAST_ITERATIONS),
        ("dict", "delitem", "DictDelOnly", "remove", FAST_ITERATIONS),

        ("OrderedDict", "setitem", "OrderedDictSetOnly", "add", MEDIUM_ITERATIONS),
        ("OrderedDict", "pop", "OrderedDictPopOnly", "remove", MEDIUM_ITERATIONS),
        ("OrderedDict", "popitem", "OrderedDictPopItemOnly", "remove", MEDIUM_ITERATIONS),
        ("OrderedDict", "move_to_end", "OrderedDictMoveToEndOnly", "stable", MEDIUM_ITERATIONS),

        ("set", "add", "SetAddOnly", "add", FAST_ITERATIONS),
        ("set", "remove", "SetRemoveOnly", "remove", FAST_ITERATIONS),
        ("set", "discard", "SetDiscardOnly", "remove", FAST_ITERATIONS),
        ("set", "pop", "SetPopOnly", "remove", FAST_ITERATIONS),

        ("heapq", "heappush", "HeapPushOnly", "add", MEDIUM_ITERATIONS),
        ("heapq", "heappop", "HeapPopOnly", "remove", MEDIUM_ITERATIONS),

        ("array", "append", "ArrayAppendOnly", "add", FAST_ITERATIONS),
        ("array", "pop", "ArrayPopOnly", "remove", FAST_ITERATIONS),

        ("bytearray", "append", "BytearrayAppendOnly", "add", FAST_ITERATIONS),
        ("bytearray", "pop", "BytearrayPopOnly", "remove", FAST_ITERATIONS),

        ("SimpleQueue", "put", "SimpleQueuePutOnly", "add", MEDIUM_ITERATIONS),
        ("SimpleQueue", "get", "SimpleQueueGetOnly", "remove", MEDIUM_ITERATIONS),

        ("Queue", "put", "QueuePutOnly", "add", MEDIUM_ITERATIONS),
        ("Queue", "get", "QueueGetOnly", "remove", MEDIUM_ITERATIONS),

        ("LifoQueue", "put", "LifoQueuePutOnly", "add", MEDIUM_ITERATIONS),
        ("LifoQueue", "get", "LifoQueueGetOnly", "remove", MEDIUM_ITERATIONS),

        ("PriorityQueue", "put", "PriorityQueuePutOnly", "add", SLOW_ITERATIONS),
        ("PriorityQueue", "get", "PriorityQueueGetOnly", "remove", SLOW_ITERATIONS),
    ]


def build_case_specs() -> list[CaseSpec]:
    specs: list[CaseSpec] = []

    for runtime_name in ("pure-python", "mypyc"):
        for container_name, operation_name, class_name, operation_kind, iterations in base_cases_for_module(runtime_name):
            for thread_count in THREAD_COUNTS:
                for lock_mode in ("unlocked", "locked"):
                    specs.append(
                        CaseSpec(
                            runtime_name=runtime_name,
                            container_name=container_name,
                            operation_name=operation_name,
                            class_name=class_name,
                            operation_kind=operation_kind,
                            iterations_per_thread=iterations,
                            lock_mode=lock_mode,
                            thread_count=thread_count,
                        )
                    )

    return specs


def timeout_for_case(spec: CaseSpec) -> float:
    timeout = CASE_TIMEOUT_SECONDS

    if spec.container_name in {"Queue", "LifoQueue", "PriorityQueue"}:
        timeout *= 2.0

    if spec.container_name in {"OrderedDict", "heapq"}:
        timeout *= 1.5

    if spec.operation_name in {"remove_unique", "pop_zero", "insert_zero"}:
        timeout *= 2.0

    if spec.lock_mode == "locked" and spec.thread_count >= 4:
        timeout *= 1.5

    return min(timeout, 120.0)


def row_from_timeout(spec: CaseSpec, timeout_seconds: float) -> dict[str, Any]:
    total_ops = spec.thread_count * spec.iterations_per_thread
    expected_final_size = expected_size_for_kind(spec.operation_kind, total_ops)

    return {
        "status": "timeout",
        "runtime": spec.runtime_name,
        "container": spec.container_name,
        "operation": spec.operation_name,
        "lock_mode": spec.lock_mode,
        "threads": spec.thread_count,
        "iters_per_thread": spec.iterations_per_thread,
        "total_ops": total_ops,
        "expected_final_size": expected_final_size,
        "repeats": REPEATS,
        "best_ms": "",
        "median_ms": "",
        "mean_ms": "",
        "best_ns_per_op": "",
        "median_ns_per_op": "",
        "mean_ns_per_op": "",
        "mean_ops_per_sec": "",
        "min_final_size": "",
        "max_final_size": "",
        "max_exceptions": "",
        "max_validation_errors": "",
        "bad_trials": REPEATS,
        "timeout_seconds": timeout_seconds,
        "returncode": "",
        "stderr_tail": "TIMEOUT",
    }


def row_from_process_failure(
        spec: CaseSpec,
        returncode: int,
        stdout: str,
        stderr: str,
) -> dict[str, Any]:
    total_ops = spec.thread_count * spec.iterations_per_thread
    expected_final_size = expected_size_for_kind(spec.operation_kind, total_ops)

    return {
        "status": "process-failed",
        "runtime": spec.runtime_name,
        "container": spec.container_name,
        "operation": spec.operation_name,
        "lock_mode": spec.lock_mode,
        "threads": spec.thread_count,
        "iters_per_thread": spec.iterations_per_thread,
        "total_ops": total_ops,
        "expected_final_size": expected_final_size,
        "repeats": REPEATS,
        "best_ms": "",
        "median_ms": "",
        "mean_ms": "",
        "best_ns_per_op": "",
        "median_ns_per_op": "",
        "mean_ns_per_op": "",
        "mean_ops_per_sec": "",
        "min_final_size": "",
        "max_final_size": "",
        "max_exceptions": "",
        "max_validation_errors": "",
        "bad_trials": REPEATS,
        "timeout_seconds": "",
        "returncode": returncode,
        "stderr_tail": (stderr or stdout)[-500:],
    }


def run_parent_case(spec: CaseSpec) -> dict[str, Any]:
    timeout_seconds = timeout_for_case(spec)

    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        "--runtime-name",
        spec.runtime_name,
        "--container-name",
        spec.container_name,
        "--operation-name",
        spec.operation_name,
        "--class-name",
        spec.class_name,
        "--operation-kind",
        spec.operation_kind,
        "--lock-mode",
        spec.lock_mode,
        "--thread-count",
        str(spec.thread_count),
        "--iterations-per-thread",
        str(spec.iterations_per_thread),
        "--repeats",
        str(REPEATS),
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        print("  TIMEOUT")
        if stdout:
            print("  stdout tail:", str(stdout)[-300:])
        if stderr:
            print("  stderr tail:", str(stderr)[-300:])
        return row_from_timeout(spec, timeout_seconds)

    result_payload: dict[str, Any] | None = None

    for line in proc.stdout.splitlines():
        if line.startswith(RESULT_PREFIX):
            result_payload = json.loads(line[len(RESULT_PREFIX):])

    if result_payload is None:
        print("  PROCESS FAILED / NO RESULT")
        if proc.stdout:
            print("  stdout tail:", proc.stdout[-500:])
        if proc.stderr:
            print("  stderr tail:", proc.stderr[-500:])
        return row_from_process_failure(spec, proc.returncode, proc.stdout, proc.stderr)

    result_payload["timeout_seconds"] = timeout_seconds
    result_payload["returncode"] = proc.returncode
    result_payload["stderr_tail"] = proc.stderr[-500:]

    if proc.returncode != 0:
        result_payload["status"] = "process-failed"

    return result_payload


def print_row_brief(row: dict[str, Any]) -> None:
    if row["status"] == "timeout":
        print(
            f"  TIMEOUT after {row['timeout_seconds']:.1f}s"
        )
        return

    if row["status"] == "process-failed":
        print(
            f"  PROCESS FAILED rc={row['returncode']}, "
            f"stderr_tail={row['stderr_tail']!r}"
        )
        return

    print(
        f"  status={row['status']}, "
        f"median_ms={float(row['median_ms']):.3f}, "
        f"median_ns/op={float(row['median_ns_per_op']):.1f}, "
        f"min_size={row['min_final_size']}, "
        f"max_size={row['max_final_size']}, "
        f"max_exceptions={row['max_exceptions']}, "
        f"validation_errors={row['max_validation_errors']}, "
        f"bad_trials={row['bad_trials']}"
    )


def print_summary_table(rows: list[dict[str, Any]]) -> None:
    print()
    print("SUMMARY")
    print(
        f"{'status':<14} "
        f"{'runtime':<12} "
        f"{'container':<14} "
        f"{'op':<14} "
        f"{'mode':<8} "
        f"{'thr':>3} "
        f"{'ops':>10} "
        f"{'expect':>8} "
        f"{'median ms':>10} "
        f"{'median ns/op':>13} "
        f"{'min size':>8} "
        f"{'max size':>8} "
        f"{'max exc':>8} "
        f"{'valid err':>9} "
        f"{'bad':>5}"
    )

    for row in rows:
        print(
            f"{str(row['status']):<14} "
            f"{str(row['runtime']):<12} "
            f"{str(row['container']):<14} "
            f"{str(row['operation']):<14} "
            f"{str(row['lock_mode']):<8} "
            f"{int(row['threads']):>3} "
            f"{int(row['total_ops']):>10,} "
            f"{int(row['expected_final_size']):>8} "
            f"{str(row['median_ms']):>10} "
            f"{str(row['median_ns_per_op']):>13} "
            f"{str(row['min_final_size']):>8} "
            f"{str(row['max_final_size']):>8} "
            f"{str(row['max_exceptions']):>8} "
            f"{str(row['max_validation_errors']):>9} "
            f"{str(row['bad_trials']):>5}"
        )


def write_csv(rows: list[dict[str, Any]]) -> None:
    path = ROOT / CSV_NAME

    fieldnames = [
        "status",
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
        "timeout_seconds",
        "returncode",
        "stderr_tail",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    print()
    print("wrote csv:", path)


def run_parent() -> None:
    print_gil_state("startup")

    if REQUIRE_NOGIL:
        require_nogil_runtime()

    build_extension()
    import_modules_for_check()

    specs = build_case_specs()
    rows: list[dict[str, Any]] = []

    for index, spec in enumerate(specs, start=1):
        print()
        print(
            f"[{index}/{len(specs)}] "
            f"runtime={spec.runtime_name}, "
            f"container={spec.container_name}, "
            f"op={spec.operation_name}, "
            f"mode={spec.lock_mode}, "
            f"threads={spec.thread_count}, "
            f"iters/thread={spec.iterations_per_thread}"
        )

        row = run_parent_case(spec)
        rows.append(row)
        print_row_brief(row)

    print_summary_table(rows)

    if WRITE_CSV:
        write_csv(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--worker", action="store_true")

    parser.add_argument("--runtime-name", default="")
    parser.add_argument("--container-name", default="")
    parser.add_argument("--operation-name", default="")
    parser.add_argument("--class-name", default="")
    parser.add_argument("--operation-kind", default="")
    parser.add_argument("--lock-mode", default="")
    parser.add_argument("--thread-count", type=int, default=0)
    parser.add_argument("--iterations-per-thread", type=int, default=0)
    parser.add_argument("--repeats", type=int, default=1)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.worker:
        run_worker_case(args)
    else:
        run_parent()


if __name__ == "__main__":
    main()