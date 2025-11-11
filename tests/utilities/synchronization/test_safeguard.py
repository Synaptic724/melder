import threading
import time
import unittest

from melder.utilities.synchronization.safeguard import SafeGuard


# Import your SafeGuard
# 
# For this test file, I'll assume SafeGuard is in scope.

# ---------- Test helpers ----------

class CountingLock:
    """
    Minimal lock-like object for deterministic testing.
    - Supports acquire(timeout=...) and release()
    - Can be configured to fail on acquire when a timeout is provided.
    """
    __slots__ = ("name", "acquire_count", "release_count", "_held", "fail_on_timeout_acquire")

    def __init__(self, name: str, fail_on_timeout_acquire: bool = False):
        self.name = name
        self.acquire_count = 0
        self.release_count = 0
        self._held = False
        self.fail_on_timeout_acquire = fail_on_timeout_acquire

    def acquire(self, timeout=None):
        # If configured to fail and a timeout is used, simulate timeout failure
        if self.fail_on_timeout_acquire and timeout is not None:
            return False
        self.acquire_count += 1
        self._held = True
        return True

    def release(self):
        if self._held:
            self.release_count += 1
            self._held = False
        else:
            # Mirror threading semantics: releasing an unlocked lock would raise.
            # We keep tolerant for the test; no-op.
            pass


class OrderRecordingLock(CountingLock):
    """
    Lock that records acquisition and release order into shared lists.
    """
    __slots__ = ("acq_log", "rel_log")

    def __init__(self, name: str, acq_log, rel_log):
        super().__init__(name)
        self.acq_log = acq_log
        self.rel_log = rel_log

    def acquire(self, timeout=None):
        ok = super().acquire(timeout=timeout)
        if ok:
            self.acq_log.append(self.name)
        return ok

    def release(self):
        super().release()
        self.rel_log.append(self.name)


# ---------- The actual tests ----------

class TestSafeGuard(unittest.TestCase):

    # 1
    def test_acquires_in_id_order(self):
        acq, rel = [], []
        l1 = OrderRecordingLock("l1", acq, rel)
        l2 = OrderRecordingLock("l2", acq, rel)
        # Expected order by id()
        expected = [x.name for x in sorted([l1, l2], key=id)]
          # adjust import
        with SafeGuard(l1, l2):
            pass
        self.assertEqual(acq, expected)
        self.assertEqual(rel, list(reversed(expected)))

    # 2
    def test_releases_in_reverse_order(self):
        acq, rel = [], []
        l1 = OrderRecordingLock("a", acq, rel)
        l2 = OrderRecordingLock("b", acq, rel)
        
        with SafeGuard(l1, l2):
            pass
        self.assertEqual(rel, list(reversed(acq)))

    # 3
    def test_deduplicates_same_lock(self):
        l = CountingLock("same")
        
        with SafeGuard(l, l, l):
            pass
        self.assertEqual(l.acquire_count, 1)
        self.assertEqual(l.release_count, 1)

    # 4
    def test_ignores_none_locks(self):
        l = CountingLock("ok")
        
        with SafeGuard(None, l, None):
            pass
        self.assertEqual(l.acquire_count, 1)
        self.assertEqual(l.release_count, 1)

    # 5
    def test_timeout_raises_and_releases_prior(self):
        l_ok = CountingLock("ok")
        l_fail = CountingLock("fail", fail_on_timeout_acquire=True)
        
        with self.assertRaises(TimeoutError):
            with SafeGuard(l_ok, l_fail, timeout=0.01):
                pass
        # l_ok should have been released after failure to acquire l_fail
        self.assertEqual(l_ok.acquire_count, 1)
        self.assertEqual(l_ok.release_count, 1)
        self.assertEqual(l_fail.acquire_count, 0)  # failed before acquiring

    # 6
    def test_exception_inside_context_releases(self):
        l1 = CountingLock("l1")
        l2 = CountingLock("l2")
        
        with self.assertRaises(ValueError):
            with SafeGuard(l1, l2):
                raise ValueError("boom")
        self.assertEqual(l1.release_count, 1)
        self.assertEqual(l2.release_count, 1)

    # 7
    def test_one_time_use_true_blocks_reuse(self):
        l = CountingLock("l")
        
        g = SafeGuard(l, one_time_use=True)
        with g:
            pass
        # Reuse should raise because __exit__ cleaned it
        with self.assertRaises(RuntimeError):
            with g:
                pass

    # 8
    def test_one_time_use_false_allows_reuse(self):
        l = CountingLock("l")
        
        g = SafeGuard(l, one_time_use=False)
        for _ in range(3):
            with g:
                pass
        # Three acquires & releases
        self.assertEqual(l.acquire_count, 3)
        self.assertEqual(l.release_count, 3)

    # 9
    def test_cleanup_idempotent(self):
        l = CountingLock("l")
        
        g = SafeGuard(l)
        g.cleanup()
        # second cleanup should be no-op
        g.cleanup()

    # 10
    def test_no_locks_is_noop(self):
        
        with SafeGuard():
            pass  # nothing to do

    # 11
    def test_accepts_threading_lock_and_rlock(self):
        t_lock = threading.Lock()
        r_lock = threading.RLock()
        
        with SafeGuard(t_lock, r_lock):
            pass  # should not raise

    # 12
    def test_release_count_matches_acquire_count(self):
        l1 = CountingLock("a")
        l2 = CountingLock("b")
        
        with SafeGuard(l1, l2):
            pass
        self.assertEqual(l1.acquire_count, l1.release_count)
        self.assertEqual(l2.acquire_count, l2.release_count)

    # 13
    def test_order_is_deterministic_across_runs(self):
        acq1, rel1 = [], []
        l1 = OrderRecordingLock("x", acq1, rel1)
        l2 = OrderRecordingLock("y", acq1, rel1)

        with SafeGuard(l1, l2): pass
        expected1 = [x.name for x in sorted([l1, l2], key=id)]
        self.assertEqual(acq1, expected1)
        self.assertEqual(rel1, list(reversed(expected1)))

        acq2, rel2 = [], []
        l3 = OrderRecordingLock("w", acq2, rel2)
        l4 = OrderRecordingLock("z", acq2, rel2)
        with SafeGuard(l3, l4): pass
        expected2 = [x.name for x in sorted([l3, l4], key=id)]
        self.assertEqual(acq2, expected2)
        self.assertEqual(rel2, list(reversed(expected2)))

    # 14
    def test_timeout_path_success_when_all_acquire(self):
        l1 = CountingLock("a")
        l2 = CountingLock("b")
        
        with SafeGuard(l1, l2, timeout=0.01):
            pass
        self.assertEqual(l1.acquire_count, 1)
        self.assertEqual(l2.acquire_count, 1)

    # 15
    def test_does_not_swallow_exceptions(self):
        l = CountingLock("a")
        
        with self.assertRaises(ZeroDivisionError):
            with SafeGuard(l):
                _ = 1 / 0

    # 16
    def test_slots_prevent_arbitrary_attributes(self):
        l = CountingLock("a")
        
        g = SafeGuard(l)
        with self.assertRaises(AttributeError):
            setattr(g, "random_attr", 123)

    # 17
    def test_cleanup_nulls_fields(self):
        l = CountingLock("a")
        
        g = SafeGuard(l)
        g.cleanup()
        self.assertTrue(g._cleaned)
        self.assertIsNone(g._locks)
        self.assertIsNone(g._acquired)
        self.assertIsNone(g._timeout)

    # 18
    def test_concurrent_reverse_order_no_deadlock(self):
        # Real locks; without ordering this pattern could deadlock
        lock_a = threading.RLock()
        lock_b = threading.RLock()
        

        done = []
        def worker_ab():
            for _ in range(50):
                with SafeGuard(lock_a, lock_b):
                    pass
            done.append("ab")

        def worker_ba():
            for _ in range(50):
                with SafeGuard(lock_b, lock_a):
                    pass
            done.append("ba")

        t1 = threading.Thread(target=worker_ab)
        t2 = threading.Thread(target=worker_ba)
        t1.start(); t2.start()
        t1.join(timeout=5); t2.join(timeout=5)
        self.assertFalse(t1.is_alive())
        self.assertFalse(t2.is_alive())
        self.assertCountEqual(done, ["ab", "ba"])

    # 19
    def test_partial_acquire_then_body_exception_releases_all(self):
        l1 = CountingLock("a")
        l2 = CountingLock("b")
        
        try:
            with SafeGuard(l1, l2):
                raise RuntimeError("fail mid-body")
        except RuntimeError:
            pass
        self.assertEqual(l1.release_count, 1)
        self.assertEqual(l2.release_count, 1)

    # 20
    def test_reuse_with_different_timeouts_when_one_time_use_false(self):
        l1 = CountingLock("a")
        l2 = CountingLock("b")
        
        g = SafeGuard(l1, l2, one_time_use=False, timeout=None)
        with g: pass
        # change timeout on object (if exposed); otherwise just call again and ensure works
        with g: pass
        self.assertEqual(l1.acquire_count, 2)
        self.assertEqual(l1.release_count, 2)
        self.assertEqual(l2.acquire_count, 2)
        self.assertEqual(l2.release_count, 2)


if __name__ == "__main__":
    unittest.main()
