"""
Standalone runner for the shared real-world gauntlet: dependency-injector, dishka and melder.

Modes:
    --lib NAME
        Run one library in this process and print its result. `test_real_world_gauntlet`
        starts the runner this way once per library (and per round), so every library is
        measured in a fresh interpreter. With --result-json PATH the result goes back to
        that parent as JSON, per-turn rows included, and this process writes no per-turn
        CSV; without it the per-turn CSV is written here, as the all-in-one mode does.
    no arguments
        Run all three libraries one after another in this process: the layout used before
        2026-09-30, kept to reproduce earlier baselines. Its numbers depend on the order.
        On free-threaded CPython each library's run leaves starting and joining threads
        slower for the libraries after it, and the gauntlet starts three threads per
        iteration, so a library measured second or third ran 5-12% slower than when it
        ran first. Compare libraries with --lib or the pytest wrapper.

Environment:
    The gauntlet reads DI_GAUNTLET_ITERS, DI_GAUNTLET_THREADS, DI_GAUNTLET_REQUEST_SCOPES,
    DI_GAUNTLET_WORKER_A_JOBS, DI_GAUNTLET_WORKER_B_JOBS, GAUNTLET_PER_TURN_CSV and the other
    GAUNTLET_* instruments in either mode.
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence


def _ensure_repo_paths() -> None:
    """
    Ensure the repo root and src tree are importable for direct runner use.
    """
    current_dir = Path(__file__).resolve().parent
    repo_root = current_dir.parents[1]
    src_dir = repo_root / "src"
    for path in (repo_root, src_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_repo_paths()

import benchmarks.testing_other_di.test_real_world_gauntlet as gauntlet


def _parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    """
    Parse the runner's command line.

    Contract:
        - `--lib` accepts exactly the names of `gauntlet._gauntlet_libraries()`.
        - `--round` and `--result-json` only mean something with `--lib`; given
          without it they are a usage error rather than being ignored.

    Args:
        argv: Arguments without the program name; None reads `sys.argv[1:]`.

    Returns:
        argparse.Namespace: `lib` (None selects the all-in-one mode), `round`
            (>= 1) and `result_json` (None unless a parent asked for a payload).

    Raises:
        SystemExit: argparse's usage error (exit code 2) for an unknown library, a
            round that is not a positive integer, or `--round` / `--result-json`
            without `--lib`.
    """
    parser = argparse.ArgumentParser(description="Run the shared real-world gauntlet.")
    parser.add_argument(
        "--lib",
        choices=gauntlet._gauntlet_libraries(),
        default=None,
        help="run only this library, in this process",
    )
    parser.add_argument(
        "--round",
        type=int,
        default=1,
        help="1-based round number recorded in the result payload (needs --lib)",
    )
    parser.add_argument(
        "--result-json",
        type=Path,
        default=None,
        help="write this library's result payload here instead of the per-turn CSV (needs --lib)",
    )
    args = parser.parse_args(argv)
    if args.round < 1:
        parser.error("--round must be >= 1")
    if args.lib is None and (args.result_json is not None or args.round != 1):
        parser.error("--round and --result-json need --lib")
    return args


def _run_one_library(lib: str, round_number: int, result_json: Optional[Path]) -> int:
    """
    Run one library of the gauntlet in this process and report it.

    Contract:
        - Nothing from the other libraries is imported or run in this process, so
          the result does not depend on them.
        - Prints the result exactly as the all-in-one mode prints each library.
        - With `result_json`, writes `gauntlet._result_payload(result, round_number)`
          there as UTF-8 JSON and leaves the per-turn CSV to the parent; without it,
          writes the per-turn CSV for this one library when `GAUNTLET_PER_TURN_CSV`
          is set.

    Args:
        lib: A name from `gauntlet._gauntlet_libraries()`.
        round_number: 1-based round recorded in the payload.
        result_json: Payload path, or None when the runner is used by hand.

    Returns:
        int: 0. Gauntlet failures propagate as exceptions, which exit non-zero.
    """
    cfg = gauntlet._GauntletConfig.from_env()
    result = gauntlet._run_gauntlet_benchmark(lib, cfg)
    gauntlet._print_benchmark_result(result)
    if result_json is None:
        gauntlet._maybe_write_per_turn_csv([result])
    else:
        payload = gauntlet._result_payload(result, round_number)
        result_json.write_text(json.dumps(payload), encoding="utf-8")
    return 0


def _run_all_in_one_process() -> int:
    """
    Run every library one after another in this process (the layout used before 2026-09-30).

    Contract:
        - Same order, calls and output as before, after one line saying that these
          numbers depend on the order; kept to reproduce earlier baselines.

    Returns:
        int: 0. Gauntlet failures propagate as exceptions, which exit non-zero.
    """
    print(
        "[gauntlet] all libraries share this process, so each result depends on the ones "
        "before it; use --lib NAME or the pytest wrapper for isolated numbers."
    )
    cfg = gauntlet._GauntletConfig.from_env()
    results = []
    for lib in gauntlet._gauntlet_libraries():
        result = gauntlet._run_gauntlet_benchmark(lib, cfg)
        gauntlet._print_benchmark_result(result)
        results.append(result)
    gauntlet._maybe_write_per_turn_csv(results)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Run the gauntlet in the mode the command line selects.

    Args:
        argv: Arguments without the program name; None reads `sys.argv[1:]`.

    Returns:
        int: The process exit code, 0 on success.
    """
    args = _parse_args(argv)
    if args.lib is None:
        return _run_all_in_one_process()
    return _run_one_library(args.lib, args.round, args.result_json)


if __name__ == "__main__":
    raise SystemExit(main())
