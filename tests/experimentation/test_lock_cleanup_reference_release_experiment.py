import threading


def _other_thread_can_acquire(lock: threading.RLock) -> bool:
    """
    Return whether another thread can acquire the provided lock.

    Args:
        lock:
            Lock object to probe from a different thread.

    Returns:
        bool:
            True when the worker thread successfully acquires and releases the
            lock within the timeout window.
    """
    result = {"acquired": False}

    def worker() -> None:
        acquired = lock.acquire(timeout=0.5)
        result["acquired"] = acquired
        if acquired:
            lock.release()

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()
    return result["acquired"]


class _InlineNoneCleanup:
    """
    Probe object that nulls its lock reference inside the `with` block.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cleaned = False

    def cleanup(self) -> None:
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._lock = None


class _PostBlockNoneCleanup:
    """
    Probe object that nulls its lock reference after the `with` block.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cleaned = False

    def cleanup(self) -> None:
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
        self._lock = None


class _KeepLockReference:
    """
    Probe object that keeps its lock reference after cleanup.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._cleaned = False

    def cleanup(self) -> None:
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True


def test_lock_is_released_even_when_reference_is_noned_inside_cleanup() -> None:
    """
    Prove that nulling a lock reference during cleanup does not strand the lock.

    Contract:
    - Python's `with self._lock:` keeps the entered lock object alive for the
      duration of the block.
    - Nulling the attribute inside or after the block must not prevent another
      thread from acquiring the original lock object after cleanup completes.
    """
    cases = [
        _InlineNoneCleanup,
        _PostBlockNoneCleanup,
        _KeepLockReference,
    ]

    for case in cases:
        obj = case()
        original_lock = obj._lock
        obj.cleanup()
        assert _other_thread_can_acquire(original_lock), (
            f"{case.__name__} left the original lock unreleased after cleanup."
        )
