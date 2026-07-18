"""
Unit tests for the chain-integrity verb (verify_checkpoint_chain) and the
retention-safe checkpoint numbering it guards: intact chains, empty-window
markers, retention-truncated prefixes, full-dropout restarts, damaged
ledgers with break evidence, and the BUG-159 restorability gate (only an
intact chain folds back to the true world).

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.crystallizer.persistence.persistence_crystal import (
    PersistenceCrystal,
)
from melder.crystallizer.persistence.persistence_system import (
    PersistenceSystem,
)
from melder.crystallizer.crystals.recorded_unit_state import (
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


def test_intact_chain_reports_contiguous_from_one():
    """
    Contract: sequential seals with journal traffic verdict "intact" with
    numbers 1..N and zero dropped prefix.
    """
    system, emit = _system_with_journal_driver()
    for _round in range(3):
        emit()
        system.create_checkpoint()
    report = system.verify_checkpoint_chain()
    assert report["verdict"] == "intact"
    assert report["restorable"] is True
    assert report["ledger_count"] == 3
    assert report["first_checkpoint_number"] == 1
    assert report["last_checkpoint_number"] == 3
    assert report["dropped_prefix_count"] == 0
    assert report["breaks"] == []
    system.cleanup()


def test_empty_ledger_reports_empty_verdict():
    """
    Contract: a profile with no seals reports "empty" with null bounds.
    """
    system, _emit = _system_with_journal_driver()
    report = system.verify_checkpoint_chain()
    assert report["verdict"] == "empty"
    assert report["restorable"] is False
    assert report["ledger_count"] == 0
    assert report["first_checkpoint_number"] is None
    system.cleanup()


def test_empty_seal_windows_list_without_breaking_the_verdict():
    """
    Contract: a marker checkpoint over an empty window (first == last + 1)
    lists in empty_windows and the chain stays "intact".
    """
    system, emit = _system_with_journal_driver()
    emit()
    system.create_checkpoint()
    marker_id = system.create_checkpoint()
    report = system.verify_checkpoint_chain()
    assert report["verdict"] == "intact"
    assert report["restorable"] is True
    assert report["empty_windows"] == [marker_id]
    system.cleanup()


def test_retention_dropout_reports_truncated_prefix_and_mints_no_duplicates():
    """
    Contract: FIFO dropout truncates the head - the verdict says so - and
    the max-based mint keeps numbering monotonic (the count-based mint
    duplicated numbers exactly here).
    """
    system, emit = _system_with_journal_driver()
    system.set_checkpoint_retention(2)
    for _round in range(3):
        emit()
        system.create_checkpoint()
    report = system.verify_checkpoint_chain()
    assert report["verdict"] == "truncated_prefix"
    assert report["restorable"] is False
    assert report["first_checkpoint_number"] == 2
    assert report["dropped_prefix_count"] == 1
    assert report["breaks"] == []
    emit()
    system.create_checkpoint()
    after = system.verify_checkpoint_chain()
    assert after["last_checkpoint_number"] == 4
    duplicate_breaks = [
        row for row in after["breaks"]
        if row["kind"] == "duplicate_checkpoint_number"
    ]
    assert duplicate_breaks == []
    system.cleanup()


def test_full_dropout_restart_is_detected_by_the_first_window():
    """
    Contract: when every crystal of a profile is gone, fresh numbering
    restarts at 1 - but the first retained window starting past sequence 1
    still betrays the lost prefix ("truncated_prefix", never "intact").
    """
    system, emit = _system_with_journal_driver()
    emit()
    system.create_checkpoint()
    # Test surgery: simulate total dropout of the profile's history.
    for checkpoint_id in list(system._checkpoint_crystals_by_id.keys()):
        system._checkpoint_crystals_by_id.pop(checkpoint_id).cleanup()
    emit()
    system.create_checkpoint()
    report = system.verify_checkpoint_chain()
    assert report["first_checkpoint_number"] == 1
    assert report["dropped_prefix_count"] == 0
    assert report["verdict"] == "truncated_prefix"
    assert report["restorable"] is False
    system.cleanup()


def test_missing_middle_crystal_reports_broken_with_evidence():
    """
    Contract: a gap in the retained run reports "broken" carrying BOTH the
    number-gap and window-discontinuity evidence rows.
    """
    system, emit = _system_with_journal_driver()
    seal_ids = []
    for _round in range(3):
        emit()
        seal_ids.append(system.create_checkpoint())
    system._checkpoint_crystals_by_id.pop(seal_ids[1]).cleanup()
    report = system.verify_checkpoint_chain()
    assert report["verdict"] == "broken"
    assert report["restorable"] is False
    kinds = sorted(row["kind"] for row in report["breaks"])
    assert kinds == ["checkpoint_number_gap", "window_discontinuity"]
    system.cleanup()


def test_duplicate_checkpoint_number_reports_broken():
    """
    Contract: two retained crystals sharing one checkpoint number report a
    duplicate_checkpoint_number break.
    """
    system, emit = _system_with_journal_driver()
    emit()
    system.create_checkpoint()
    forged = PersistenceCrystal(
        checkpoint_id="01FORGEDDUPLICATE0000000000",
        profile_name="default",
        checkpoint_number=1,
        description="forged duplicate",
        journal_segment=[],
        captured_payloads={},
        sequence_range=(2, 1),
    )
    system._checkpoint_crystals_by_id[forged.id] = forged
    report = system.verify_checkpoint_chain()
    assert report["verdict"] == "broken"
    assert report["restorable"] is False
    assert any(
        row["kind"] == "duplicate_checkpoint_number"
        for row in report["breaks"]
    )
    system.cleanup()


def test_unknown_profile_raises_and_cleaned_system_guards():
    """
    Contract: unknown profile names raise the standard self-correcting
    KeyError; a cleaned system refuses the verb.
    """
    system, _emit = _system_with_journal_driver()
    with pytest.raises(KeyError):
        system.verify_checkpoint_chain("no_such_profile")
    system.cleanup()
    with pytest.raises(RuntimeError):
        system.verify_checkpoint_chain()


def test_bug159_retention_dropped_baseline_is_not_restorable():
    """
    BUG-159 (Critical) regression: with retention cap one, seal Nexus state,
    then seal an unrelated MutationResearch state. FIFO drops the Nexus
    baseline, so the surviving single-crystal chain can no longer fold back to
    the true (Nexus + MutationResearch) world. The integrity verb must refuse
    to certify it: verdict stays "truncated_prefix" but restorable is False -
    never the old "a fold yields the post-prefix world" reading that let a
    restore silently rebuild a world missing the evicted state.
    """
    system = PersistenceSystem()
    system.set_checkpoint_retention(1)
    system.record_nexus_state(RecordedUnitState.enabled)
    system.create_checkpoint()
    system.record_mutation_research_state(RecordedUnitState.enabled)
    system.create_checkpoint()
    report = system.verify_checkpoint_chain()
    # The baseline that uniquely held Nexus state was evicted by retention.
    assert report["ledger_count"] == 1
    assert report["dropped_prefix_count"] == 1
    assert report["verdict"] == "truncated_prefix"
    assert report["breaks"] == []
    # BUG-159 fix: the gate must NOT declare the truncated chain usable.
    assert report["restorable"] is False
    system.cleanup()


def test_intact_chain_is_restorable_control():
    """
    Positive control for the restorability gate: a contiguous chain that
    still holds its baseline (checkpoint 1, sequence 1) is restorable.
    """
    system, emit = _system_with_journal_driver()
    for _round in range(2):
        emit()
        system.create_checkpoint()
    report = system.verify_checkpoint_chain()
    assert report["verdict"] == "intact"
    assert report["restorable"] is True
    system.cleanup()
