"""
Component tests for the S2+S3 composition that lets a parallel restore
execute behind held load authority (parallel_restore_ulid_identity, second
safety wave 2026-07-19): a REAL PhaseScheduler pool and a REAL LoadGate,
wired exactly the way CrystalLoaderSystem wires them - the span holder
enrolls the pool's worker idents, level units check passage from worker
threads, foreign threads park, and release restores the single-thread law.

Most rows drive the mechanism in isolation (no hosted world); the two
Aether-verb rows boot the real hosted singletons briefly to pin the
delegation layer the loader actually calls, resetting them around the
test.

Runs only on 3.14t (melder package root import chain).
"""
import threading

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.phase_execution_error import (
    PhaseExecutionError,
)
from melder.utilities.synchronization.load_gate import LoadGate
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler


def _pool(workers=2):
    """
    Build one explicit-lane scheduler pool (the loader's construction).

    Returns:
        PhaseScheduler: A live pool with `workers` threads.
    """
    return PhaseScheduler(
        spellbook=None,
        configuration=None,
        worker_count=workers,
        barrier_timeout_ms=10000,
    )


def test_enrolled_pool_workers_pass_the_held_gate_and_foreign_parks():
    """
    Purpose:
        The restore-worker admission law end to end: while the span holder
        keeps the gate, enrolled pool workers pass wait_for_passage inside
        scheduler units, and a foreign thread parks until its deadline.
    Contract:
        - Every unit on the enrolled pool returns from wait_for_passage
          and the phase completes while the gate is HELD.
        - A non-member thread's wait raises RuntimeError naming the span
          label; after release the same check passes immediately.
    Returns:
        None.
    Raises:
        AssertionError: If a worker parks or a foreign thread passes.
    """
    gate = LoadGate()
    scheduler = _pool(workers=2)
    try:
        gate.acquire("restore-span")
        for ident in scheduler.worker_thread_idents():
            gate.enroll_worker(ident)

        passed = []

        def unit_body(index):
            gate.wait_for_passage(timeout=2.0)
            passed.append(index)
            return index

        def factory():
            return [
                scheduler.create_unit_of_work(unit_body, args=(index,))
                for index in range(4)
            ]

        scheduler.register_phase("level_0", factory)
        scheduler.run_all_phases()
        assert sorted(passed) == [0, 1, 2, 3]
        assert gate.is_held() is True

        foreign_error = []

        def foreign():
            try:
                gate.wait_for_passage(timeout=0.3)
            except RuntimeError as error:
                foreign_error.append(str(error))

        outsider = threading.Thread(target=foreign)
        outsider.start()
        outsider.join()
        assert len(foreign_error) == 1
        assert "restore-span" in foreign_error[0]

        gate.release()
        assert gate.is_held() is False

        after = []

        def foreign_after():
            gate.wait_for_passage(timeout=0.3)
            after.append(True)

        latecomer = threading.Thread(target=foreign_after)
        latecomer.start()
        latecomer.join()
        assert after == [True]
    finally:
        scheduler.cleanup()
        gate.cleanup()


def test_release_clears_membership_for_the_next_span():
    """
    Purpose:
        The S3 no-survival law composed through the scheduler: release()
        clears the cohort, so the NEXT span parks the same pool workers
        unless the holder re-enrolls them - and that parking surfaces as
        the scheduler's own fail-fast error.
    Contract:
        Span 1 (enrolled) completes. Span 2 (NOT re-enrolled) fails:
        the unit's wait_for_passage times out and run_all_phases raises
        PhaseExecutionError carrying the level name.
    Returns:
        None.
    Raises:
        AssertionError: If membership leaks across spans.
    """
    gate = LoadGate()
    scheduler = _pool(workers=1)
    try:
        gate.acquire("span-one")
        for ident in scheduler.worker_thread_idents():
            gate.enroll_worker(ident)

        def passing_factory():
            return [
                scheduler.create_unit_of_work(
                    gate.wait_for_passage, kwargs={"timeout": 2.0}
                )
            ]

        scheduler.register_phase("level_0", passing_factory)
        scheduler.run_all_phases()
        gate.release()

        gate.acquire("span-two")
        scheduler.clear_phases()

        def parked_factory():
            return [
                scheduler.create_unit_of_work(
                    gate.wait_for_passage, kwargs={"timeout": 0.3}
                )
            ]

        scheduler.register_phase("level_0", parked_factory)
        with pytest.raises(PhaseExecutionError) as raised:
            scheduler.run_all_phases()
        assert raised.value.phase_name == "level_0"
        gate.release()
    finally:
        scheduler.cleanup()
        gate.cleanup()


def test_holder_thread_passes_alone_without_enrollment():
    """
    Purpose:
        The default-span sanity row: a cohort of one - the holder itself -
        passes its own gate with a live but UNENROLLED pool standing by.
    Contract:
        wait_for_passage on the holder thread returns immediately while
        the gate is held and the pool's workers were never enrolled.
    Returns:
        None.
    Raises:
        AssertionError: If the holder's own passage regresses.
    """
    gate = LoadGate()
    scheduler = _pool(workers=1)
    try:
        scheduler.worker_thread_idents()
        gate.acquire("solo-span")
        gate.wait_for_passage(timeout=0.5)
        assert gate.is_held() is True
        gate.release()
    finally:
        scheduler.cleanup()
        gate.cleanup()


def test_consecutive_spans_with_reenrollment_both_pass():
    """
    Purpose:
        Pin span repeatability: the loader runs load after load on ONE
        persistent pool - every span re-enrolls the same idents and every
        span's units must pass.
    Contract:
        Two acquire/enroll/run/release cycles both complete with the
        pool's units passing the held gate each time.
    Returns:
        None.
    Raises:
        AssertionError: If a second span regresses after the first.
    """
    gate = LoadGate()
    scheduler = _pool(workers=2)
    try:
        for span_index in range(2):
            gate.acquire("span-{0}".format(span_index))
            for ident in scheduler.worker_thread_idents():
                gate.enroll_worker(ident)

            def factory():
                return [
                    scheduler.create_unit_of_work(
                        gate.wait_for_passage, kwargs={"timeout": 2.0}
                    )
                    for _ in range(2)
                ]

            scheduler.clear_phases()
            scheduler.register_phase("level_0", factory)
            scheduler.run_all_phases()
            assert gate.is_held() is True
            gate.release()
            assert gate.is_held() is False
    finally:
        scheduler.cleanup()
        gate.cleanup()


def test_aether_authority_verbs_wire_the_same_mechanism():
    """
    Purpose:
        Pin the Aether wiring layer the loader actually calls:
        acquire_load_authority claims the hosted gate, enroll_load_worker
        admits pool idents, and release_load_authority restores the
        single-thread law - the exact verb chain of a mediated load span.
    Contract:
        Enrolled pool units pass through scheduler execution while the
        authority is held; the hosted gate reports held/released truth.
    Returns:
        None.
    Raises:
        AssertionError: If the Aether delegation drifts from the gate.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    scheduler = _pool(workers=2)
    try:
        aether = Aether()
        aether.acquire_load_authority("component-span")
        try:
            for ident in scheduler.worker_thread_idents():
                aether.enroll_load_worker(ident)
            assert aether._load_gate.is_held() is True

            def factory():
                return [
                    scheduler.create_unit_of_work(
                        aether._load_gate.wait_for_passage,
                        kwargs={"timeout": 2.0},
                    )
                    for _ in range(2)
                ]

            scheduler.register_phase("level_0", factory)
            scheduler.run_all_phases()
        finally:
            aether.release_load_authority()
        assert aether._load_gate.is_held() is False
    finally:
        scheduler.cleanup()
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()


def test_aether_authority_refusal_edges():
    """
    Purpose:
        Pin the pairing bugs at the Aether layer: double-acquire refuses
        naming the holding span, and a foreign thread cannot release the
        holder's authority.
    Contract:
        Both misuses raise RuntimeError; the holder's release succeeds.
    Returns:
        None.
    Raises:
        AssertionError: If a pairing bug is admitted.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    try:
        aether = Aether()
        aether.acquire_load_authority("held-span")
        try:
            with pytest.raises(RuntimeError, match="held-span"):
                aether.acquire_load_authority("second-span")
            errors = []

            def foreign_release():
                try:
                    aether.release_load_authority()
                except RuntimeError as error:
                    errors.append(str(error))

            thread = threading.Thread(target=foreign_release)
            thread.start()
            thread.join()
            assert len(errors) == 1
            assert "held-span" in errors[0]
        finally:
            aether.release_load_authority()
        assert aether._load_gate.is_held() is False
    finally:
        Aether._reset_singleton_for_tests()
        AetherUtilitySystem._reset_singleton_for_tests()
        Nexus._reset_singleton_for_tests()
        Crystallizer._reset_singleton_for_tests()


def test_gate_cleanup_mid_span_wakes_parked_foreigner():
    """
    Purpose:
        Pin the terminal-open tombstone law composed with a REAL parked
        waiter: gate cleanup during a held span must wake the foreign
        thread and let it pass (teardown races never strand waiters).
    Contract:
        The foreign thread parked on wait_for_passage returns (no error)
        once cleanup opens the gate terminally.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup strands or errors the parked waiter.
    """
    gate = LoadGate()
    gate.acquire("doomed-span")
    outcomes = []
    parked = threading.Event()

    def foreigner():
        parked.set()
        try:
            gate.wait_for_passage(timeout=5.0)
            outcomes.append("passed")
        except RuntimeError:
            outcomes.append("timed_out")

    thread = threading.Thread(target=foreigner)
    thread.start()
    assert parked.wait(timeout=5.0) is True
    gate.cleanup()
    thread.join(timeout=5.0)
    assert outcomes == ["passed"]
