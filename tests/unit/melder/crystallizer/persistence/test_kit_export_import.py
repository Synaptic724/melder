"""
Unit tests for the kit export/import payload lane: fold-safety gating,
manifest shape, JSON-safety, idempotent insert-if-absent import, and the
honest truncated-prefix annotation.

Runs only on 3.14t (melder package root import chain).
"""
import json

import pytest

from melder.crystallizer.persistence.persistence_system import (
    PersistenceSystem,
)
from melder.crystallizer.persistence.recorded_unit_state import (
    RecordedUnitState,
)


def _system_with_journal_driver():
    """
    Build one persistence system plus a cheap journal driver.

    Returns:
        tuple: (system, emit) where emit() journals exactly one entry into
        the active profile (a nexus state flip needs no twin construction).
    """
    system = PersistenceSystem()

    def emit() -> None:
        system.record_nexus_state(RecordedUnitState.enabled)

    return system, emit


def test_export_refuses_empty_and_broken_chains_loudly():
    """
    Contract: nothing trustworthy, nothing exported - empty ledgers and
    broken chains raise expressive ValueErrors (a kit must never
    propagate a wrong world).
    """
    system, emit = _system_with_journal_driver()
    with pytest.raises(ValueError, match="empty"):
        system.build_kit_payload()
    seal_ids = []
    for _round in range(3):
        emit()
        seal_ids.append(system.create_checkpoint())
    system._checkpoint_crystals_by_id.pop(seal_ids[1]).cleanup()
    with pytest.raises(ValueError, match="broken"):
        system.build_kit_payload()
    system.cleanup()


def test_export_manifest_shape_and_json_safety():
    """
    Contract: the kit payload is JSON-safe end to end; the manifest
    carries format version 1, the profile name, aligned ids/numbers
    (oldest first), and the full chain report.
    """
    system, emit = _system_with_journal_driver()
    for _round in range(2):
        emit()
        system.create_checkpoint()
    kit = system.build_kit_payload()
    manifest = kit["manifest"]
    assert manifest["kit_format_version"] == 1
    assert manifest["profile_name"] == "default"
    assert manifest["checkpoint_numbers"] == [1, 2]
    assert len(manifest["checkpoint_ids"]) == 2
    assert manifest["chain_report"]["verdict"] == "intact"
    assert [item["checkpoint_number"] for item in kit["items"]] == [1, 2]
    # JSON-safety is the transport contract: the whole payload round-trips.
    rehydrated = json.loads(json.dumps(kit))
    assert rehydrated["manifest"]["checkpoint_ids"] == list(
        manifest["checkpoint_ids"]
    )
    system.cleanup()


def test_truncated_chains_export_with_the_honest_annotation():
    """
    Contract: retention dropout does not block export - the manifest
    carries the truncated_prefix verdict so importers see the history
    bounds.
    """
    system, emit = _system_with_journal_driver()
    system.set_checkpoint_retention(2)
    for _round in range(3):
        emit()
        system.create_checkpoint()
    kit = system.build_kit_payload()
    assert kit["manifest"]["chain_report"]["verdict"] == "truncated_prefix"
    assert kit["manifest"]["checkpoint_numbers"] == [2, 3]
    system.cleanup()


def test_import_is_insert_if_absent_and_idempotent():
    """
    Contract: a fresh ledger inserts every kit crystal; re-import skips
    every existing id (a kit never overwrites live history); the imported
    chain verifies intact and unfold targets resolve.
    """
    source, emit = _system_with_journal_driver()
    for _round in range(2):
        emit()
        source.create_checkpoint()
    kit = json.loads(json.dumps(source.build_kit_payload()))
    source.cleanup()

    target = PersistenceSystem()
    first = target.import_kit_payload(kit)
    assert first["profile_name"] == "default"
    assert len(first["inserted"]) == 2
    assert first["skipped_existing"] == []
    second = target.import_kit_payload(kit)
    assert second["inserted"] == []
    assert len(second["skipped_existing"]) == 2
    report = target.verify_checkpoint_chain()
    assert report["verdict"] == "intact"
    assert report["ledger_count"] == 2
    target.cleanup()
