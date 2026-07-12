"""
Crystallizer checkpoint profiles, pytest-style.

Run (3.14t, repo root; -s shows the timing tables):
    .venv_new\\Scripts\\python.exe -m pytest tests/experiments/cprofile_testing/pytest_profile_crystallizer_checkpoints.py -q -s

Tier via env (default small):
    MELDER_BENCH_TIER=large python -m pytest ... -q -s
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from profile_harness import ProfileScenario, run_scenarios
from profile_crystallizer_checkpoints import (
    _build_recorded_world,
    _cache_round_trip,
    _load,
    _seal,
    _setup_sealed,
    _teardown,
)


def _tier() -> str:
    """Resolve the bench tier from MELDER_BENCH_TIER (default small)."""
    return os.environ.get("MELDER_BENCH_TIER", "small")


def test_profile_crystallizer_checkpoint_seal() -> None:
    """Profile create_checkpoint over a recorded dynamic world."""
    run_scenarios(
        [ProfileScenario(
            "crystallizer_checkpoint_seal",
            _build_recorded_world, _seal, _teardown,
            repeats=3, fresh_state_per_run=True,
        )],
        tier=_tier(),
    )


def test_profile_crystallizer_cache_round_trip() -> None:
    """Profile flush_checkpoint + reload_cached_checkpoint."""
    run_scenarios(
        [ProfileScenario(
            "crystallizer_cache_round_trip",
            _build_recorded_world, _cache_round_trip, _teardown,
            repeats=3, fresh_state_per_run=True,
        )],
        tier=_tier(),
    )


def test_profile_crystallizer_checkpoint_load() -> None:
    """Profile the full RestoreEngine unfold (the slow-test suspect)."""
    run_scenarios(
        [ProfileScenario(
            "crystallizer_checkpoint_load",
            _setup_sealed, _load, _teardown,
            repeats=3, fresh_state_per_run=True,
        )],
        tier=_tier(),
    )
