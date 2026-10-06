"""Run the persistent duration/thread series through ordinary pytest.

Configuration and aggregation live in persistent_runtime_gauntlet_series_runner.py.
Default cells cross 60/180/300 seconds with 3/5 threads, both existing
scenarios, and all three libraries. Each cell runs in its own GIL-off process.

Usage:
    python -m pytest -s benchmarks/testing_other_di/test_persistent_runtime_gauntlet_series.py
"""

from benchmarks.testing_other_di import persistent_runtime_gauntlet_series_runner as runner


def test_persistent_runtime_gauntlet_series() -> None:
    """Run the configured series and keep individual logs plus aggregate reports."""
    runner.run_series()
