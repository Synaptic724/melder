"""Check persistent series isolation, selection, result retention and aggregation.

The real subprocess case uses short measurement windows across both scenarios,
all three libraries and both thread counts; it never runs the multi-hour defaults.
"""

import csv
from dataclasses import asdict, replace
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from benchmarks.testing_other_di import persistent_runtime_gauntlet_series_runner as series


@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep developer benchmark settings and generated reports outside each test's inputs."""
    for name in tuple(os.environ):
        if name.startswith("PERSISTENT_"):
            monkeypatch.delenv(name)
    monkeypatch.setenv("PERSISTENT_SERIES_OUTPUT_DIR", str(tmp_path))


def row(lib: str = "melder", scenario: str = "fastapi_steady", seconds: float = 60,
        threads: int = 3) -> series.SeriesRow:
    """Represent a completed cell without creating a container for launcher-only tests."""
    return series.SeriesRow(lib, scenario, seconds, threads, 123, "disabled", "disabled", seconds,
                            10, 100, 6300, 100 / seconds, 6300 / seconds, 1, 2, "full", 20, "test")


@pytest.mark.parametrize("values", [[], [0], [-1], [301], [float("inf")], [float("nan")], [60, 60], [True]])
def test_invalid_measurement_windows_fail_before_launch(monkeypatch: pytest.MonkeyPatch, values: list[float]) -> None:
    """Zero, unbounded and duplicate durations cannot silently become expensive series runs."""
    monkeypatch.setattr(series, "DURATION_SECONDS", values)
    with pytest.raises(ValueError):
        series.run_series()


@pytest.mark.parametrize("values", [[], [0], [-1], [3, 3], [3.5], [True]])
def test_invalid_thread_selections_fail_before_launch(monkeypatch: pytest.MonkeyPatch, values: list[int]) -> None:
    """The series requires distinct positive integer worker counts."""
    monkeypatch.setattr(series, "THREAD_COUNTS", values)
    with pytest.raises(ValueError):
        series.run_series()


def test_child_launch_forces_selected_cell_and_gil_without_mutating_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Observe the actual subprocess boundary rather than mocking configuration helpers."""
    monkeypatch.setenv("PYTHON_GIL", "1")
    monkeypatch.setenv("PERSISTENT_GAUNTLET_SECONDS", "999")
    monkeypatch.setenv("PERSISTENT_GAUNTLET_THREADS", "99")
    monkeypatch.setattr(series, "WARMUP_SECONDS", 4)
    payload = row(seconds=180, threads=5)
    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        assert command[:3] == [sys.executable, "-X", "gil=0"]
        assert kwargs["env"]["PYTHON_GIL"] == "0"
        assert kwargs["env"]["PERSISTENT_GAUNTLET_SECONDS"] == "180"
        assert kwargs["env"]["PERSISTENT_GAUNTLET_THREADS"] == "5"
        assert kwargs["env"]["PERSISTENT_GAUNTLET_WARMUP_SECONDS"] == "4"
        assert kwargs["timeout"] > 184
        Path(command[-1]).write_text(json.dumps(asdict(payload)), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "child output\n", "")
    monkeypatch.setattr(series.subprocess, "run", run)
    assert series._run_isolated_cell("melder", "fastapi_steady", 180, 5, tmp_path / "cell.json") == payload
    assert os.environ["PYTHON_GIL"] == "1"
    assert os.environ["PERSISTENT_GAUNTLET_SECONDS"] == "999"
    assert (tmp_path / "cell.log").read_text(encoding="utf-8") == "child output\n"


@pytest.mark.parametrize("change", [{"threads": 7}, {"duration_s": 120}, {"gil_status": "enabled"}, {"cycles": 0}])
def test_mismatched_or_empty_child_result_is_refused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, change: dict,
) -> None:
    """A successful process exit alone cannot qualify the wrong workload or an empty measurement."""
    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        Path(command[-1]).write_text(json.dumps(asdict(replace(row(), **change))), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")
    monkeypatch.setattr(series.subprocess, "run", run)
    with pytest.raises(RuntimeError):
        series._run_isolated_cell("melder", "fastapi_steady", 60, 3, tmp_path / "cell.json")


def test_failed_child_keeps_log_and_cannot_return_a_result(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep process diagnostics while propagating its failure to pytest and CI."""
    monkeypatch.setattr(series.subprocess, "run", lambda command, **kwargs: subprocess.CompletedProcess(command, 17, "started\n", "failed\n"))
    with pytest.raises(RuntimeError, match="exit 17"):
        series._run_isolated_cell("melder", "fastapi_steady", 60, 3, tmp_path / "cell.json")
    assert (tmp_path / "cell.log").read_text(encoding="utf-8") == "started\nfailed\n"


def test_timeout_preserves_child_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A hung child is bounded and its captured output survives the timeout failure."""
    def run(command: list[str], **kwargs: object) -> None:
        raise subprocess.TimeoutExpired(command, kwargs["timeout"], output=b"last progress\n")
    monkeypatch.setattr(series.subprocess, "run", run)
    with pytest.raises(RuntimeError, match="timed out"):
        series._run_isolated_cell("melder", "fastapi_steady", 60, 3, tmp_path / "cell.json")
    assert "last progress" in (tmp_path / "cell.log").read_text(encoding="utf-8")


def test_later_failure_preserves_completed_cells_as_incomplete(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """One successful cell remains usable without being presented as a complete series."""
    monkeypatch.setenv("PERSISTENT_SERIES_SECONDS", "60,180")
    monkeypatch.setenv("PERSISTENT_SERIES_THREADS", "3")
    monkeypatch.setenv("PERSISTENT_GAUNTLET_LIBS", "melder")
    monkeypatch.setenv("PERSISTENT_GAUNTLET_SCENARIOS", "fastapi_steady")
    def cell(lib: str, scenario: str, seconds: float, threads: int, path: Path) -> series.SeriesRow:
        if seconds == 180:
            raise RuntimeError("second cell failed")
        return row(lib, scenario, seconds, threads)
    monkeypatch.setattr(series, "_run_isolated_cell", cell)
    with pytest.raises(RuntimeError, match="second cell"):
        series.run_series()
    report = json.loads(next(tmp_path.glob("run-*/results.json")).read_text(encoding="utf-8"))
    assert report["complete"] is False and report["completed_runs"] == 1
    assert report["settings"]["expected_runs"] == 2
    assert report["results"][0]["duration_s"] == 60


@pytest.mark.parametrize("argv", [["--lib", "melder"], ["--seconds", "60"]])
def test_incomplete_child_arguments_never_start_a_series(argv: list[str]) -> None:
    """A mistyped child invocation fails immediately instead of launching the default two-hour run."""
    with pytest.raises(SystemExit) as raised:
        series.main(argv)
    assert raised.value.code == 2


def test_short_real_series_uses_fresh_gil_off_children_and_separate_aggregates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """Exercise the real pytest entry point across 24 short isolated cells, never the full defaults."""
    from benchmarks.testing_other_di import test_persistent_runtime_gauntlet_series as wrapper
    monkeypatch.setenv("PYTHON_GIL", "1")
    monkeypatch.setenv("PERSISTENT_SERIES_SECONDS", "0.2,0.3")
    monkeypatch.setenv("PERSISTENT_SERIES_THREADS", "3,5")
    monkeypatch.setenv("PERSISTENT_GAUNTLET_WARMUP_SECONDS", "0")
    monkeypatch.setenv("PERSISTENT_BURST_ACTIVE_MS", "20")
    monkeypatch.setenv("PERSISTENT_BURST_IDLE_MS", "10")
    wrapper.test_persistent_runtime_gauntlet_series()
    directory = next(tmp_path.glob("run-*"))
    report = json.loads((directory / "results.json").read_text(encoding="utf-8"))
    expected = set(itertools.product((0.2, 0.3), (3, 5), ("fastapi_steady", "bursty_app"), ("dishka", "melder", "dependency-injector")))
    assert report["complete"] is True and report["completed_runs"] == 24
    assert {(item["duration_s"], item["threads"], item["scenario"], item["lib"]) for item in report["results"]} == expected
    assert all(item["gil_status"] == item["gil_status_at_setup"] == "disabled" for item in report["results"])
    assert all(item["process_id"] != os.getpid() and item["cycles"] > 0 and item["semantics_checks"] > 0 for item in report["results"])
    with (directory / "results.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    assert len(csv_rows) == 24
    assert len(list(directory.glob("*.log"))) == 24
    assert "Completed: 24/24; complete=True" in (directory / "summary.md").read_text(encoding="utf-8")
    output = capsys.readouterr().out
    assert output.startswith("[persistent series] duration seconds: [0.2, 0.3]\n[persistent series] thread counts: [3, 5]")
    assert os.environ["PYTHON_GIL"] == "1"
