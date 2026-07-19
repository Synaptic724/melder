"""
Unit lifecycle tests for RestoreEngine's driver dispatch and single-use
law over EMPTY worlds (wave 3, 2026-07-19): both drivers must complete an
empty folded chain identically (parity on empty worlds is a documented S4
edge), the engine is single-use, and fold honesty rides the returned
report.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.crystallizer.crystal_loader_system.restore_engine import (
    RestoreEngine,
)
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler


def _empty_window():
    """
    Build one empty sealed window.

    Returns:
        dict: A journal-less, payload-less replay window.
    """
    return {"journal": [], "payloads": {}}


def test_sequential_restore_of_an_empty_world_completes():
    """
    Purpose:
        Pin the empty-world law on the sequential driver: nothing to
        build is a SUCCESS, not an error.
    Contract:
        status complete, zero built counts, empty plan (sequential never
        populates one), no shortfalls.
    Returns:
        None.
    Raises:
        AssertionError: If an empty world fails or fabricates units.
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-empty"],
        chain=[_empty_window()],
    )
    report = engine.restore()
    payload = report.describe()
    assert payload["status"] == "complete"
    assert payload["built_counts"] == {}
    assert payload["plan"] == {}
    assert payload["shortfalls"] == []
    engine.cleanup()
    report.cleanup()


def test_parallel_restore_of_an_empty_world_completes_with_empty_plan():
    """
    Purpose:
        Pin the S4 empty-plan edge: the parallel driver over an empty
        fold registers ZERO level phases and completes (parity with
        sequential on empty worlds by contract).
    Contract:
        status complete; plan summary present with level_count 0 and an
        empty nodes_per_level list.
    Returns:
        None.
    Raises:
        AssertionError: If the empty plan fails or fabricates levels.
    """
    scheduler = PhaseScheduler(
        spellbook=None,
        configuration=None,
        worker_count=1,
        barrier_timeout_ms=5000,
    )
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-empty"],
        chain=[_empty_window()],
        scheduler=scheduler,
    )
    try:
        report = engine.restore()
        payload = report.describe()
        assert payload["status"] == "complete"
        assert payload["plan"] == {
            "level_count": 0, "nodes_per_level": [],
        }
        assert payload["built_counts"] == {}
        report.cleanup()
    finally:
        engine.cleanup()
        scheduler.cleanup()


def test_engine_is_single_use():
    """
    Purpose:
        Pin the single-use law: a consumed engine refuses a second
        restore with remediation text.
    Contract:
        Second restore() raises RuntimeError naming the fresh-engine
        remedy.
    Returns:
        None.
    Raises:
        AssertionError: If a consumed engine restores twice.
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-once"],
        chain=[_empty_window()],
    )
    report = engine.restore()
    with pytest.raises(RuntimeError, match="single-use"):
        engine.restore()
    engine.cleanup()
    report.cleanup()


def test_cleaned_engine_refuses_restore():
    """
    Purpose:
        Pin the terminal cleanup law on the driver entry.
    Contract:
        restore() after cleanup() raises RuntimeError (check_cleaned).
    Returns:
        None.
    Raises:
        AssertionError: If a cleaned engine still restores.
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-cleaned"],
        chain=[_empty_window()],
    )
    engine.cleanup()
    with pytest.raises(RuntimeError):
        engine.restore()


def test_fold_honesty_shortfalls_ride_the_completed_report():
    """
    Purpose:
        Pin the honesty surface end to end at unit grade: a capture
        anomaly found during fold is visible on the COMPLETED report the
        caller receives (fold gaps never block an otherwise-empty
        restore; they report).
    Contract:
        The journal-without-payload shortfall appears in the returned
        report's describe() beside status complete.
    Returns:
        None.
    Raises:
        AssertionError: If fold honesty is dropped from the outcome.
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-gap"],
        chain=[{"journal": [[1, "spell_index", "idx-ghost"]],
                "payloads": {}}],
    )
    report = engine.restore()
    payload = report.describe()
    assert payload["status"] == "complete"
    assert payload["shortfalls"] == [{
        "kind": "spell_index", "key": "idx-ghost",
        "reason": "journal_entry_without_captured_payload",
    }]
    engine.cleanup()
    report.cleanup()
