"""
MutationResearch verb profiles, pytest-style.

Run (3.14t, repo root; -s shows the timing tables):
    .venv_new\\Scripts\\python.exe -m pytest tests/experiments/cprofile_testing/pytest_profile_mutation_research.py -q -s

Tier via env (default small):
    MELDER_BENCH_TIER=large python -m pytest ... -q -s
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from profile_harness import ProfileScenario, run_scenarios
from profile_mutation_research import (
    _campaign_view,
    _record_entries,
    _residency_views,
    _setup_empty,
    _setup_populated,
    _teardown,
)


def _tier() -> str:
    """Resolve the bench tier from MELDER_BENCH_TIER (default small)."""
    return os.environ.get("MELDER_BENCH_TIER", "small")


def test_profile_mr_record_world_entries() -> None:
    """Profile N world-entry declarations (the bind seam's record cost)."""
    run_scenarios(
        [ProfileScenario(
            "mr_record_world_entries",
            _setup_empty, _record_entries, _teardown,
        )],
        tier=_tier(),
    )


def test_profile_mr_residency_views() -> None:
    """Profile the query-time residency join per declared spell."""
    run_scenarios(
        [ProfileScenario(
            "mr_residency_views",
            _setup_populated, _residency_views, _teardown,
        )],
        tier=_tier(),
    )


def test_profile_mr_campaign_view() -> None:
    """Profile one campaign_view gather over the stamped population."""
    run_scenarios(
        [ProfileScenario(
            "mr_campaign_view",
            _setup_populated, _campaign_view, _teardown,
        )],
        tier=_tier(),
    )
