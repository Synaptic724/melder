"""Forced reproduction of the Windows failure of
test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock.

`_CoordinatedLock` below is the test's helper copied verbatim. Only its inner RLock is replaced, by a gate that
holds the first acquirer inside acquire() until the second thread has also called acquire(). That is the
interleaving the free-threaded Windows runner produced: both threads read `_entered_first` before the first one
set it. Run from a worktree root: PYTHONPATH=src:. python <this file>
"""

import os
import sys
import threading
from typing import List

from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor


class _CoordinatedLock:
    """Verbatim copy of the helper in the failing test (0.2.82)."""

    def __init__(self, descriptor: FrameDescriptor) -> None:
        self._descriptor = descriptor
        self._entered_first = threading.Event()
        self._second_attempted = threading.Event()
        self._lock = threading.RLock()

    def __enter__(self):
        if self._entered_first.is_set():
            self._second_attempted.set()
        self._lock.acquire()
        if not self._entered_first.is_set():
            self._entered_first.set()
            assert self._second_attempted.wait(timeout=1.0)
            self._descriptor._cleaned = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self._lock.release()


class _GateRLock:
    """RLock stand-in that parks the first acquirer until a second acquire() call arrives."""

    def __init__(self) -> None:
        self._rlock = threading.RLock()
        self._meta = threading.Lock()
        self._calls = 0
        self.second_called_acquire = threading.Event()

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        with self._meta:
            self._calls += 1
            call = self._calls
        if call == 1:
            acquired = self._rlock.acquire()
            self.second_called_acquire.wait(timeout=5.0)
            return acquired
        self.second_called_acquire.set()
        return self._rlock.acquire()

    def release(self) -> None:
        self._rlock.release()


def main() -> int:
    """Drive two cleanups through the original helper in the forced order and report what happened."""
    assert sys.version_info >= (3, 14), sys.version
    errors: List[str] = []
    threading.excepthook = lambda args: errors.append(
        f"{args.thread.name}: {type(args.exc_value).__name__}: {args.exc_value!r}"
    )
    descriptor = FrameDescriptor("ops")
    coordinated = _CoordinatedLock(descriptor)
    coordinated._lock = _GateRLock()
    descriptor._lock = coordinated
    first = threading.Thread(target=descriptor.cleanup, name="first", daemon=True)
    second = threading.Thread(target=descriptor.cleanup, name="second", daemon=True)
    first.start()
    second.start()
    first.join(timeout=3.0)
    second.join(timeout=3.0)
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()}")
    print("first thread alive:", first.is_alive())
    print("second thread alive (blocked on a lock whose owner died):", second.is_alive())
    print("descriptor.cleaned:", descriptor.cleaned)
    print("thread errors:", errors)
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
