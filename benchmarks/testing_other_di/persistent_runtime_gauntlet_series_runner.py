"""Run the persistent benchmark as an isolated duration/thread series.

Edit the settings below, then run test_persistent_runtime_gauntlet_series.py
through pytest, or execute this file directly. Every duration/thread/scenario/
library cell gets a fresh interpreter with the GIL disabled. The original
persistent benchmark owns its container, workers, warmup and cleanup unchanged.

Defaults produce 36 cells: 108 minutes of measured work plus 6 minutes of warmup
and setup/cleanup. Durations must be positive and at most 300 seconds. Optional
PERSISTENT_SERIES_SECONDS and PERSISTENT_SERIES_THREADS comma-separated inputs
override the two lists. The existing PERSISTENT_GAUNTLET_LIBS/SCENARIOS and other
persistent settings remain usable; scalar seconds/threads cannot replace the
series selections.

Results go into a new run directory below persistent_gauntlet_results beside
this file, or PERSISTENT_SERIES_OUTPUT_DIR. Each child retains its own JSON and
log. results.json, results.csv and summary.md are refreshed after every completed
cell, keeping partial evidence if a later cell fails. Different durations,
thread counts and scenarios retain separate rows; their timings are not averaged.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from benchmarks.testing_other_di.test_persistent_runtime_gauntlet import PersistentResult

# ---- Editable series configuration ----
DURATION_SECONDS: list[float] = [60, 180, 300]
THREAD_COUNTS: list[int] = [3, 5]
LIBRARIES: list[str] = ["dishka", "melder", "dependency-injector"]
SCENARIOS: list[str] = ["fastapi_steady", "bursty_app"]
WARMUP_SECONDS: float = 10.0
SAMPLE_EVERY: int = 1000
APP_WORK_NS: int = 0
BURST_ACTIVE_MS: int = 2000
BURST_IDLE_MS: int = 1000
BURST_REQUEST_WEIGHT: int = 60
BURST_WORKER_A_WEIGHT: int = 25
BURST_WORKER_B_WEIGHT: int = 15
BUCKET_SECONDS: float = 0.0
INSTRUMENTATION: str = "full"
OUTPUT_DIRECTORY: Path = Path(__file__).resolve().parent / "persistent_gauntlet_results"
# ---- End editable configuration ----

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SUPPORTED_LIBRARIES = ("dependency-injector", "dishka", "melder")
_SUPPORTED_SCENARIOS = ("fastapi_steady", "bursty_app")


@dataclass(frozen=True)
class SeriesRow:
    """Store one completed cell's identity and wall-throughput evidence.

    Object counts are declared workload minimums. Setup, warmup and cleanup are
    separate from measured time. Raw phase and degradation details stay in the
    cell log; this compact record is shared by JSON, CSV and the summary table.
    """

    lib: str
    scenario: str
    duration_s: float
    threads: int
    process_id: int
    gil_status: str
    gil_status_at_setup: str
    measured_s: float
    warmup_s: float
    cycles: int
    objects_min: int
    cycles_per_s: float
    objects_per_s_min: float
    setup_ms: float
    cleanup_ms: float
    instrumentation: str
    semantics_checks: int
    environment: str


def _duration(value: float) -> float:
    """Refuse nonfinite, nonpositive or over-five-minute measurement windows."""
    if isinstance(value, bool) or not math.isfinite(value) or not 0 < value <= 300:
        raise ValueError("Series durations must be greater than 0 and at most 300 seconds.")
    return value


def _series_counts() -> tuple[tuple[float, ...], tuple[int, ...]]:
    """Read the editable lists or explicit series overrides, preserving their order."""
    seconds = os.getenv("PERSISTENT_SERIES_SECONDS", "").strip()
    threads = os.getenv("PERSISTENT_SERIES_THREADS", "").strip()
    durations = tuple(_duration(float(part)) for part in seconds.split(",")) if seconds else tuple(_duration(value) for value in DURATION_SECONDS)
    counts = tuple(int(part) for part in threads.split(",")) if threads else tuple(THREAD_COUNTS)
    if not durations or len(set(durations)) != len(durations):
        raise ValueError("The duration list must be nonempty with no duplicates.")
    if not counts or any(type(value) is not int or value <= 0 for value in counts) or len(set(counts)) != len(counts):
        raise ValueError("The thread list must contain distinct positive integers.")
    return durations, counts


def _names(name: str, defaults: list[str], allowed: tuple[str, ...]) -> tuple[str, ...]:
    """Select supported libraries/scenarios before starting any benchmark child."""
    raw = os.getenv(name, "").strip()
    values = tuple(part.strip() for part in raw.split(",")) if raw else tuple(defaults)
    if not values or len(set(values)) != len(values) or any(value not in allowed for value in values):
        raise ValueError(f"{name} must select distinct entries from {allowed}.")
    return values


def _child_environment(seconds: float, threads: int) -> dict[str, str]:
    """Copy runtime settings for one child without mutating the parent environment.

    Explicit persistent instrumentation/warmup overrides win over the editable
    defaults. This cell's duration and thread count always come from the series.
    Both the interpreter flag and environment force GIL-off before library imports.
    """
    env = os.environ.copy()
    for name, value in (
        ("PERSISTENT_GAUNTLET_WARMUP_SECONDS", WARMUP_SECONDS),
        ("PERSISTENT_GAUNTLET_SAMPLE_EVERY", SAMPLE_EVERY),
        ("PERSISTENT_APP_WORK_NS", APP_WORK_NS),
        ("PERSISTENT_BURST_ACTIVE_MS", BURST_ACTIVE_MS),
        ("PERSISTENT_BURST_IDLE_MS", BURST_IDLE_MS),
        ("PERSISTENT_BURST_REQUEST_WEIGHT", BURST_REQUEST_WEIGHT),
        ("PERSISTENT_BURST_WORKER_A_WEIGHT", BURST_WORKER_A_WEIGHT),
        ("PERSISTENT_BURST_WORKER_B_WEIGHT", BURST_WORKER_B_WEIGHT),
        ("PERSISTENT_GAUNTLET_BUCKET_SECONDS", BUCKET_SECONDS),
        ("PERSISTENT_GAUNTLET_INSTRUMENTATION", INSTRUMENTATION),
    ):
        if not env.get(name, "").strip():
            env[name] = str(value)
    warmup = float(env["PERSISTENT_GAUNTLET_WARMUP_SECONDS"])
    if not math.isfinite(warmup) or warmup < 0:
        raise ValueError("Warmup seconds must be finite and nonnegative.")
    env.update(PERSISTENT_GAUNTLET_SECONDS=str(seconds), PERSISTENT_GAUNTLET_THREADS=str(threads),
               PYTHON_GIL="0", PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    return env


def _result_row(result: PersistentResult) -> SeriesRow:
    """Keep the existing benchmark's measured-wall denominator in the aggregate."""
    seconds = result.measured_ns / 1_000_000_000
    cycles = sum(lane.cycles for lane in result.worker_stats.lanes.values())
    objects = sum(lane.objects_min for lane in result.worker_stats.lanes.values())
    return SeriesRow(result.lib, result.cfg.scenario, result.cfg.duration_s, result.cfg.threads,
                     os.getpid(), result.gil_status, result.gil_status_at_setup, seconds,
                     result.warmup_ns / 1_000_000_000, cycles, objects, cycles / seconds,
                     objects / seconds, result.setup_ns / 1_000_000, result.cleanup_ns / 1_000_000,
                     result.cfg.instrumentation, result.semantics_checks, result.environment)


def _run_child(lib: str, scenario: str, seconds: float, threads: int, result_path: Path) -> None:
    """Measure one cell in this process using the original benchmark's lifecycle."""
    _duration(seconds)
    if threads <= 0:
        raise ValueError("Thread count must be positive.")
    os.environ.update(_child_environment(seconds, threads))
    sys.path.insert(0, str(_REPO_ROOT))
    from benchmarks.testing_other_di import test_persistent_runtime_gauntlet as persistent

    persistent.base._require_gil_disabled()
    cfg = persistent.PersistentConfig.from_env(scenario)
    result = persistent.run_persistent_benchmark_with_cleanup(lib, cfg)
    persistent._print_result(result)
    persistent._print_degradation(result)
    persistent.base._require_gil_disabled()
    if result.gil_status_at_setup != "disabled" or result.gil_status != "disabled":
        raise RuntimeError("The persistent benchmark did not remain GIL-off.")
    result_path.write_text(json.dumps(asdict(_result_row(result)), indent=2) + "\n", encoding="utf-8")


def _run_isolated_cell(lib: str, scenario: str, seconds: float, threads: int, result_path: Path) -> SeriesRow:
    """Start a bounded fresh interpreter, retain its output, and verify its identity."""
    env = _child_environment(seconds, threads)
    command = [sys.executable, "-X", "gil=0", str(Path(__file__).resolve()), "--lib", lib,
               "--scenario", scenario, "--seconds", str(seconds), "--threads", str(threads),
               "--result-json", str(result_path)]
    timeout = seconds + float(env["PERSISTENT_GAUNTLET_WARMUP_SECONDS"]) + 180
    try:
        completed = subprocess.run(command, cwd=_REPO_ROOT, env=env, capture_output=True,
                                   text=True, encoding="utf-8", errors="replace", check=False, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        output = error.stdout or b""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        result_path.with_suffix(".log").write_text(output + f"\nChild timed out after {timeout}s.\n", encoding="utf-8")
        raise RuntimeError(f"Persistent cell timed out: {lib}, {scenario}, {seconds}s, {threads} threads") from error
    output = completed.stdout + completed.stderr
    result_path.with_suffix(".log").write_text(output, encoding="utf-8")
    print(output, end="" if output.endswith("\n") else "\n", flush=True)
    if completed.returncode:
        raise RuntimeError(f"Persistent cell failed: {lib}, {scenario}, {seconds}s, {threads} threads; exit {completed.returncode}")
    row = SeriesRow(**json.loads(result_path.read_text(encoding="utf-8")))
    if (row.lib, row.scenario, row.duration_s, row.threads, row.gil_status, row.gil_status_at_setup) != (
            lib, scenario, seconds, threads, "disabled", "disabled"):
        raise RuntimeError("Persistent child returned mismatched library/scenario/duration/threads/GIL identity.")
    if row.cycles <= 0 or row.measured_s < 0.9 * seconds or row.semantics_checks <= 0:
        raise RuntimeError("Persistent child did not report a valid measured workload.")
    return row


def _write_reports(directory: Path, settings: dict[str, object], rows: list[SeriesRow], complete: bool) -> str:
    """Retain completed cells as separate CSV/JSON/table rows, including partial runs."""
    report = {"settings": settings, "complete": complete, "completed_runs": len(rows),
              "results": [asdict(row) for row in rows]}
    (directory / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (directory / "results.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(SeriesRow.__dataclass_fields__))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    lines = ["# Persistent runtime series", "", f"Durations (seconds): {settings['duration_seconds']}",
             f"Threads: {settings['thread_counts']}", f"Completed: {len(rows)}/{settings['expected_runs']}; complete={complete}", "",
             "| Seconds | Threads | Scenario | Library | Measured s | Cycles/s | Objects/s minimum |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        lines.append(f"| {row.duration_s:g} | {row.threads} | {row.scenario} | {row.lib} | {row.measured_s:.3f} | {row.cycles_per_s:,.0f} | {row.objects_per_s_min:,.0f} |")
    summary = "\n".join(lines) + "\n"
    (directory / "summary.md").write_text(summary, encoding="utf-8")
    return summary


def run_series() -> Path:
    """Run the selected Cartesian series sequentially and return its retained results directory.

    Each child has its own container and worker threads. A failed child stops the
    series; previously completed rows and that child's log remain available.
    The caller can be ordinary pytest: only measured children require GIL-off.
    """
    durations, threads = _series_counts()
    libraries = _names("PERSISTENT_GAUNTLET_LIBS", LIBRARIES, _SUPPORTED_LIBRARIES)
    scenarios = _names("PERSISTENT_GAUNTLET_SCENARIOS", SCENARIOS, _SUPPORTED_SCENARIOS)
    expected = len(durations) * len(threads) * len(libraries) * len(scenarios)
    print(f"[persistent series] duration seconds: {list(durations)}", flush=True)
    print(f"[persistent series] thread counts: {list(threads)}", flush=True)
    print(f"[persistent series] libraries: {list(libraries)}; scenarios: {list(scenarios)}; runs: {expected}", flush=True)
    parent = Path(os.getenv("PERSISTENT_SERIES_OUTPUT_DIR") or OUTPUT_DIRECTORY).resolve()
    parent.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    print(f"[persistent series] results: {directory}", flush=True)
    settings = {"duration_seconds": list(durations), "thread_counts": list(threads),
                "libraries": list(libraries), "scenarios": list(scenarios), "expected_runs": expected}
    rows: list[SeriesRow] = []
    _write_reports(directory, settings, rows, False)
    for seconds in durations:
        for count in threads:
            for scenario in scenarios:
                for lib in libraries:
                    print(f"[persistent series] {len(rows) + 1}/{expected}: {seconds:g}s, {count} threads, {scenario}, {lib}", flush=True)
                    result_path = directory / f"{seconds:g}s_{count}threads_{scenario}_{lib}.json"
                    rows.append(_run_isolated_cell(lib, scenario, seconds, count, result_path))
                    summary = _write_reports(directory, settings, rows, len(rows) == expected)
    print(summary, flush=True)
    return directory


def main(argv: list[str] | None = None) -> int:
    """Run the series by default; complete child arguments select exactly one cell."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lib", choices=_SUPPORTED_LIBRARIES)
    parser.add_argument("--scenario", choices=_SUPPORTED_SCENARIOS)
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--threads", type=int)
    parser.add_argument("--result-json", type=Path)
    args = parser.parse_args(argv)
    selections = (args.lib, args.scenario, args.seconds, args.threads, args.result_json)
    if all(value is None for value in selections):
        run_series()
    elif any(value is None for value in selections):
        parser.error("A child run needs --lib, --scenario, --seconds, --threads and --result-json together.")
    else:
        _run_child(args.lib, args.scenario, args.seconds, args.threads, args.result_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
