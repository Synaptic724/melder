import threading
import time

import pytest

from melder.utilities.synchronization.load_gate import LoadGate


def test_load_gate_initial_state_open() -> None:
    """
    Purpose:
        Verify a fresh gate starts open with no holder.
    Contract:
        - is_held() is False.
        - describe() reports no holder thread and no label.
    """
    gate = LoadGate()
    assert gate.is_held() is False
    snapshot = gate.describe()
    assert snapshot["holder_thread_id"] is None
    assert snapshot["holder_label"] is None
    gate.cleanup()


def test_load_gate_acquire_records_holder_and_label() -> None:
    """
    Purpose:
        Verify acquire claims the gate for the calling thread.
    Contract:
        - is_held() flips True.
        - describe() reports the calling thread id and the given label.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:01TEST")
    assert gate.is_held() is True
    snapshot = gate.describe()
    assert snapshot["holder_thread_id"] == threading.get_ident()
    assert snapshot["holder_label"] == "checkpoint_load:01TEST"
    gate.release()
    gate.cleanup()


def test_load_gate_acquire_requires_label() -> None:
    """
    Purpose:
        Verify acquire refuses falsy labels.
    Contract:
        - ValueError is raised; the gate stays open.
    """
    gate = LoadGate()
    with pytest.raises(ValueError):
        gate.acquire("")
    assert gate.is_held() is False
    gate.cleanup()


def test_load_gate_second_acquire_refuses_naming_holder() -> None:
    """
    Purpose:
        Verify one-load-at-a-time: a second acquire refuses, even from the
        holder thread (nested acquire is a pairing bug, not a wait).
    Contract:
        - RuntimeError names the holding load's label.
    """
    gate = LoadGate()
    gate.acquire("first_load")
    with pytest.raises(RuntimeError, match="first_load"):
        gate.acquire("second_load")
    gate.release()
    gate.cleanup()


def test_load_gate_release_requires_holder_thread() -> None:
    """
    Purpose:
        Verify release discipline.
    Contract:
        - Releasing an open gate raises RuntimeError.
        - Releasing from a non-holder thread raises RuntimeError.
    """
    gate = LoadGate()
    with pytest.raises(RuntimeError):
        gate.release()

    gate.acquire("owned_elsewhere")
    errors: list = []

    def foreign_release() -> None:
        try:
            gate.release()
        except RuntimeError as exc:
            errors.append(exc)

    thread = threading.Thread(target=foreign_release)
    thread.start()
    thread.join()
    assert len(errors) == 1
    assert gate.is_held() is True
    gate.release()
    gate.cleanup()


def test_load_gate_wait_for_passage_open_gate_is_noop() -> None:
    """
    Purpose:
        Verify the mediator hot path: an open gate passes immediately.
    Contract:
        - wait_for_passage returns without blocking.
    """
    gate = LoadGate()
    started = time.monotonic()
    gate.wait_for_passage(timeout=5.0)
    assert time.monotonic() - started < 1.0
    gate.cleanup()


def test_load_gate_holder_thread_passes_free() -> None:
    """
    Purpose:
        Verify the loading thread's own transactions pass while it holds the
        gate ("the loading thread has all control").
    Contract:
        - wait_for_passage returns immediately for the holder thread.
    """
    gate = LoadGate()
    gate.acquire("self_load")
    started = time.monotonic()
    gate.wait_for_passage(timeout=5.0)
    assert time.monotonic() - started < 1.0
    gate.release()
    gate.cleanup()


def test_load_gate_foreign_thread_waits_and_resumes_on_release() -> None:
    """
    Purpose:
        Verify a foreign thread parks during a load and resumes on release.
    Contract:
        - wait_for_passage blocks while held by another thread.
        - release() wakes the waiter before its timeout.
    """
    gate = LoadGate()
    gate.acquire("blocking_load")
    resumed = threading.Event()

    def foreign_wait() -> None:
        gate.wait_for_passage(timeout=10.0)
        resumed.set()

    thread = threading.Thread(target=foreign_wait)
    thread.start()
    time.sleep(0.2)
    assert resumed.is_set() is False

    gate.release()
    thread.join(timeout=5.0)
    assert resumed.is_set() is True
    gate.cleanup()


def test_load_gate_foreign_thread_timeout_names_load_label() -> None:
    """
    Purpose:
        Verify the teach-grade timeout: a starved waiter learns WHICH load
        holds the system.
    Contract:
        - RuntimeError message contains the holder label.
    """
    gate = LoadGate()
    gate.acquire("slow_world_load")
    errors: list = []

    def starved_wait() -> None:
        try:
            gate.wait_for_passage(timeout=0.2)
        except RuntimeError as exc:
            errors.append(str(exc))

    thread = threading.Thread(target=starved_wait)
    thread.start()
    thread.join(timeout=5.0)
    assert len(errors) == 1
    assert "slow_world_load" in errors[0]
    gate.release()
    gate.cleanup()


def test_load_gate_cleanup_wakes_waiters_and_is_idempotent() -> None:
    """
    Purpose:
        Verify teardown never strands a parked waiter.
    Contract:
        - cleanup() clears the holder and notifies waiters.
        - cleanup() is idempotent.
    """
    gate = LoadGate()
    gate.acquire("teardown_load")
    resumed = threading.Event()

    def parked_wait() -> None:
        gate.wait_for_passage(timeout=10.0)
        resumed.set()

    thread = threading.Thread(target=parked_wait)
    thread.start()
    time.sleep(0.2)

    gate.cleanup()
    thread.join(timeout=5.0)
    assert resumed.is_set() is True
    gate.cleanup()


# ---------------------------------------------------------------------------
# S3 cohort suite (parallel_restore_ulid_identity): span cohort membership.
# ---------------------------------------------------------------------------


def _run_in_thread(target) -> "threading.Thread":
    """
    Start one daemon helper thread for gate adversarial checks.

    Returns:
        threading.Thread: The started thread (caller joins it).
    """
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread


def test_cohort_member_passes_while_span_is_held() -> None:
    """
    Purpose:
        Prove the S3 admission law: an enrolled worker passes the gate
        while the span is held, without waiting.
    Contract:
        - wait_for_passage returns promptly for the member (no timeout).
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:cohort")
    outcomes = []

    def worker() -> None:
        gate.wait_for_passage(timeout=1.0)
        outcomes.append("passed")

    ready = threading.Event()

    def enrolled_worker() -> None:
        ready.wait(2.0)
        worker()

    thread = threading.Thread(target=enrolled_worker, daemon=True)
    thread.start()
    gate.enroll_worker(thread.ident)
    ready.set()
    thread.join(3.0)
    assert outcomes == ["passed"]
    gate.release()
    gate.cleanup()


def test_foreign_thread_still_parks_and_times_out_during_cohort_span() -> None:
    """
    Purpose:
        Prove foreign-park semantics are byte-identical: a thread OUTSIDE
        the cohort times out with the existing holder-naming error while a
        cohort span is active.
    Contract:
        - RuntimeError naming the load label; the member's presence changes
          nothing for foreigners.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:foreign-park")
    errors = []

    def foreigner() -> None:
        try:
            gate.wait_for_passage(timeout=0.05)
        except RuntimeError as error:
            errors.append(str(error))

    thread = _run_in_thread(foreigner)
    thread.join(3.0)
    assert len(errors) == 1
    assert "checkpoint_load:foreign-park" in errors[0]
    gate.release()
    gate.cleanup()


def test_enroll_refuses_without_active_span() -> None:
    """
    Purpose:
        Prove enrollment outside a span is a pairing bug.
    Contract:
        - RuntimeError on an open gate; nothing becomes enrolled.
    """
    gate = LoadGate()
    with pytest.raises(RuntimeError, match="no active load span"):
        gate.enroll_worker(12345)
    assert gate.describe()["cohort_size"] == 0
    gate.cleanup()


def test_enroll_refuses_from_non_holder_thread() -> None:
    """
    Purpose:
        Prove workers never self-enroll: enrollment from any thread other
        than the holder refuses naming the load.
    Contract:
        - RuntimeError raised inside the non-holder thread.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:holder-only")
    errors = []

    def impostor() -> None:
        try:
            gate.enroll_worker(threading.get_ident())
        except RuntimeError as error:
            errors.append(str(error))

    thread = _run_in_thread(impostor)
    thread.join(3.0)
    assert len(errors) == 1
    assert "holder" in errors[0]
    assert gate.describe()["cohort_size"] == 0
    gate.release()
    gate.cleanup()


def test_enroll_rejects_invalid_thread_idents() -> None:
    """
    Purpose:
        Prove ident validation strictness: bools, non-ints, and
        non-positive ints refuse without touching the cohort.
    Contract:
        - ValueError per invalid candidate; cohort stays empty.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:idents")
    for bad_ident in (True, False, 0, -7, "123", 1.5, None):
        with pytest.raises(ValueError):
            gate.enroll_worker(bad_ident)
        with pytest.raises(ValueError):
            gate.withdraw_worker(bad_ident)
    assert gate.describe()["cohort_size"] == 0
    gate.release()
    gate.cleanup()


def test_withdrawn_worker_parks_at_next_passage_check() -> None:
    """
    Purpose:
        Prove withdrawal takes effect at the next passage check: the same
        thread that passed while enrolled times out after withdrawal.
    Contract:
        - First check passes; post-withdraw check raises at the deadline.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:withdraw")
    outcomes = []
    enrolled = threading.Event()
    withdrawn = threading.Event()
    worker_ident = []

    def worker() -> None:
        worker_ident.append(threading.get_ident())
        enrolled.wait(2.0)
        gate.wait_for_passage(timeout=1.0)
        outcomes.append("passed-enrolled")
        withdrawn.wait(2.0)
        try:
            gate.wait_for_passage(timeout=0.05)
        except RuntimeError:
            outcomes.append("parked-after-withdraw")

    thread = _run_in_thread(worker)
    while not worker_ident:
        time.sleep(0.01)
    gate.enroll_worker(worker_ident[0])
    enrolled.set()
    while "passed-enrolled" not in outcomes:
        time.sleep(0.01)
    gate.withdraw_worker(worker_ident[0])
    withdrawn.set()
    thread.join(3.0)
    assert outcomes == ["passed-enrolled", "parked-after-withdraw"]
    gate.release()
    gate.cleanup()


def test_release_clears_cohort_so_next_span_starts_alone() -> None:
    """
    Purpose:
        Prove no membership survives a span: after release + re-acquire,
        the previously enrolled ident is foreign again.
    Contract:
        - describe() shows an empty cohort on the new span; the stale
          member times out.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:span-one")
    stale_ident = 999_999_001
    gate.enroll_worker(stale_ident)
    assert gate.describe()["cohort_size"] == 1
    gate.release()
    gate.acquire("checkpoint_load:span-two")
    snapshot = gate.describe()
    assert snapshot["cohort_size"] == 0
    assert snapshot["cohort_thread_ids"] == []
    gate.release()
    gate.cleanup()


def test_enroll_and_withdraw_are_idempotent() -> None:
    """
    Purpose:
        Prove set semantics: double enroll holds one membership; double
        withdraw (and withdrawing a non-member) are no-ops.
    Contract:
        - cohort_size reflects set membership exactly.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:idempotent")
    gate.enroll_worker(424242)
    gate.enroll_worker(424242)
    assert gate.describe()["cohort_size"] == 1
    gate.withdraw_worker(424242)
    gate.withdraw_worker(424242)
    gate.withdraw_worker(555555)
    assert gate.describe()["cohort_size"] == 0
    gate.release()
    gate.cleanup()


def test_cleanup_clears_cohort_and_stays_terminally_open() -> None:
    """
    Purpose:
        Prove teardown law: cleanup during a cohort span clears membership,
        wakes parked foreigners, and leaves the gate terminally open.
    Contract:
        - A parked foreign thread exits cleanly on cleanup; late passage
          checks pass immediately; enroll after cleanup refuses.
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:teardown")
    gate.enroll_worker(31337)
    outcomes = []

    def parked_foreigner() -> None:
        gate.wait_for_passage(timeout=5.0)
        outcomes.append("woke-clean")

    thread = _run_in_thread(parked_foreigner)
    time.sleep(0.05)
    gate.cleanup()
    thread.join(3.0)
    assert outcomes == ["woke-clean"]
    gate.wait_for_passage(timeout=0.01)
    with pytest.raises(RuntimeError):
        gate.enroll_worker(31337)


def test_describe_reports_cohort_truthfully() -> None:
    """
    Purpose:
        Prove observability: describe() carries the holder plus a detached
        sorted cohort view.
    Contract:
        - cohort_thread_ids is sorted and detached (mutating the returned
          list never touches gate state).
    """
    gate = LoadGate()
    gate.acquire("checkpoint_load:describe")
    gate.enroll_worker(300)
    gate.enroll_worker(200)
    snapshot = gate.describe()
    assert snapshot["cohort_size"] == 2
    assert snapshot["cohort_thread_ids"] == [200, 300]
    snapshot["cohort_thread_ids"].append(999)
    assert gate.describe()["cohort_size"] == 2
    gate.release()
    gate.cleanup()


def test_acquire_refuses_while_held_from_any_thread():
    """
    Purpose:
        Pin the one-load-at-a-time law: acquire refuses while ANY holder
        exists - including the holder itself (nested acquire is a pairing
        bug) and any other thread.
    Contract:
        Both refusals raise RuntimeError naming the holding label.
    Returns:
        None.
    Raises:
        AssertionError: If a second span can open over a held gate.
    """
    gate = LoadGate()
    try:
        gate.acquire("span-alpha")
        with pytest.raises(RuntimeError, match="span-alpha"):
            gate.acquire("nested")
        errors = []

        def foreign_acquire():
            try:
                gate.acquire("intruder")
            except RuntimeError as error:
                errors.append(str(error))

        thread = threading.Thread(target=foreign_acquire)
        thread.start()
        thread.join()
        assert len(errors) == 1
        assert "span-alpha" in errors[0]
        gate.release()
    finally:
        gate.cleanup()


def test_release_refuses_open_gate_and_foreign_thread():
    """
    Purpose:
        Pin the release pairing law: only the holder thread may release,
        and releasing an open gate is a caller bug.
    Contract:
        Open-gate release raises; a non-holder thread's release raises
        naming the holding load; the holder then releases cleanly.
    Returns:
        None.
    Raises:
        AssertionError: If a foreign or unpaired release succeeds.
    """
    gate = LoadGate()
    try:
        with pytest.raises(RuntimeError, match="open gate"):
            gate.release()
        gate.acquire("span-owner")
        errors = []

        def foreign_release():
            try:
                gate.release()
            except RuntimeError as error:
                errors.append(str(error))

        thread = threading.Thread(target=foreign_release)
        thread.start()
        thread.join()
        assert len(errors) == 1
        assert "span-owner" in errors[0]
        gate.release()
        assert gate.is_held() is False
    finally:
        gate.cleanup()


def test_three_enrolled_members_pass_concurrently():
    """
    Purpose:
        Pin cohort breadth: several enrolled workers pass the held gate
        at once (the parallel pool shape), none serialized behind the
        condition.
    Contract:
        All three member threads return from wait_for_passage within the
        bound while the gate stays held.
    Returns:
        None.
    Raises:
        AssertionError: If any member parks or the span leaks.
    """
    gate = LoadGate()
    try:
        gate.acquire("wide-span")
        started = []
        passed = []
        record_lock = threading.Lock()
        all_started = threading.Barrier(4, timeout=5.0)
        release_members = threading.Event()

        def member():
            with record_lock:
                started.append(threading.get_ident())
            all_started.wait()
            release_members.wait(timeout=5.0)
            gate.wait_for_passage(timeout=2.0)
            with record_lock:
                passed.append(threading.get_ident())

        threads = [threading.Thread(target=member) for _ in range(3)]
        for thread in threads:
            thread.start()
        all_started.wait()
        for ident in list(started):
            gate.enroll_worker(ident)
        release_members.set()
        for thread in threads:
            thread.join()
        assert sorted(passed) == sorted(started)
        assert gate.is_held() is True
        gate.release()
    finally:
        gate.cleanup()


def test_acquire_label_and_held_truth_lifecycle():
    """
    Purpose:
        Pin the span bookkeeping edges: a falsy label refuses with
        ValueError, and is_held() tracks the exact span lifecycle.
    Contract:
        False before acquire, True during, False after release.
    Returns:
        None.
    Raises:
        AssertionError: If span truth or label validation drifts.
    """
    gate = LoadGate()
    try:
        with pytest.raises(ValueError):
            gate.acquire("")
        assert gate.is_held() is False
        gate.acquire("lifecycle")
        assert gate.is_held() is True
        gate.release()
        assert gate.is_held() is False
    finally:
        gate.cleanup()
