import os
import subprocess
import sys
from pathlib import Path

import pytest


def _runner_path() -> Path:
    """
    Purpose:
        Resolve the standalone Melder gauntlet cProfile runner script.
    Contract:
        - Returns the sibling runner path next to this pytest wrapper.
        - The returned script is executed directly with the current Python
          interpreter, without toggling the GIL.
    Returns:
        Absolute path to the standalone runner script.
    """
    return Path(__file__).resolve().with_name("melder_gauntlet_cprofile_runner.py")


def _repo_root() -> Path:
    """
    Purpose:
        Resolve the repository root for the standalone cProfile runner.
    Contract:
        - Assumes this file lives at
          `benchmarks/testing_other_di/test_melder_gauntlet_cprofile.py`.
        - Returns the repo root used as the child-process working directory.
    Returns:
        Repository root path.
    """
    return Path(__file__).resolve().parents[2]


@pytest.mark.timeout(3600)
def test_melder_gauntlet_cprofile() -> None:
    """
    Purpose:
        Run the Melder-only cProfile harness in a standalone subprocess.
    Contract:
        - Avoids running cProfile inside pytest-owned execution state.
        - Does not force the interpreter back onto the GIL.
        - Streams child stdout/stderr back into the pytest terminal output for
          artifact visibility and failure diagnosis.
    Returns:
        None.
    Raises:
        AssertionError: If the standalone runner returns a non-zero exit code.
    """
    completed = subprocess.run(
        [sys.executable, str(_runner_path())],
        cwd=str(_repo_root()),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n")

    if completed.returncode != 0:
        raise AssertionError(
            "Melder gauntlet cProfile runner failed with exit code "
            f"{completed.returncode}."
        )
