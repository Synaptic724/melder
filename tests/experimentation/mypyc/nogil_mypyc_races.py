from __future__ import annotations

import gc
import importlib
import queue
import statistics
import subprocess
import sys
import sysconfig
import threading
from pathlib import Path
from time import perf_counter_ns


ROOT = Path(__file__).resolve().parent

THREAD_COUNT = 3

REQUIRE_NOGIL = True

BARRIER_TRIALS = 1_000
BARRIER_LIMIT = 1
BARRIER_SPIN = 50_000

HOT_LOOP_TRIALS = 200
HOT_LOOP_LIMIT = 1_000
HOT_LOOP_ITERATIONS_PER_THREAD = 5_000
HOT_LOOP_SPIN = 1_000

COUNTER_TRIALS = 100
COUNTER_ITERATIONS_PER_THREAD = 20_000
COUNTER_SPIN = 200


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
            "Use Python 3.13t / 3.14t or a CPython build configured with --disable-gil.\n"
        )

    if is_gil_enabled():
        print_gil_state("GIL enabled")
        raise SystemExit(
            "\nThis Python build supports free-threading, but the GIL is enabled.\n"
            "Run one of these:\n"
            "  PYTHON_GIL=0 python nogil_mypyc_races.py\n"
            "  python -X gil=0 nogil_mypyc_races.py\n"
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


def import_compiled_module():
    importlib.invalidate_caches()

    print_gil_state("before compiled import")

    module = importlib.import_module("list_race_target")

    print_gil_state("after compiled import")

    module_file = str(module.__file__)
    print("module file:", module_file)

    if not (module_file.endswith(".pyd") or module_file.endswith(".so")):
        raise SystemExit(
            "\nPython imported the .py file, not the compiled extension.\n"
            "The test is invalid until it imports the compiled .pyd/.so module.\n"
        )

    if REQUIRE_NOGIL and is_gil_enabled():
        raise SystemExit(
            "\nImporting the mypyc extension enabled the GIL.\n"
            "That means this mypyc extension/runtime is not running in true no-GIL mode.\n"
            "The race test is invalid until the GIL stays disabled after import.\n"
        )

    return module


def run_barrier_limit_trial(target_cls: type) -> int:
    target = target_cls(BARRIER_LIMIT, BARRIER_SPIN)
    barrier = threading.Barrier(THREAD_COUNT + 1)
    errors: queue.SimpleQueue[BaseException] = queue.SimpleQueue()

    def worker(thread_id: int) -> None:
        try:
            barrier.wait()
            target.try_append_once(thread_id)
        except BaseException as exc:
            errors.put(exc)

    threads = [
        threading.Thread(target=worker, args=(thread_id,))
        for thread_id in range(THREAD_COUNT)
    ]

    for thread in threads:
        thread.start()

    barrier.wait()

    for thread in threads:
        thread.join()

    if not errors.empty():
        raise errors.get()

    return target.current_length()


def run_hot_loop_limit_trial(target_cls: type) -> int:
    target = target_cls(HOT_LOOP_LIMIT, HOT_LOOP_SPIN)
    barrier = threading.Barrier(THREAD_COUNT + 1)
    errors: queue.SimpleQueue[BaseException] = queue.SimpleQueue()

    def worker(thread_id: int) -> None:
        try:
            barrier.wait()
            target.hammer_append(thread_id, HOT_LOOP_ITERATIONS_PER_THREAD)
        except BaseException as exc:
            errors.put(exc)

    threads = [
        threading.Thread(target=worker, args=(thread_id,))
        for thread_id in range(THREAD_COUNT)
    ]

    for thread in threads:
        thread.start()

    barrier.wait()

    for thread in threads:
        thread.join()

    if not errors.empty():
        raise errors.get()

    return target.current_length()


def run_counter_trial(target_cls: type) -> int:
    target = target_cls(COUNTER_SPIN)
    barrier = threading.Barrier(THREAD_COUNT + 1)
    errors: queue.SimpleQueue[BaseException] = queue.SimpleQueue()

    def worker() -> None:
        try:
            barrier.wait()
            target.hammer_increment(COUNTER_ITERATIONS_PER_THREAD)
        except BaseException as exc:
            errors.put(exc)

    threads = [
        threading.Thread(target=worker)
        for _ in range(THREAD_COUNT)
    ]

    for thread in threads:
        thread.start()

    barrier.wait()

    for thread in threads:
        thread.join()

    if not errors.empty():
        raise errors.get()

    return target.current_value()


def summarize_overshoot_case(name: str, values: list[int], limit: int) -> None:
    overshoots = sum(1 for value in values if value > limit)
    exact = sum(1 for value in values if value == limit)
    below = sum(1 for value in values if value < limit)

    print()
    print(name)
    print("  trials:", len(values))
    print("  limit:", limit)
    print("  min:", min(values))
    print("  mean:", f"{statistics.mean(values):.2f}")
    print("  max:", max(values))
    print("  exact:", exact)
    print("  below:", below)
    print("  overshoots:", overshoots)

    if overshoots:
        print("  RESULT: RACE DETECTED")
    else:
        print("  RESULT: no overshoot observed")


def summarize_lost_update_case(name: str, values: list[int], expected: int) -> None:
    lost_updates = sum(1 for value in values if value < expected)
    exact = sum(1 for value in values if value == expected)
    above = sum(1 for value in values if value > expected)

    print()
    print(name)
    print("  trials:", len(values))
    print("  expected:", expected)
    print("  min:", min(values))
    print("  mean:", f"{statistics.mean(values):.2f}")
    print("  max:", max(values))
    print("  exact:", exact)
    print("  above:", above)
    print("  lost-update races:", lost_updates)

    if lost_updates:
        print("  RESULT: RACE DETECTED")
    else:
        print("  RESULT: no lost updates observed")


def run_race_tests(module) -> None:
    limit_cls = module.SharedListLimitRace
    counter_cls = module.SharedListCounterRace

    gc_was_enabled = gc.isenabled()
    gc.disable()

    try:
        barrier_lengths: list[int] = []
        hot_loop_lengths: list[int] = []
        counter_values: list[int] = []

        start = perf_counter_ns()
        for _ in range(BARRIER_TRIALS):
            barrier_lengths.append(run_barrier_limit_trial(limit_cls))
        barrier_elapsed = perf_counter_ns() - start

        start = perf_counter_ns()
        for _ in range(HOT_LOOP_TRIALS):
            hot_loop_lengths.append(run_hot_loop_limit_trial(limit_cls))
        hot_loop_elapsed = perf_counter_ns() - start

        start = perf_counter_ns()
        for _ in range(COUNTER_TRIALS):
            counter_values.append(run_counter_trial(counter_cls))
        counter_elapsed = perf_counter_ns() - start

    finally:
        if gc_was_enabled:
            gc.enable()

    summarize_overshoot_case(
        "barrier check-then-append race",
        barrier_lengths,
        BARRIER_LIMIT,
    )
    print("  elapsed ms:", f"{barrier_elapsed / 1_000_000:.3f}")

    summarize_overshoot_case(
        "hot-loop check-then-append race",
        hot_loop_lengths,
        HOT_LOOP_LIMIT,
    )
    print("  elapsed ms:", f"{hot_loop_elapsed / 1_000_000:.3f}")

    summarize_lost_update_case(
        "list[0] read-modify-write counter race",
        counter_values,
        THREAD_COUNT * COUNTER_ITERATIONS_PER_THREAD,
        )
    print("  elapsed ms:", f"{counter_elapsed / 1_000_000:.3f}")


def main() -> None:
    print_gil_state("startup")

    if REQUIRE_NOGIL:
        require_nogil_runtime()

    build_extension()
    module = import_compiled_module()
    run_race_tests(module)


if __name__ == "__main__":
    main()