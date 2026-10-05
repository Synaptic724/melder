"""
Contract tests for the shared gauntlet's one-process-per-library mode.

Purpose:
    `test_real_world_gauntlet` measures dependency-injector, dishka and melder with
    each library in its own interpreter, because running the three one after
    another in one free-threaded process made whichever ran later 5-12% slower.
    These tests pin the pieces that mode is made of, without running a full
    gauntlet:

    - the library order per round and the REAL_WORLD_GAUNTLET_ROUNDS setting;
    - the per-library median summary and the per-turn CSV with its Round column;
    - the command the wrapper starts for one library;
    - the runner's `--lib` mode end to end, with a few iterations.

Usage:
    python -X gil=0 -m pytest benchmarks/testing_other_di/test_real_world_gauntlet_isolation.py -q

This is a benchmark diagnostic surface, not production runtime code.
"""

import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest


def _ensure_local_paths() -> None:
    """
    Ensure the repository root, `src/` and this benchmark directory are importable.

    Contract:
        Adds each path once, so the module imports the same way from pytest or a
        direct `python` run, from the repository root or this directory.
    """
    current_dir = Path(__file__).resolve().parent
    repo_root = current_dir.parents[1]
    for path in (repo_root, repo_root / "src", current_dir):
        path_as_str = str(path)
        if path_as_str not in sys.path:
            sys.path.insert(0, path_as_str)


_ensure_local_paths()

import test_real_world_gauntlet as _shared


def _payload(lib: str, round_number: int, total_ms: float, rows: List[List[Any]]) -> Dict[str, Any]:
    """
    Build a payload shaped like `_shared._result_payload` for the helper tests.

    Args:
        lib: Library name.
        round_number: 1-based round.
        total_ms: Loop total; the per-iteration fields are derived from it.
        rows: Per-turn rows `(turn, total_ns, bootstrap_ns, threaded_ns, gc_during, gen0_live)`.

    Returns:
        Dict[str, Any]: The payload.
    """
    return {
        "lib": lib,
        "round": round_number,
        "iterations": 3,
        "threads": 3,
        "gil_status": "disabled",
        "setup_ms": 1.0,
        "cleanup_ms": 0.5,
        "total_ms": total_ms,
        "avg_ms": total_ms / 3,
        "median_ms": total_ms / 3,
        "p95_ms": total_ms / 3,
        "p99_ms": total_ms / 3,
        "max_ms": total_ms / 3,
        "threaded_avg_ms": 0.25,
        "bootstrap_avg_ms": 0.01,
        "hot_scopes_per_s": 1000.0,
        "per_turn_rows": rows,
    }


def _run_runner(args: List[str], iterations: int) -> subprocess.CompletedProcess[str]:
    """
    Run the standalone runner in a child process with a small iteration count.

    Args:
        args: Runner arguments.
        iterations: Value for DI_GAUNTLET_ITERS.

    Returns:
        subprocess.CompletedProcess[str]: The finished child, output captured as text.
    """
    env = os.environ.copy()
    env["DI_GAUNTLET_ITERS"] = str(iterations)
    env.pop("GAUNTLET_PER_TURN_CSV", None)
    return subprocess.run(
        [sys.executable, str(_shared._runner_path()), *args],
        cwd=str(_shared._repo_root()),
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )


def test_round_zero_runs_the_libraries_in_their_printed_order() -> None:
    """
    Round 0 keeps the order the gauntlet has always printed.

    Contract:
        The first round starts the libraries in `_gauntlet_libraries()` order, so a
        one-round run prints dependency-injector, dishka and melder as before.
    """
    assert _shared._isolated_order(0) == ("dependency-injector", "dishka", "melder")
    assert _shared._isolated_order(0) == _shared._gauntlet_libraries()


def test_three_rounds_put_every_library_in_every_slot_once() -> None:
    """
    Over three rounds the rotation puts every library in every slot exactly once.

    Contract:
        Each round is a permutation of the three libraries, and each slot sees all
        three across rounds 0-2.
    """
    libraries = set(_shared._gauntlet_libraries())
    orders = [_shared._isolated_order(round_ix) for round_ix in range(3)]
    for order in orders:
        assert sorted(order) == sorted(libraries)
    for slot in range(3):
        assert {order[slot] for order in orders} == libraries


def test_the_rotation_repeats_every_three_rounds() -> None:
    """
    The order cycles with period three.

    Contract:
        Round 3 repeats round 0 and round 4 repeats round 1.
    """
    assert _shared._isolated_order(3) == _shared._isolated_order(0)
    assert _shared._isolated_order(4) == _shared._isolated_order(1)


def test_a_negative_round_is_refused() -> None:
    """
    A negative round index is a caller error.

    Contract:
        `_isolated_order(-1)` raises AssertionError naming `round_ix`.
    """
    with pytest.raises(AssertionError, match="round_ix"):
        _shared._isolated_order(-1)


def test_rounds_default_to_the_editable_setting(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unset environment override uses the benchmark's editable rounds setting."""
    monkeypatch.delenv("REAL_WORLD_GAUNTLET_ROUNDS", raising=False)
    monkeypatch.setattr(_shared, "REAL_WORLD_GAUNTLET_ROUNDS", 2)
    assert _shared._gauntlet_rounds() == 2


def test_rounds_read_a_positive_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    REAL_WORLD_GAUNTLET_ROUNDS sets how many times every library is measured.

    Contract:
        A positive integer is returned as given.
    """
    monkeypatch.setenv("REAL_WORLD_GAUNTLET_ROUNDS", "3")
    assert _shared._gauntlet_rounds() == 3


def test_zero_rounds_are_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Zero rounds would measure nothing, so it is refused.

    Contract:
        A value of 0 raises AssertionError naming the variable.
    """
    monkeypatch.setenv("REAL_WORLD_GAUNTLET_ROUNDS", "0")
    with pytest.raises(AssertionError, match="REAL_WORLD_GAUNTLET_ROUNDS"):
        _shared._gauntlet_rounds()


def test_median_lines_give_each_library_its_median_and_spread() -> None:
    """
    The round summary prints one median line per library, in the printed order.

    Contract:
        A library without runs is skipped; the loop total shows the median with its
        min and max; other fields are medians too; one run reads "1 round".
    """
    payloads = [_payload("melder", number, total, []) for number, total in ((1, 30.0), (2, 10.0), (3, 20.0))]
    payloads.append(_payload("dishka", 1, 5.0, []))
    lines = _shared._isolated_median_lines(payloads)
    assert len(lines) == 2
    assert lines[0].startswith("[dishka] isolated median over 1 round |")
    assert lines[1].startswith("[melder] isolated median over 3 rounds |")
    assert "total=20.00ms (min=10.00, max=30.00)" in lines[1]
    assert "threaded avg=0.250ms" in lines[1]


def test_isolated_csv_has_one_header_and_a_round_column(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """
    The wrapper's per-turn CSV has one header and a trailing Round column.

    Contract:
        Rows follow the payloads in run order, times in milliseconds to four
        decimals, GC incidence as yes/no and the payload's round last.
    """
    target = tmp_path / "per_turn.csv"
    monkeypatch.setenv("GAUNTLET_PER_TURN_CSV", "1")
    monkeypatch.setattr(_shared, "_per_turn_csv_path", lambda: target)
    payloads = [
        _payload("dishka", 1, 1.0, [[0, 1_000_000, 10_000, 900_000, False, 5]]),
        _payload(
            "melder",
            2,
            1.0,
            [[0, 2_000_000, 20_000, 1_800_000, True, 7], [1, 1_500_000, 0, 1_400_000, False, 9]],
        ),
    ]
    _shared._write_isolated_per_turn_csv(payloads)
    rows = list(csv.reader(target.read_text(encoding="utf-8").splitlines()))
    assert rows[0] == [*_shared._per_turn_csv_header(), "Round", "Threads"]
    assert rows[1] == ["dishka", "0", "1.0000", "0.0100", "0.9000", "no", "5", "1", "3"]
    assert rows[2] == ["melder", "0", "2.0000", "0.0200", "1.8000", "yes", "7", "2", "3"]
    assert rows[3][0] == "melder" and rows[3][-2:] == ["2", "3"]
    assert len(rows) == 4


def test_isolated_csv_is_not_written_when_disabled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """
    Without GAUNTLET_PER_TURN_CSV the wrapper writes no CSV.

    Contract:
        The target path stays absent.
    """
    target = tmp_path / "per_turn.csv"
    monkeypatch.delenv("GAUNTLET_PER_TURN_CSV", raising=False)
    monkeypatch.setattr(_shared, "_per_turn_csv_path", lambda: target)
    _shared._write_isolated_per_turn_csv([_payload("dishka", 1, 1.0, [[0, 1, 1, 1, False, 0]])])
    assert not target.exists()


def test_isolated_run_starts_the_runner_for_one_library(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """
    The wrapper starts the runner for exactly one library, round and payload path.

    Contract:
        Uses this interpreter, always adds `-X gil=0` and child PYTHON_GIL=0,
        passes --lib, --round and --result-json, runs from the repository root and
        leaves the exit code to the caller (check=False). subprocess.run is the
        mocked boundary.
    """
    seen: Dict[str, Any] = {}

    def fake_run(command: List[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        """Record the command and keyword arguments; report a successful child."""
        seen["command"] = command
        seen["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(_shared.subprocess, "run", fake_run)
    result_path = tmp_path / "melder.json"
    _shared._run_isolated_library("melder", 3, result_path)
    command = seen["command"]
    assert command[0] == sys.executable
    assert command[1:3] == ["-X", "gil=0"]
    assert seen["kwargs"]["env"]["PYTHON_GIL"] == "0"
    assert str(_shared._runner_path()) in command
    assert command[command.index("--lib") + 1] == "melder"
    assert command[command.index("--round") + 1] == "3"
    assert command[command.index("--result-json") + 1] == str(result_path)
    assert seen["kwargs"]["check"] is False
    assert seen["kwargs"]["cwd"] == str(_shared._repo_root())


def test_runner_lib_mode_runs_only_that_library_and_hands_back_its_payload(tmp_path: Path) -> None:
    """
    `--lib` runs one library in the runner's process and writes its payload.

    Contract:
        Only that library's result lines are printed, and the JSON payload carries
        its name, round, iteration count and a positive loop total, with no per-turn
        rows while GAUNTLET_PER_TURN_CSV is off. Runs the real runner with three
        iterations of dishka.
    """
    pytest.importorskip("dishka")
    result_path = tmp_path / "dishka.json"
    completed = _run_runner(["--lib", "dishka", "--round", "2", "--result-json", str(result_path)], iterations=3)
    assert completed.returncode == 0, completed.stderr
    assert "[dishka] gauntlet total(3)=" in completed.stdout
    assert "[melder]" not in completed.stdout
    assert "[dependency-injector]" not in completed.stdout
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    assert payload["lib"] == "dishka"
    assert payload["round"] == 2
    assert payload["iterations"] == 3
    assert payload["total_ms"] > 0
    assert payload["per_turn_rows"] == []


def test_runner_refuses_an_unknown_library() -> None:
    """
    An unknown library name is a usage error.

    Contract:
        argparse exits with code 2 and reports an invalid choice.
    """
    completed = _run_runner(["--lib", "not-a-library"], iterations=3)
    assert completed.returncode == 2
    assert "invalid choice" in completed.stderr


def test_runner_refuses_a_payload_path_without_a_library(tmp_path: Path) -> None:
    """
    A payload path without --lib is a usage error rather than being ignored.

    Contract:
        The runner exits with code 2 and says --result-json needs --lib.
    """
    completed = _run_runner(["--result-json", str(tmp_path / "payload.json")], iterations=3)
    assert completed.returncode == 2
    assert "need --lib" in completed.stderr
