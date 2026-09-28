"""Apply the hardened cleanup-recheck test to one tree (worktree or device). melder_0, 2026-09-27.

Usage: python apply_hardened_test.py <repository root>
Edits only tests/unit/melder/aether/test_aetheric_frame_descriptor.py; keeps its BOM and CRLF line endings.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import eol_lines

assert sys.version_info >= (3, 14), "run with the 3.14 venv"

ROOT = pathlib.Path(sys.argv[1])
TARGET = str(ROOT / "tests/unit/melder/aether/test_aetheric_frame_descriptor.py")

IMPORT_TYPES_OLD = "﻿from types import SimpleNamespace\n"
IMPORT_TYPES_NEW = "﻿from types import SimpleNamespace, TracebackType\n"
IMPORT_TYPING_OLD = "from typing import Optional, Tuple\n"
IMPORT_TYPING_NEW = "from typing import List, Optional, Self, Tuple, Type\n"

HELPER_OLD = '''def test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _CoordinatedLock:
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
'''

HELPER_NEW = '''def test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify the frame name accessor, and that a cleanup that loses the race rechecks `_cleaned` under the lock.

    Contract:
        - Two cleanups start together, and both pass cleanup's unlocked `_cleaned` check.
        - The lock stand-in holds the first cleanup inside the lock until the second one is known to be
          waiting on it, then marks the descriptor cleaned, as a finished teardown would.
        - The second cleanup must return at its recheck inside the lock instead of tearing down again; a second
          teardown fails on the fields the first one deleted, and the test records that failure.

    Why the coordination is shaped this way:
        The first version chose the first entrant by reading an event before taking the lock, and asserted on a
        1 s wait inside `__enter__`. When both threads read the event before either set it (free-threaded
        Windows CI, 2026-09-27), the waiter never signalled, the assert fired while its thread held the lock,
        and the waiter blocked for good, which also held up interpreter shutdown. The first entrant is now the
        thread whose non-blocking acquire succeeds, a failing first entrant releases the lock before raising,
        and the threads are daemons with liveness and exception checks, so a regression fails here instead of
        hanging the run or passing with only a warning.

    Returns:
        None.
    """
    class _CoordinatedLock:
        """
        Descriptor lock stand-in that parks the first cleanup until the second one waits on the lock.

        Contract:
            - The first entrant is the thread whose non-blocking acquire succeeds. Any other entrant sets
              `_waiter_blocked` and then blocks on the lock, so it has already passed cleanup's unlocked
              check when the descriptor is marked cleaned.
            - The first entrant marks the descriptor cleaned only after the waiter signalled.
            - A first entrant that fails releases the lock before raising, so no waiter is stranded on it.
        """

        def __init__(self, descriptor: FrameDescriptor) -> None:
            """Hold the descriptor to mark, the waiter signal and the real re-entrant lock."""
            self._descriptor = descriptor
            self._waiter_blocked = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self) -> Self:
            """Take the lock as the first entrant or as the waiter, as the class contract describes."""
            if self._lock.acquire(blocking=False):
                try:
                    assert self._waiter_blocked.wait(timeout=10.0)
                    self._descriptor._cleaned = True
                except BaseException:
                    self._lock.release()
                    raise
                return self
            self._waiter_blocked.set()
            self._lock.acquire()
            return self

        def __exit__(
                self,
                exc_type: Optional[Type[BaseException]],
                exc: Optional[BaseException],
                tb: Optional[TracebackType],
        ) -> None:
            """Release the lock taken in `__enter__`."""
            self._lock.release()
'''

THREADS_OLD = '''    descriptor = FrameDescriptor("ops")
    descriptor._lock = _CoordinatedLock(descriptor)

    first = threading.Thread(target=descriptor.cleanup)
    second = threading.Thread(target=descriptor.cleanup)
    first.start()
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert descriptor.cleaned is True
'''

THREADS_NEW = '''    descriptor = FrameDescriptor("ops")
    descriptor._lock = _CoordinatedLock(descriptor)
    thread_errors: List[BaseException] = []

    def run_cleanup() -> None:
        """Run one cleanup and keep any exception it raises for the assertions below."""
        try:
            descriptor.cleanup()
        except BaseException as error:
            thread_errors.append(error)

    first = threading.Thread(target=run_cleanup, daemon=True)
    second = threading.Thread(target=run_cleanup, daemon=True)
    first.start()
    second.start()
    first.join(timeout=15.0)
    second.join(timeout=15.0)

    assert not first.is_alive() and not second.is_alive()
    assert thread_errors == []
    assert descriptor.cleaned is True
'''


def main() -> int:
    """Apply the four replacements and report each result."""
    for old, new in (
        (IMPORT_TYPES_OLD, IMPORT_TYPES_NEW),
        (IMPORT_TYPING_OLD, IMPORT_TYPING_NEW),
        (HELPER_OLD, HELPER_NEW),
        (THREADS_OLD, THREADS_NEW),
    ):
        print(eol_lines.replace_lines(TARGET, old, new))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
