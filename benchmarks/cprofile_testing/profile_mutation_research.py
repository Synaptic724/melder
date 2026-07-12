"""
MutationResearch verb profiles.

Scenarios (tiered by declared-spell count):
    - mr_record_world_entries: N register_spell declarations (the bind seam's
      auto-record cost in isolation).
    - mr_residency_views:      N residency_view joins (query-time join cost).
    - mr_campaign_view:        one campaign_view over a stamped population
      (journal-walk cost).

Run (3.14t):
    python benchmarks/cprofile_testing/profile_mutation_research.py small|medium|large

Rot check:
    tiers scale 100 -> 500 -> 2000 declarations. residency_view is the one to
    watch: it probes frames + custody per call - super-linear growth there
    means the join is rescanning instead of indexing.
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from profile_harness import ProfileScenario, run_scenarios

from melder.mutation_research.mutation_research import MutationResearch

_TIER_SPELLS = {"small": 100, "medium": 500, "large": 2000}


def _sha(index: int, tier: str) -> str:
    """Mint one deterministic spell id for bench declarations."""
    return hashlib.sha256(
        "bench_{0}_{1}".format(tier, index).encode("utf-8"),
    ).hexdigest()


def _fresh_root():
    """Build one activated, standalone MR root (no Aether world needed)."""
    MutationResearch._reset_singleton_for_tests()
    root = MutationResearch(aether=None)
    configuration = root.create_configuration()
    configuration.with_defaults()
    root.configure(configuration)
    root.activate(hydrate_from_record=False)
    return root


def _setup_empty(tier: str):
    """Setup: activated empty root + the tier's spell-id list."""
    root = _fresh_root()
    return {
        "root": root,
        "ids": [_sha(index, tier) for index in range(_TIER_SPELLS[tier])],
    }


def _setup_populated(tier: str):
    """Setup: root pre-populated with the tier's declarations, stamped."""
    state = _setup_empty(tier)
    root = state["root"]
    root.set_active_campaign("bench_campaign")
    for spell_id in state["ids"]:
        root.record_world_entry(spell_id)
    root.clear_active_campaign()
    return state


def _teardown(state) -> None:
    """Clean the bench root (best-effort)."""
    try:
        state["root"].cleanup()
    except Exception:
        pass
    MutationResearch._reset_singleton_for_tests()


def _record_entries(state) -> None:
    """Measured body: declare every tier spell id (idempotent re-runs)."""
    root = state["root"]
    for spell_id in state["ids"]:
        root.record_world_entry(spell_id)


def _residency_views(state) -> None:
    """Measured body: one residency join per declared spell."""
    root = state["root"]
    for spell_id in state["ids"]:
        root.residency_view(spell_id)


def _campaign_view(state) -> object:
    """Measured body: gather the stamped campaign in declaration order."""
    return state["root"].research_set().campaign_view("bench_campaign")


if __name__ == "__main__":
    tier_argument = sys.argv[1] if len(sys.argv) > 1 else "small"
    run_scenarios(
        [
            ProfileScenario(
                "mr_record_world_entries",
                _setup_empty, _record_entries, _teardown,
            ),
            ProfileScenario(
                "mr_residency_views",
                _setup_populated, _residency_views, _teardown,
            ),
            ProfileScenario(
                "mr_campaign_view",
                _setup_populated, _campaign_view, _teardown,
            ),
        ],
        tier=tier_argument,
    )
