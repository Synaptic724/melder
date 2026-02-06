import time
from pathlib import Path
from typing import Iterable, Tuple

import pytest


def _run_bool_check(iters: int, flag: bool) -> int:
    """
    Purpose:
        Exercise a simple boolean branch in a tight loop.

    Contract:
        - Returns the number of True branches taken.
        - Does not mutate inputs.

    Args:
        iters: Number of loop iterations to execute.
        flag: Boolean value used in the branch condition.

    Returns:
        int: Count of iterations where the branch executed.
    """
    count = 0
    for _ in range(iters):
        if flag:
            count += 1
    return count


def _run_dict_truthy_check(iters: int, data: dict) -> int:
    """
    Purpose:
        Exercise ``if dict`` truthiness in a tight loop.

    Contract:
        - Returns the number of True branches taken.
        - Does not mutate inputs.

    Args:
        iters: Number of loop iterations to execute.
        data: Dictionary evaluated for truthiness.

    Returns:
        int: Count of iterations where the branch executed.
    """
    count = 0
    for _ in range(iters):
        if data:
            count += 1
    return count


def _run_dict_len_check(iters: int, data: dict) -> int:
    """
    Purpose:
        Exercise ``if len(dict)`` in a tight loop.

    Contract:
        - Returns the number of True branches taken.
        - Does not mutate inputs.

    Args:
        iters: Number of loop iterations to execute.
        data: Dictionary whose length is evaluated.

    Returns:
        int: Count of iterations where the branch executed.
    """
    count = 0
    for _ in range(iters):
        if len(data):
            count += 1
    return count


def _measure_ns(fn, *args) -> Tuple[int, int]:
    """
    Purpose:
        Measure elapsed nanoseconds for a callable and return its result.

    Contract:
        - Uses time.perf_counter_ns for timing.
        - Returns (elapsed_ns, result) without side effects.

    Args:
        fn: Callable to time.
        *args: Positional arguments for the callable.

    Returns:
        Tuple[int, int]: (elapsed_ns, callable_result).
    """
    start_ns = time.perf_counter_ns()
    result = fn(*args)
    end_ns = time.perf_counter_ns()
    return end_ns - start_ns, result


def _write_results(lines: Iterable[str]) -> Path:
    """
    Purpose:
        Persist benchmark results to a dated file for inspection.

    Contract:
        - Creates the output directory if missing.
        - Appends results to a dated file.

    Args:
        lines: Iterable of lines to write.

    Returns:
        Path: The output file path used for the write.
    """
    date_tag = time.strftime("%Y-%m-%d")
    output_dir = Path(
        "benchmarks/competitors/melder_implementation_plan/competitor_lessons/benchmarks"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"bool_vs_len_perf_{date_tag}.txt"
    with output_path.open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{line}\n")
    return output_path


def test_bool_vs_len_perf() -> None:
    """
    Purpose:
        Compare a boolean check versus dict truthiness and len(dict) checks.

    Contract:
        - Runs 10k iterations for each variant.
        - Writes measured averages to a benchmark output file.
        - Asserts the branch count matches the iteration count.
    """
    iters = 10_000
    data = {"key": 1}
    flag = True
    rows = [
        f"bool_vs_len_perf: iters={iters}, timestamp={time.strftime('%Y-%m-%d %H:%M:%S')}"
    ]

    elapsed_ns, count = _measure_ns(_run_bool_check, iters, flag)
    if count != iters:
        raise AssertionError("Bool check iteration count mismatch.")
    rows.append(f"bool_check: total_ns={elapsed_ns}, avg_ns={elapsed_ns / iters:.2f}")
    print(rows[-1])

    elapsed_ns, count = _measure_ns(_run_dict_truthy_check, iters, data)
    if count != iters:
        raise AssertionError("Dict truthiness iteration count mismatch.")
    rows.append(f"dict_truthy: total_ns={elapsed_ns}, avg_ns={elapsed_ns / iters:.2f}")
    print(rows[-1])

    elapsed_ns, count = _measure_ns(_run_dict_len_check, iters, data)
    if count != iters:
        raise AssertionError("Dict len iteration count mismatch.")
    rows.append(f"dict_len: total_ns={elapsed_ns}, avg_ns={elapsed_ns / iters:.2f}")
    print(rows[-1])

    output_path = _write_results(rows)
    assert output_path.exists()
