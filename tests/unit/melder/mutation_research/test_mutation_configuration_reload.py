"""
MR reload-lane unit suite (mr_restore_build_stage_2026_07_11, S1).

The verb mirrors the owner reload-lane law: defaults are the backfill
floor, recorded truth overwrites, per-key rejected/backfilled reporting,
and the lane SEALS via activate() on return (the config's emission factor
- inert here because no activated Crystallizer rides these tests).
"""

import pytest

from melder.mutation_research.mutation_configuration import (
    MutationResearchConfiguration,
)


def test_reload_applies_recorded_truth_over_defaults():
    """
    Contract: a recorded True overwrites the schema default False, the
    outcome reports no rejections/backfills, and the lane returns SEALED
    (frozen + activated - exactly what root activation requires).
    """
    configuration = MutationResearchConfiguration()
    try:
        outcome = configuration.load_recorded_dictionary(
            {"unrestricted_module_mutations": True}
        )
        assert outcome == {"rejected": [], "backfilled": []}
        assert configuration.get_property(
            "unrestricted_module_mutations"
        ) is True
        assert configuration.frozen is True
        assert configuration.activated is True
    finally:
        configuration.cleanup()


def test_reload_backfills_missing_keys_and_reports_them():
    """
    Contract: keys the record did not carry land as schema defaults AND
    ride back under "backfilled" - nothing defaults silently.
    """
    configuration = MutationResearchConfiguration()
    try:
        outcome = configuration.load_recorded_dictionary({})
        assert outcome["rejected"] == []
        assert outcome["backfilled"] == ["unrestricted_module_mutations"]
        assert configuration.get_property(
            "unrestricted_module_mutations"
        ) is False
    finally:
        configuration.cleanup()


def test_reload_rejects_unknown_and_mistyped_keys_with_reasons():
    """
    Contract: refusals are collected per key as "key: reason" - never
    raised mid-lane and never silently coerced.
    """
    configuration = MutationResearchConfiguration()
    try:
        outcome = configuration.load_recorded_dictionary({
            "unrestricted_module_mutations": "not-a-bool",
            "key_the_schema_never_had": 7,
        })
        assert len(outcome["rejected"]) == 2
        assert any(
            entry.startswith("unrestricted_module_mutations:")
            for entry in outcome["rejected"]
        )
        assert any(
            entry.startswith("key_the_schema_never_had:")
            for entry in outcome["rejected"]
        )
        # A refused registry key rides BOTH lists (Nexus-lane semantics):
        # "rejected" carries the reason, and because it never applied,
        # "backfilled" honestly reports that the defaults floor holds.
        assert configuration.get_property(
            "unrestricted_module_mutations"
        ) is False
        assert outcome["backfilled"] == ["unrestricted_module_mutations"]
    finally:
        configuration.cleanup()


def test_reload_refuses_frozen_configurations():
    """
    Contract: the reload lane requires a fresh configuration object; a
    sealed one refuses with RuntimeError.
    """
    configuration = MutationResearchConfiguration().with_defaults()
    configuration.freeze()
    try:
        with pytest.raises(RuntimeError, match="already frozen"):
            configuration.load_recorded_dictionary({})
    finally:
        configuration.cleanup()
