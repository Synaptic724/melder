"""
Profile melder setup (binds + conjure, phases 1-7/11) under cProfile.

Purpose:
    Attribute the conjure-time cost (the real-world gauntlet's ~220ms warm
    setup) to concrete functions so phase 1-10 optimization targets measured
    cost: phase bodies vs scheduler vs bind-time reflection vs hashing.

Usage:
    .venv_new\\Scripts\\python.exe benchmarks\\testing_other_di\\profile_melder_setup.py

Contract:
    - Re-execs under `PYTHON_GIL=1` on free-threaded interpreters (cProfile
      requirement); relative attribution is the deliverable.
    - Builds the exact real-world gauntlet runtime surface twice: once cold
      (cache regenerating) and once warm (cache hit), profiling each build
      separately so both postures get their own attribution.
    - Writes the full report to `melder_setup_profile.txt` next to this
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

import test_melder_gauntlet as _bench


def _profile_one_build(label: str, report_stream: io.StringIO) -> None:
    """
    Profile one full runtime build (binds + conjure) and append the report.
    """
    profiler = cProfile.Profile()
    profiler.activate()
    ops = _bench._build_runtime_melder()
    profiler.disable()
    ops.cleanup()

    stats = pstats.Stats(profiler, stream=report_stream)
    stats.strip_dirs()
    report_stream.write("=" * 78 + "\n")
    report_stream.write(f"[{label}] TOP 50 BY TOTTIME (self time)\n")
    report_stream.write("=" * 78 + "\n")
    stats.sort_stats("tottime").print_stats(50)
    report_stream.write("=" * 78 + "\n")
    report_stream.write(f"[{label}] TOP 50 BY CUMULATIVE (call tree)\n")
    report_stream.write("=" * 78 + "\n")
    stats.sort_stats("cumulative").print_stats(50)
    report_stream.write("=" * 78 + "\n")
    report_stream.write(f"[{label}] PHASE AND BIND ATTRIBUTION\n")
    report_stream.write("=" * 78 + "\n")
    stats.print_stats("compiler_phase_")
    stats.print_stats("spell_requirements_finder|spell_examiner|bind.py")
    stats.print_stats("hash_codegen_signature|sha256")


def main() -> None:
    """
    Profile a cold build then a warm build of the gauntlet runtime surface.
    """
    report_stream = io.StringIO()

    # First build: whatever cache state exists on disk (typically warm in a
    # working tree). Second build: guaranteed warm (first build staged it).
    _profile_one_build("build-1 (disk state as-is)", report_stream)
    _profile_one_build("build-2 (warm cache)", report_stream)

    report_text = report_stream.getvalue()
    output_path = Path(__file__).resolve().parent / "melder_setup_profile.txt"
    output_path.write_text(report_text, encoding="utf-8")
    print(report_text[:12000])
    print(f"\nFull report written to: {output_path}")


if __name__ == "__main__":
    main()
