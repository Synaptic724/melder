"""
Profile the melder gauntlet hot path under cProfile.

Purpose:
    Attribute the per-iteration meld cost (the gauntlet's ~1.35ms/iter median)
    to concrete functions so hot-path work targets measured cost, not guesses.

Usage:
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_melder_hot_path.py

Contract:
    - cProfile is not usable on a GIL-disabled interpreter, so this script
      re-execs itself under `PYTHON_GIL=1` when it detects a free-threaded
      run. Lock-contention costs are therefore underrepresented in the
      report; CPU attribution (the thing we are hunting) remains valid.
    - Reuses the exact gauntlet workload builder from `test_melder_gauntlet`.
    - Runs warmup iterations first so phases 8-11, hydration, and the
      process-wide executor caches are all hot before profiling starts;
      the profile window therefore measures steady-state melds only.
    - cProfile inflates absolute times (~2x); only the RELATIVE attribution
      matters here.
    - Writes the full report to `melder_hot_path_profile.txt` next to this
      script and prints the top sections to stdout.
"""

import cProfile
import io
import os
import pstats
import sys
from pathlib import Path


def _ensure_gil_enabled_interpreter() -> None:
    """
    Re-exec this script under a GIL-enabled interpreter when needed.

    Contract:
        - cProfile breaks on GIL-disabled (free-threaded) interpreters, and
          the GIL cannot be re-enabled inside a running process, so the only
          correct move is re-exec with `PYTHON_GIL=1` before any profiling.
        - `sys._is_gil_enabled` is a capability probe on an interpreter
          surface that varies by build; absent means a GIL build.
    """
    is_gil_enabled_probe = getattr(sys, "_is_gil_enabled", None)
    if is_gil_enabled_probe is None or is_gil_enabled_probe():
        return
    environment = dict(os.environ)
    environment["PYTHON_GIL"] = "1"
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)


def _ensure_local_paths() -> None:
    """
    Ensure local source and benchmark helper paths are importable.
    """
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parents[1]
    src_dir = project_root / "src"
    for path in (src_dir, current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_gil_enabled_interpreter()
_ensure_local_paths()

import melder_gauntlet_support as _support
import test_melder_gauntlet as _bench

WARMUP_ITERATIONS = 10
PROFILED_ITERATIONS = 50


def main() -> None:
    """
    Build the gauntlet runtime, warm it, profile steady-state iterations.
    """
    cfg = _support.GauntletConfig(
        iterations=PROFILED_ITERATIONS,
        threads=1,
        request_scope_runs=_support.REQUEST_SCOPE_RUNS_DEFAULT,
        worker_a_jobs=_support.WORKER_A_JOBS_DEFAULT,
        worker_b_jobs=_support.WORKER_B_JOBS_DEFAULT,
    )
    ops = _bench._build_runtime_melder()
    try:
        ops.spawn_singletons()
        for iteration_ix in range(WARMUP_ITERATIONS):
            _support.run_gauntlet_once(ops, cfg, iteration_ix)

        profiler = cProfile.Profile()
        profiler.enable()
        for iteration_ix in range(PROFILED_ITERATIONS):
            _support.run_gauntlet_once(ops, cfg, iteration_ix)
        profiler.disable()

        report_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=report_stream)
        stats.strip_dirs()

        report_stream.write("=" * 78 + "\n")
        report_stream.write("TOP 45 BY TOTTIME (self time - where cycles are actually spent)\n")
        report_stream.write("=" * 78 + "\n")
        stats.sort_stats("tottime").print_stats(45)

        report_stream.write("=" * 78 + "\n")
        report_stream.write("TOP 45 BY CUMULATIVE (call-tree hotspots)\n")
        report_stream.write("=" * 78 + "\n")
        stats.sort_stats("cumulative").print_stats(45)

        report_stream.write("=" * 78 + "\n")
        report_stream.write("MELD FRONT DOOR CALLERS/CALLEES\n")
        report_stream.write("=" * 78 + "\n")
        stats.print_callees("conduit_meld.py.*meld")
        stats.print_callees("spellspace_meld.py.*meld")

        report_text = report_stream.getvalue()
        output_path = Path(__file__).resolve().parent / "melder_hot_path_profile.txt"
        output_path.write_text(report_text, encoding="utf-8")
        print(report_text[:12000])
        print(f"\nFull report written to: {output_path}")
    finally:
        ops.cleanup()


if __name__ == "__main__":
    main()
