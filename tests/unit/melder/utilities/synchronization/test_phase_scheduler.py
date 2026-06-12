import time
import threading

import pytest

from melder.utilities.synchronization.phase_scheduler import PhaseScheduler
from melder.utilities.synchronization.unit_of_work import UnitOfWork
from melder.utilities.custom_exceptions.phase_execution_error import PhaseExecutionError
from melder.utilities.custom_exceptions.phase_timeout_error import PhaseTimeoutError
from melder.utilities.custom_exceptions.phase_scheduler_error import PhaseSchedulerError


class DummyConfig:
    def __init__(self, workers=1, timeout_ms=100):
        self.values = {
            "phase_scheduler_workers_per_spellbook": workers,
            "phase_scheduler_barrier_timeout_milliseconds": timeout_ms,
        }

    def get_property(self, key):
        return self.values[key]


def test_register_phase_and_run_success():
    cfg = DummyConfig(workers=1, timeout_ms=500)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)

    uow = UnitOfWork(lambda: 123)
    uow.run_synchronously()
    scheduler.register_phase("p1", lambda: [uow])
    results = scheduler.run_all_phases("cid")
    assert "p1" in results
    assert results["p1"][0] is uow

    scheduler.cleanup()


def test_run_all_phases_raises_on_missing_factory():
    cfg = DummyConfig()
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    scheduler._phase_order.append("missing")
    with pytest.raises(PhaseSchedulerError):
        scheduler.run_all_phases("cid")


def test_run_single_phase_propagates_execution_error():
    cfg = DummyConfig()
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    err = RuntimeError("boom")
    uow = UnitOfWork(lambda: (_ for _ in ()).throw(err))
    with pytest.raises(RuntimeError):
        uow.run_synchronously()
    scheduler.register_phase("p1", lambda: [uow])
    with pytest.raises(PhaseExecutionError):
        scheduler.run_all_phases("cid")
    scheduler.cleanup()


def test_run_single_phase_timeout():
    cfg = DummyConfig(timeout_ms=1)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    # Simulate a UnitOfWork that won't finish before timeout
    uow = UnitOfWork(lambda: time.sleep(0.1))
    # leave it pending so wait() times out
    def slow_factory():
        return [uow]
    scheduler.register_phase("p1", slow_factory)
    with pytest.raises(PhaseTimeoutError):
        scheduler.run_all_phases("cid")
    scheduler.cleanup()


def test_run_single_phase_fail_fast_on_exception():
    cfg = DummyConfig(workers=2, timeout_ms=200)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    block_event = threading.Event()

    def blocking():
        block_event.wait()
        return "done"

    err = RuntimeError("boom")
    failing = UnitOfWork(lambda: (_ for _ in ()).throw(err))
    blocking_uow = UnitOfWork(blocking)

    scheduler.register_phase("p1", lambda: [blocking_uow, failing])
    try:
        with pytest.raises(PhaseExecutionError):
            scheduler.run_all_phases("cid")
    finally:
        block_event.set()
        scheduler.cleanup()


def test_run_single_phase_fail_fast_on_cancel():
    cfg = DummyConfig(workers=1, timeout_ms=500)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    block_event = threading.Event()

    def blocking():
        block_event.wait()
        return "done"

    uow = UnitOfWork(blocking)

    scheduler.register_phase("p1", lambda: [uow])

    def trigger_cancel():
        time.sleep(0.05)
        scheduler.cancel()

    canceller = threading.Thread(target=trigger_cancel, daemon=True)
    canceller.start()
    try:
        with pytest.raises(PhaseSchedulerError):
            scheduler.run_all_phases("cid")
    finally:
        block_event.set()
        scheduler.cleanup()


def test_cleanup_idempotent_and_cancels():
    cfg = DummyConfig()
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    scheduler.cleanup()
    scheduler.cleanup()  # idempotent
    # after cleanup, using check_cleaned should raise
    with pytest.raises(RuntimeError):
        scheduler.check_cleaned()


def test_multi_worker_executes_all_units():
    cfg = DummyConfig(workers=5, timeout_ms=500)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    executed: list[int] = []
    lock = threading.Lock()

    def make_uow(idx: int) -> UnitOfWork:
        def _fn():
            time.sleep(0.01)
            with lock:
                executed.append(idx)
            return idx

        return scheduler.create_unit_of_work(_fn)

    units = [make_uow(i) for i in range(10)]
    scheduler.register_phase("p1", lambda: units)

    results = scheduler.run_all_phases("cid")
    assert scheduler.workers == 5
    assert len(executed) == 10
    assert sorted(executed) == list(range(10))
    # results contain all units and each has a result
    assert "p1" in results
    assert len(results["p1"]) == 10
    assert all(u.result() in executed for u in results["p1"])

    scheduler.cleanup()


def test_multiple_phases_and_thread_pool_reuse():
    cfg = DummyConfig(workers=10, timeout_ms=500)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)

    phase1_units = [scheduler.create_unit_of_work(lambda: "a") for _ in range(3)]
    phase2_units = [scheduler.create_unit_of_work(lambda: "b") for _ in range(4)]

    scheduler.register_phase("phase1", lambda: phase1_units)
    scheduler.register_phase("phase2", lambda: phase2_units)

    results = scheduler.run_all_phases("cid")

    assert scheduler.workers == 10
    assert scheduler._workers_started is True
    assert len(scheduler._threads) == 10

    assert list(results.keys()) == ["phase1", "phase2"]
    assert [u.result() for u in results["phase1"]] == ["a"] * 3
    assert [u.result() for u in results["phase2"]] == ["b"] * 4

    scheduler.cleanup()


def test_idle_workers_survive_empty_queue_timeouts_between_phases():
    cfg = DummyConfig(workers=5, timeout_ms=2000)

    class InspectPhaseScheduler(PhaseScheduler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.alive_before_phase: dict[str, int] = {}

        def _run_single_phase(self, phase_name, factory):
            self.alive_before_phase[phase_name] = sum(
                1 for thread in self._threads if thread.is_alive()
            )
            return super()._run_single_phase(phase_name, factory)

    scheduler = InspectPhaseScheduler(spellbook=object(), configuration=cfg)

    scheduler.register_phase(
        "p1",
        lambda: [scheduler.create_unit_of_work(lambda: time.sleep(0.35))],
    )
    scheduler.register_phase(
        "p2",
        lambda: [scheduler.create_unit_of_work(lambda: "ok")],
    )

    try:
        results = scheduler.run_all_phases("cid")
        assert results["p2"][0].result() == "ok"
        assert scheduler.alive_before_phase["p2"] == scheduler.workers
    finally:
        scheduler.cleanup()


def test_persistent_pool_reuses_same_threads_across_runs():
    # v2 contract: one worker pool serves every run for the scheduler's
    # lifetime; a second run spawns no new threads.
    cfg = DummyConfig(workers=3, timeout_ms=2000)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    try:
        scheduler.register_phase(
            "run1",
            lambda: [scheduler.create_unit_of_work(lambda: "a")],
        )
        scheduler.run_all_phases("cid")
        first_threads = list(scheduler._threads)
        assert len(first_threads) == 3

        scheduler.register_phase(
            "run2",
            lambda: [scheduler.create_unit_of_work(lambda: "b")],
        )
        results = scheduler.run_all_phases("cid")
        assert results["run2"][0].result() == "b"
        assert scheduler._threads == first_threads
        assert all(thread.is_alive() for thread in scheduler._threads)
    finally:
        scheduler.cleanup()


def test_per_run_cancellation_scope_does_not_poison_next_run():
    # v2 contract: a failed/aborted run's cancellation cannot leak into the
    # next run on the same persistent pool.
    cfg = DummyConfig(workers=2, timeout_ms=2000)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    try:
        err = RuntimeError("boom")
        scheduler.register_phase(
            "failing",
            lambda: [
                scheduler.create_unit_of_work(
                    lambda: (_ for _ in ()).throw(err)
                )
            ],
        )
        with pytest.raises(PhaseExecutionError):
            scheduler.run_all_phases("cid")
        assert scheduler.is_cancelled is True

        scheduler.register_phase(
            "healthy",
            lambda: [scheduler.create_unit_of_work(lambda: "ok")],
        )
        results = scheduler.run_all_phases("cid")
        assert results["healthy"][0].result() == "ok"
        assert scheduler.is_cancelled is False
    finally:
        scheduler.cleanup()


def test_registrations_are_cleared_after_every_run_outcome():
    # v2 contract: phase registrations are per-run state in all outcomes.
    cfg = DummyConfig(workers=1, timeout_ms=2000)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    try:
        scheduler.register_phase(
            "p1",
            lambda: [scheduler.create_unit_of_work(lambda: 1)],
        )
        scheduler.run_all_phases("cid")
        assert scheduler.run_all_phases("cid") == {}

        scheduler.register_phase(
            "failing",
            lambda: [
                scheduler.create_unit_of_work(
                    lambda: (_ for _ in ()).throw(RuntimeError("boom"))
                )
            ],
        )
        with pytest.raises(PhaseExecutionError):
            scheduler.run_all_phases("cid")
        assert scheduler.run_all_phases("cid") == {}
    finally:
        scheduler.cleanup()


def test_clear_phases_discards_stale_registrations_before_run():
    cfg = DummyConfig(workers=1, timeout_ms=2000)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    try:
        scheduler.register_phase(
            "stale",
            lambda: [scheduler.create_unit_of_work(lambda: "stale")],
        )
        scheduler.clear_phases()
        assert scheduler.run_all_phases("cid") == {}
        # The name is reusable after clearing.
        scheduler.register_phase(
            "stale",
            lambda: [scheduler.create_unit_of_work(lambda: "fresh")],
        )
        results = scheduler.run_all_phases("cid")
        assert results["stale"][0].result() == "fresh"
    finally:
        scheduler.cleanup()


def test_cleanup_terminates_pool_threads():
    cfg = DummyConfig(workers=4, timeout_ms=2000)
    scheduler = PhaseScheduler(spellbook=object(), configuration=cfg)
    scheduler.register_phase(
        "p1",
        lambda: [scheduler.create_unit_of_work(lambda: "x")],
    )
    scheduler.run_all_phases("cid")
    threads = list(scheduler._threads)
    assert len(threads) == 4
    scheduler.cleanup()
    for thread in threads:
        thread.join(timeout=5.0)
    assert not any(thread.is_alive() for thread in threads)
