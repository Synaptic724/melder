"""
Unit safety tests for RestoreReport and the engine's built-stack teardown
(parallel_restore_ulid_identity S4, second safety wave 2026-07-19).

The parallel driver made the report a shared object: per-entity units on
scheduler worker threads mutate it concurrently, and the built stack's
append order IS the all-or-nothing teardown order. These rows pin the
concurrency contract (one RLock, zero lost updates), the detachment
contract (describe() hands out copies; setters copy their inputs), the
failure state machine, and the newest-first best-effort teardown law.

Runs only on 3.14t (melder package root import chain).
"""
import threading

import pytest

from melder.crystallizer.crystal_loader_system.restore_engine import (
    RestoreEngine,
    RestoreReport,
)


def _report():
    """
    Build one minimal live report.

    Returns:
        RestoreReport: A report over a one-checkpoint chain identity.
    """
    return RestoreReport("default", ["ck-safety"])


def test_concurrent_record_built_loses_no_increments():
    """
    Purpose:
        Pin the S4 lock law: built counters mutated from many worker
        threads lose no increments (the parallel driver's units all call
        record_built on the SAME report).
    Contract:
        8 threads x 250 increments across 4 kinds -> every kind counts
        exactly 500 (two threads per kind).
    Returns:
        None.
    Raises:
        AssertionError: If any increment is lost under contention.
    """
    report = _report()
    kinds = ("spellbook", "conduit", "link", "cluster")

    def hammer(kind):
        for _ in range(250):
            report.record_built(kind)

    threads = [
        threading.Thread(target=hammer, args=(kinds[i % 4],))
        for i in range(8)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    counts = report.describe()["built_counts"]
    assert counts == {kind: 500 for kind in kinds}


def test_concurrent_identity_and_shortfall_writes_lose_no_rows():
    """
    Purpose:
        Pin the same lock law over the identity map (per-key disjoint
        writes) and the shortfall ledger (append-only honesty rows).
    Contract:
        6 threads x 200 disjoint identities and 6 x 100 shortfalls ->
        1200 mapped identities, 600 shortfall rows, none corrupted.
    Returns:
        None.
    Raises:
        AssertionError: If a mapping or honesty row is lost.
    """
    report = _report()

    def map_many(prefix):
        for index in range(200):
            report.map_identity(
                "rec-{0}-{1}".format(prefix, index),
                "live-{0}-{1}".format(prefix, index),
            )

    def shortfall_many(prefix):
        for index in range(100):
            report.add_shortfall(
                "link", "key-{0}-{1}".format(prefix, index), "reason"
            )

    threads = [
        threading.Thread(target=map_many, args=(i,)) for i in range(6)
    ] + [
        threading.Thread(target=shortfall_many, args=(i,)) for i in range(6)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    payload = report.describe()
    assert len(payload["identity_map"]) == 1200
    assert len(payload["shortfalls"]) == 600
    assert report.translate("rec-0-0") == "live-0-0"
    assert report.translate("rec-none") is None


def test_describe_hands_out_detached_copies():
    """
    Purpose:
        Pin the detachment law: mutating a described payload must never
        write through into the report (consumers hold VALUE copies).
    Contract:
        Mutations on every outer container of one describe() result leave
        a fresh describe() unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If a described container aliases report state.
    """
    report = _report()
    report.record_built("spellbook")
    report.add_shortfall("link", "k", "r")
    report.map_identity("rec", "live")
    report.set_plan_summary({"level_count": 1, "nodes_per_level": [2]})

    tampered = report.describe()
    tampered["built_counts"]["spellbook"] = 999
    tampered["shortfalls"].append({"kind": "x", "key": "x", "reason": "x"})
    tampered["identity_map"]["rec"] = "poisoned"
    tampered["plan"]["level_count"] = 999
    tampered["checkpoint_ids"].append("ck-phantom")

    fresh = report.describe()
    assert fresh["built_counts"] == {"spellbook": 1}
    assert fresh["shortfalls"] == [
        {"kind": "link", "key": "k", "reason": "r"}
    ]
    assert fresh["identity_map"] == {"rec": "live"}
    assert fresh["plan"]["level_count"] == 1
    assert fresh["checkpoint_ids"] == ["ck-safety"]


def test_summary_setters_copy_their_inputs():
    """
    Purpose:
        Pin input detachment: the plan/preflight setters copy the supplied
        dict, so a caller mutating its own dict later cannot corrupt the
        sealed report.
    Contract:
        Mutating the source dicts after set_plan_summary/set_preflight
        leaves the described payload on the values set at call time.
    Returns:
        None.
    Raises:
        AssertionError: If a setter aliases its input.
    """
    report = _report()
    plan = {"level_count": 3, "nodes_per_level": [1, 2, 3]}
    preflight = {"verdict": "clean"}
    report.set_plan_summary(plan)
    report.set_preflight(preflight)
    plan["level_count"] = 999
    preflight["verdict"] = "poisoned"
    payload = report.describe()
    assert payload["plan"]["level_count"] == 3
    assert payload["preflight"]["verdict"] == "clean"


def test_failure_marks_status_and_stage():
    """
    Purpose:
        Pin the failure state machine the drivers rely on: mark_failed
        names the stage; a later mark_complete (the success path) is a
        distinct terminal write.
    Contract:
        After mark_failed("level_2"): status "failed", failed_stage
        "level_2". A fresh report marked complete reads "complete" with a
        None failed_stage.
    Returns:
        None.
    Raises:
        AssertionError: If the status/stage law drifts.
    """
    failed = _report()
    failed.mark_failed("level_2")
    payload = failed.describe()
    assert payload["status"] == "failed"
    assert payload["failed_stage"] == "level_2"

    completed = _report()
    completed.mark_complete()
    payload = completed.describe()
    assert payload["status"] == "complete"
    assert payload["failed_stage"] is None


def test_report_constructor_refuses_empty_identity():
    """
    Purpose:
        Pin the identity refusals: a report cannot exist without its
        profile and chain identity.
    Contract:
        Empty profile_name and empty checkpoint_ids each raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If an unidentified report constructs.
    """
    with pytest.raises(ValueError, match="profile_name"):
        RestoreReport("", ["ck-1"])
    with pytest.raises(ValueError, match="checkpoint id"):
        RestoreReport("default", [])


def test_cleaned_report_refuses_every_verb_idempotently():
    """
    Purpose:
        Pin the terminal cleanup law: a cleaned report refuses every
        mutator and reader, and cleanup stays idempotent.
    Contract:
        Double cleanup passes; each verb raises RuntimeError afterwards.
    Returns:
        None.
    Raises:
        AssertionError: If a cleaned report still answers.
    """
    report = _report()
    report.cleanup()
    report.cleanup()
    with pytest.raises(RuntimeError):
        report.record_built("spellbook")
    with pytest.raises(RuntimeError):
        report.add_shortfall("k", "k", "r")
    with pytest.raises(RuntimeError):
        report.map_identity("a", "b")
    with pytest.raises(RuntimeError):
        report.translate("a")
    with pytest.raises(RuntimeError):
        report.describe()
    with pytest.raises(RuntimeError):
        report.mark_complete()
    with pytest.raises(RuntimeError):
        report.mark_failed("stage")


class _TeardownProbe:
    """Stubbed built unit recording its own teardown order."""

    def __init__(self, name, order, explode=False):
        self.name = name
        self.cleaned = False
        self._order = order
        self._explode = explode

    def cleanup(self):
        self._order.append(self.name)
        if self._explode:
            raise RuntimeError("teardown noise from {0}".format(self.name))
        self.cleaned = True


def test_built_stack_teardown_runs_newest_first_and_survives_noise():
    """
    Purpose:
        Pin the all-or-nothing ordering law: teardown pops the built stack
        newest first, and one raising unit must not stop the pop (its
        failure is noise; the run's stage error is the signal).
    Contract:
        Units recorded a-b-c-d tear down d-c-b-a even when c raises; the
        stack ends empty and the live maps end cleared.
    Returns:
        None.
    Raises:
        AssertionError: If teardown order or the best-effort law drifts.
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-teardown"],
        chain=[{"journal": [], "payloads": {}}],
    )
    try:
        order = []
        for name, explode in (
                ("a", False), ("b", False), ("c", True), ("d", False)
        ):
            engine._record_built_unit(
                "conduit", _TeardownProbe(name, order, explode)
            )
        engine._live_conduits["probe"] = object()
        engine._teardown_built()
        assert order == ["d", "c", "b", "a"]
        assert engine._built_stack == []
        assert engine._live_conduits == {}
    finally:
        engine.cleanup()


def test_concurrent_built_stack_appends_lose_no_units():
    """
    Purpose:
        Pin the build-lock law: _record_built_unit appends from many
        threads (the parallel level units) lose nothing, so teardown can
        always reach every built unit.
    Contract:
        6 threads x 100 units -> 600 stack entries.
    Returns:
        None.
    Raises:
        AssertionError: If an append is lost under contention.
    """
    engine = RestoreEngine(
        profile_name="default",
        checkpoint_ids=["ck-stack"],
        chain=[{"journal": [], "payloads": {}}],
    )
    try:
        order = []

        def hammer():
            for _ in range(100):
                engine._record_built_unit(
                    "conduit", _TeardownProbe("x", order)
                )

        threads = [threading.Thread(target=hammer) for _ in range(6)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert len(engine._built_stack) == 600
    finally:
        engine.cleanup()
