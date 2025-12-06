import threading
import pytest

from melder.utilities.synchronization.safeguard import SafeGuard


class _FalseLock:
    def acquire(self, timeout=None):
        return False

    def release(self):
        pass


def test_safeguard_context_orders_and_cleans():
    lock1 = threading.RLock()
    lock2 = threading.RLock()
    guard = SafeGuard(lock2, lock1, one_time_use=True)
    with guard:
        assert True  # locks acquired in order
    # one_time_use triggers cleanup; re-entry should raise
    with pytest.raises(RuntimeError):
        guard.check_cleaned()


def test_safeguard_timeout_releases_partial():
    # lock that fails acquire should trigger release of previous
    good_lock = threading.RLock()
    bad_lock = _FalseLock()
    guard = SafeGuard(good_lock, bad_lock, timeout=0.01, one_time_use=False)
    with pytest.raises(TimeoutError):
        with guard:
            pass
    # good_lock should be released after failure
    assert good_lock.acquire(blocking=False)
    good_lock.release()


def test_safeguard_release_without_acquire():
    guard = SafeGuard()
    with pytest.raises(RuntimeError):
        guard.release()
