"""Verify repeated workload lanes and fresh GIL-off processes across the thread relay."""

from collections import Counter
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
from typing import Callable

import pytest

from benchmarks.testing_other_di import test_real_world_gauntlet as gauntlet


@pytest.mark.parametrize("threads", [1, 2, 3, 5, 7, 9, 28])
def test_every_requested_thread_executes_its_own_repeated_workload(threads: int) -> None:
    """Exercise real threads and independent metrics, including labels beyond Z.

    Lightweight scope callbacks isolate scheduler/accounting correctness from DI
    implementations. All threads exist at the ready barrier before work begins;
    their OS identities therefore cannot be recycled between lane executions.
    """
    seen: list[tuple[int, str]] = []

    def cycle(workload: str) -> Callable[[int], gauntlet._ScopeCycleMetrics]:
        """Return a measured-work callback recording the actual executing thread."""
        def run(variant: int) -> gauntlet._ScopeCycleMetrics:
            """Record one scope cycle and return deterministic timing samples."""
            seen.append((threading.get_ident(), workload))
            return gauntlet._ScopeCycleMetrics(1, 2, 3, 4, 5, 6)
        return run

    ops = gauntlet._RuntimeOps("melder", lambda: None, lambda: None,
                               cycle("request"), cycle("worker_a"), cycle("worker_b"), lambda: None)
    result = gauntlet._run_gauntlet_once(ops, gauntlet._GauntletConfig(1, threads, 2, 3, 4), 0)
    assert len({identity for identity, _ in seen}) == threads
    assert len(result.lane_metrics) == threads
    assert len(seen) == sum((2, 3, 4)[index % 3] for index in range(threads))
    assert Counter(workload for _, workload in seen) == Counter({
        "request": ((threads + 2) // 3) * 2,
        "worker_a": ((threads + 1) // 3) * 3,
        "worker_b": (threads // 3) * 4,
    })
    assert list(result.lane_metrics)[:min(threads, 3)] == ["request", "worker_a", "worker_b"][:threads]
    if threads >= 5:
        assert len(result.lane_metrics["worker_c"].outer_total_ns) == 2
        assert len(result.lane_metrics["worker_d"].outer_total_ns) == 3
    if threads == 28:
        assert len(result.lane_metrics["worker_aa"].outer_total_ns) == 2
    for name, samples in result.lane_metrics.items():
        assert sum(result.lane_variant_counts[name]) == len(samples.outer_total_ns)
        assert set(samples.outer_create_ns) == {1}
        assert set(samples.request_total_ns) == {6}


def test_default_relay_uses_the_editable_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """The configured list selects the run order, and callers cannot mutate it through the result."""
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_THREAD_COUNTS", raising=False)
    monkeypatch.delenv("DI_GAUNTLET_THREADS", raising=False)
    configured = [9, 3, 6]
    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_THREAD_COUNTS", configured)
    assert gauntlet._gauntlet_thread_counts() == (9, 3, 6)
    assert configured == [9, 3, 6]


@pytest.mark.parametrize("counts", [[], [0], [-2], [3, 3], [3.5], [True]])
def test_invalid_configured_relays_are_refused(monkeypatch: pytest.MonkeyPatch, counts: list) -> None:
    """Empty, nonpositive, duplicate and noninteger thread relays cannot produce plausible results."""
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_THREAD_COUNTS", raising=False)
    monkeypatch.delenv("DI_GAUNTLET_THREADS", raising=False)
    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_THREAD_COUNTS", counts)
    with pytest.raises(ValueError):
        gauntlet._gauntlet_thread_counts()


def test_environment_can_select_a_relay_or_one_legacy_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """Explicit relay input takes precedence while the single-count profiling path remains usable."""
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_THREAD_COUNTS", raising=False)
    monkeypatch.setenv("DI_GAUNTLET_THREADS", "12")
    assert gauntlet._gauntlet_thread_counts() == (12,)
    assert gauntlet._GauntletConfig.from_env().threads == 12
    monkeypatch.setenv("REAL_WORLD_GAUNTLET_THREAD_COUNTS", " 3, 5, 7, 9 ")
    assert gauntlet._gauntlet_thread_counts() == (3, 5, 7, 9)


def test_child_forces_gil_off_without_changing_parent_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Verify actual launch arguments and child environment at the subprocess boundary."""
    monkeypatch.setenv("PYTHON_GIL", "1")
    monkeypatch.setenv("DI_GAUNTLET_THREADS", "99")
    seen: list[tuple[list[str], dict[str, str]]] = []

    def run(command: list[str], *, env: dict[str, str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        """Capture process inputs without starting an extra measured child in this unit case."""
        seen.append((command, env))
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(gauntlet.subprocess, "run", run)
    gauntlet._run_isolated_library("melder", 1, tmp_path / "result.json", threads=7, iterations=11)
    command, child_env = seen[0]
    assert command[:3] == [sys.executable, "-X", "gil=0"]
    assert child_env["PYTHON_GIL"] == "0"
    assert child_env["DI_GAUNTLET_THREADS"] == "7"
    assert child_env["DI_GAUNTLET_ITERS"] == "11"
    assert os.environ["PYTHON_GIL"] == "1" and os.environ["DI_GAUNTLET_THREADS"] == "99"


def test_enabled_gil_is_refused_before_library_setup(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unsuitable measured interpreter fails before it can build or time a DI graph."""
    monkeypatch.setattr(sys, "_is_gil_enabled", lambda: True)
    with pytest.raises(RuntimeError, match="GIL disabled in the measured process"):
        gauntlet._run_gauntlet_benchmark("must-not-be-built", gauntlet._GauntletConfig(1, 3, 10, 25, 30))


def test_round_summaries_do_not_mix_thread_counts() -> None:
    """Three-thread and five-thread timings retain separate medians, even for the same library."""
    payloads = []
    for threads, total in ((3, 10), (5, 100), (3, 20), (5, 200)):
        payloads.append({"lib": "melder", "iterations": 1, "threads": threads, "total_ms": total,
                         "avg_ms": total, "p99_ms": total, "threaded_avg_ms": total,
                         "hot_scopes_per_s": 1, "setup_ms": 1})
    lines = gauntlet._isolated_median_lines(payloads)
    assert len(lines) == 2
    assert "threads=3" in lines[0] and "total=15.00ms" in lines[0]
    assert "threads=5" in lines[1] and "total=150.00ms" in lines[1]


def test_small_real_relay_runs_all_libraries_and_reports_every_thread_count(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Run real isolated children at 3/5/7/9 threads and prove their observed no-GIL/count identity.

    One- and two-iteration cells make this a correctness check, not a performance
    ranking. The parent advertises GIL=1 deliberately; every measured child must
    override it before startup. Normal pytest output retains all twenty-four results.
    """
    pytest.importorskip("dishka")
    pytest.importorskip("dependency_injector")
    monkeypatch.setenv("PYTHON_GIL", "1")
    monkeypatch.setenv("DI_GAUNTLET_ITERS", "2")
    monkeypatch.setenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", "1,2")
    monkeypatch.setenv("REAL_WORLD_GAUNTLET_ROUNDS", "1")
    monkeypatch.setenv("REAL_WORLD_GAUNTLET_THREAD_COUNTS", "3,5,7,9")
    monkeypatch.delenv("GAUNTLET_PER_TURN_CSV", raising=False)
    gauntlet.test_real_world_gauntlet()
    output = capsys.readouterr().out
    for lib in ("dependency-injector", "dishka", "melder"):
        configs = re.findall(r"\[" + re.escape(lib) + r"\] gauntlet config: ([^\n]+)", output)
        assert len(configs) == 8
        observed = [(int(re.search(r"iterations=(\d+)", config)[1]),
                     int(re.search(r"threads=(\d+)", config)[1])) for config in configs]
        assert observed == [(iterations, threads) for iterations in (1, 2) for threads in (3, 5, 7, 9)]
        assert all("gil=disabled" in config for config in configs)
        assert f"[{lib}] lane=worker_h |" in output
    assert os.environ["PYTHON_GIL"] == "1"
    print(output)

def test_file_iteration_and_round_settings_need_no_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Editing the file defaults is sufficient for ordinary pytest launches."""
    monkeypatch.delenv("DI_GAUNTLET_ITERS", raising=False)
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_ROUNDS", raising=False)
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", raising=False)
    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_ITERATION_COUNTS", [4, 8])
    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_ROUNDS", 2)
    assert gauntlet._GauntletConfig.from_env().iterations == 4
    assert gauntlet._gauntlet_rounds() == 2


def test_iteration_relay_reads_the_editable_list_and_optional_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Iteration counts retain file order and support bounded legacy single-count runs."""
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", raising=False)
    monkeypatch.delenv("DI_GAUNTLET_ITERS", raising=False)
    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_ITERATION_COUNTS", [5, 2])
    assert gauntlet._gauntlet_iteration_counts() == (5, 2)
    monkeypatch.setenv("DI_GAUNTLET_ITERS", "3")
    assert gauntlet._gauntlet_iteration_counts() == (3,)
    monkeypatch.setenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", " 2, 4 ")
    assert gauntlet._gauntlet_iteration_counts() == (2, 4)


@pytest.mark.parametrize("counts", [[], [0], [-1], [2, 2], [2.5], [True]])
def test_invalid_iteration_relays_are_refused(monkeypatch: pytest.MonkeyPatch, counts: list) -> None:
    """Refuse meaningless iteration relays before any measured process starts."""
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_ITERATION_COUNTS", raising=False)
    monkeypatch.delenv("DI_GAUNTLET_ITERS", raising=False)
    monkeypatch.setattr(gauntlet, "REAL_WORLD_GAUNTLET_ITERATION_COUNTS", counts)
    with pytest.raises(ValueError):
        gauntlet._gauntlet_iteration_counts()


def test_round_summaries_do_not_mix_iteration_counts() -> None:
    """Identical thread counts still produce separate medians for different iteration budgets."""
    payloads = [{"lib": "melder", "iterations": iterations, "threads": 3, "total_ms": total,
                 "avg_ms": total, "p99_ms": total, "threaded_avg_ms": total,
                 "hot_scopes_per_s": 1, "setup_ms": 1}
                for iterations, total in ((5, 10), (10, 100), (5, 20), (10, 200))]
    lines = gauntlet._isolated_median_lines(payloads)
    assert len(lines) == 2
    assert "iterations=5" in lines[0] and "total=15.00ms" in lines[0]
    assert "iterations=10" in lines[1] and "total=150.00ms" in lines[1]
