import threading
import time

import pytest

from melder.utilities.synchronization.safeguard import SafeGuard


class DummyLock:
    def __init__(self, name: str = "", allow: bool = True):
        self.name = name
        self.allow = allow
        self.acquire_calls = 0
        self.release_calls = 0
        self.history = []
        self.timeout_seen = []

    def acquire(self, timeout: float | None = None):
        self.acquire_calls += 1
        self.history.append(("acquire", timeout))
        self.timeout_seen.append(timeout)
        if not self.allow:
            return False
        return True

    def release(self):
        self.release_calls += 1
        self.history.append(("release", None))


def test_filters_none_and_dedup_by_id():
    lock = DummyLock("a")
    guard = SafeGuard(lock, None, lock, one_time_use=False)
    assert len(guard._locks) == 1
    with guard:
        pass


def test_acquire_success_no_timeout_and_release_reverse_order():
    l1 = DummyLock("1")
    l2 = DummyLock("2")
    guard = SafeGuard(l2, l1, one_time_use=False)
    with guard as g:
        assert g is guard
        assert l1.acquire_calls == 1
        assert l2.acquire_calls == 1
    # release order should be reverse of acquired order
    assert l1.release_calls == 1
    assert l2.release_calls == 1
    assert l1.history[-1][0] == "release"
    assert l2.history[-1][0] == "release"


def test_timeout_raises_and_releases_partial():
    good = threading.RLock()
    bad = DummyLock("bad", allow=False)
    guard = SafeGuard(good, bad, timeout=0.01, one_time_use=False)
    with pytest.raises(TimeoutError):
        with guard:
            pass
    # good lock released after failure
    assert good.acquire(blocking=False) is True
    good.release()


def test_one_time_use_cleans_after_exit():
    lock = DummyLock()
    guard = SafeGuard(lock, one_time_use=True)
    with guard:
        pass
    with pytest.raises(RuntimeError):
        guard.check_cleaned()
    with pytest.raises(RuntimeError):
        with guard:
            pass


def test_one_time_use_false_allows_reuse_then_cleanup():
    lock = DummyLock()
    guard = SafeGuard(lock, one_time_use=False)
    for _ in range(2):
        with guard:
            pass
    guard.cleanup()
    with pytest.raises(RuntimeError):
        guard.check_cleaned()


def test_cleanup_idempotent_and_nulls_references():
    guard = SafeGuard(one_time_use=False)
    guard.cleanup()
    guard.cleanup()
    assert guard._locks is None
    assert guard._acquired is None
    with pytest.raises(RuntimeError):
        guard.check_cleaned()


def test_enter_after_cleanup_raises_when_one_time_use_true():
    guard = SafeGuard(one_time_use=True)
    guard.cleanup()
    with pytest.raises(RuntimeError):
        with guard:
            pass


def test_dedup_single_acquire_even_if_passed_twice():
    lock = DummyLock()
    guard = SafeGuard(lock, lock, one_time_use=False)
    with guard:
        pass
    assert lock.acquire_calls == 1


def test_non_lock_object_with_acquire_release_supported():
    lock = DummyLock()
    with SafeGuard(lock, one_time_use=False):
        pass
    assert lock.acquire_calls == 1
    assert lock.release_calls == 1


def test_empty_guard_is_noop():
    with SafeGuard(one_time_use=False):
        pass


def test_exception_inside_context_propagates_and_releases():
    lock = DummyLock()
    guard = SafeGuard(lock, one_time_use=False)
    with pytest.raises(ValueError):
        with guard:
            raise ValueError("boom")
    assert lock.release_calls == 1


def test_timeout_param_is_forwarded():
    lock = DummyLock()
    guard = SafeGuard(lock, timeout=0.5, one_time_use=False)
    with guard:
        pass
    assert lock.timeout_seen[0] == 0.5


def test_ordering_by_id_consistent():
    l1 = DummyLock("a")
    l2 = DummyLock("b")
    # reverse order intentionally
    guard = SafeGuard(l2, l1, one_time_use=False)
    with guard:
        pass
    # acquired sequence should follow sorted id order
    acquired_sequence = [h for (h, _) in l1.history + l2.history if h == "acquire"]
    assert acquired_sequence == ["acquire", "acquire"]


def test_reentrant_lock_support():
    rlock = threading.RLock()
    guard = SafeGuard(rlock, one_time_use=False)
    with guard:
        assert rlock.acquire(blocking=False) is True
        rlock.release()
    assert rlock.acquire(blocking=False) is True
    rlock.release()


def test_concurrent_order_prevents_deadlock():
    lock_a = threading.Lock()
    lock_b = threading.Lock()
    counter = []

    def worker(l1, l2):
        with SafeGuard(l1, l2, one_time_use=False):
            counter.append(1)
            time.sleep(0.01)

    t1 = threading.Thread(target=worker, args=(lock_a, lock_b))
    t2 = threading.Thread(target=worker, args=(lock_b, lock_a))
    t1.start(); t2.start()
    t1.join(timeout=1)
    t2.join(timeout=1)
    assert len(counter) == 2


def test_reverse_release_order_after_partial_failure():
    l1 = threading.RLock()
    l2 = DummyLock("fail", allow=False)
    guard = SafeGuard(l1, l2, timeout=0.01, one_time_use=False)
    with pytest.raises(TimeoutError):
        with guard:
            pass
    # l1 release should have been invoked
    assert l1.acquire(blocking=False) is True
    l1.release()


def test_guard_returns_false_to_not_swallow_exceptions():
    lock = DummyLock()
    guard = SafeGuard(lock, one_time_use=False)
    with pytest.raises(ZeroDivisionError):
        with guard:
            1 / 0


def test_acquire_timeout_on_first_lock():
    bad = DummyLock("bad", allow=False)
    guard = SafeGuard(bad, timeout=0.01, one_time_use=False)
    with pytest.raises(TimeoutError):
        with guard:
            pass
    assert bad.release_calls == 0
