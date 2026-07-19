"""
Component tests for the PhaseScheduler pipeline guarantees the parallel
restore driver stands on (parallel_restore_ulid_identity S4, wave 3): the
inter-phase barrier, fail-fast gating of later phases, pool persistence
across runs, and true multi-thread execution - each proven with real
UnitOfWork objects on a real explicit-lane pool.

Runs only on 3.14t (melder package root import chain).
"""
import threading

import pytest

from melder.utilities.custom_exceptions.phase_execution_error import (
    PhaseExecutionError,
)
from melder.utilities.synchronization.phase_scheduler import PhaseScheduler


def _pool(workers):
    """
    Build one explicit-lane pool.

    Returns:
        PhaseScheduler: A live pool with `workers` threads.
    """
    return PhaseScheduler(
        spellbook=None,
        configuration=None,
        worker_count=workers,
        barrier_timeout_ms=10000,
    )


def test_next_phase_factory_observes_every_prior_phase_result():
    """
    Purpose:
        Pin the barrier law level replay relies on: a later level's
        factory runs only after EVERY unit of the prior level completed -
        identity-map reads behind a passed barrier are safe by
        construction, not by discipline.
    Contract:
        The level_1 factory observes all four level_0 results at
        factory-invocation time.
    Returns:
        None.
    Raises:
        AssertionError: If a later factory runs before the barrier.
    """
    scheduler = _pool(workers=2)
    try:
        produced = []
        observed_at_factory_time = []

        def level_zero_factory():
            return [
                scheduler.create_unit_of_work(produced.append, args=(i,))
                for i in range(4)
            ]

        def level_one_factory():
            observed_at_factory_time.append(sorted(produced))
            return [scheduler.create_unit_of_work(lambda: None)]

        scheduler.register_phase("level_0", level_zero_factory)
        scheduler.register_phase("level_1", level_one_factory)
        scheduler.run_all_phases()
        assert observed_at_factory_time == [[0, 1, 2, 3]]
    finally:
        scheduler.cleanup()


def test_failed_phase_gates_the_next_phase_factory():
    """
    Purpose:
        Pin fail-fast at the phase boundary: after a level fails, the
        next level's factory must never run (no unit of a later level
        starts over a half-built prior level).
    Contract:
        PhaseExecutionError names the failing level and the level_1
        factory was never invoked.
    Returns:
        None.
    Raises:
        AssertionError: If a later level starts after a failure.
    """
    scheduler = _pool(workers=2)
    try:
        later_factory_ran = []

        def failing_factory():
            def explode():
                raise ValueError("poisoned unit")
            return [scheduler.create_unit_of_work(explode)]

        def later_factory():
            later_factory_ran.append(True)
            return [scheduler.create_unit_of_work(lambda: None)]

        scheduler.register_phase("level_0", failing_factory)
        scheduler.register_phase("level_1", later_factory)
        with pytest.raises(PhaseExecutionError) as raised:
            scheduler.run_all_phases()
        assert raised.value.phase_name == "level_0"
        assert later_factory_ran == []
    finally:
        scheduler.cleanup()


def test_persistent_pool_serves_consecutive_runs():
    """
    Purpose:
        Pin pool persistence: the loader owns ONE pool across every load,
        so consecutive run_all_phases calls must reuse the same worker
        threads and both complete.
    Contract:
        Worker idents are identical before and after two full runs; both
        runs execute their units.
    Returns:
        None.
    Raises:
        AssertionError: If the pool is rebuilt or a rerun regresses.
    """
    scheduler = _pool(workers=2)
    try:
        idents_before = scheduler.worker_thread_idents()
        outcomes = []
        for run_index in range(2):
            scheduler.clear_phases()
            scheduler.register_phase(
                "level_0",
                lambda run=run_index: [
                    scheduler.create_unit_of_work(
                        outcomes.append, args=(run,)
                    )
                ],
            )
            scheduler.run_all_phases()
        assert sorted(outcomes) == [0, 1]
        assert scheduler.worker_thread_idents() == idents_before
    finally:
        scheduler.cleanup()


def test_units_within_a_phase_run_on_distinct_threads_simultaneously():
    """
    Purpose:
        Pin real parallelism (the point of the whole program): two units
        in one phase meet at a shared Barrier - impossible unless both
        run at the same time on distinct pool threads.
    Contract:
        Both units pass the rendezvous within its bound and record two
        distinct worker idents.
    Returns:
        None.
    Raises:
        AssertionError: If in-phase units are serialized.
    """
    scheduler = _pool(workers=2)
    try:
        rendezvous = threading.Barrier(2, timeout=5.0)
        worker_idents = []
        record_lock = threading.Lock()

        def meet():
            rendezvous.wait()
            with record_lock:
                worker_idents.append(threading.get_ident())

        def factory():
            return [
                scheduler.create_unit_of_work(meet) for _ in range(2)
            ]

        scheduler.register_phase("level_0", factory)
        scheduler.run_all_phases()
        assert len(worker_idents) == 2
        assert len(set(worker_idents)) == 2
    finally:
        scheduler.cleanup()
