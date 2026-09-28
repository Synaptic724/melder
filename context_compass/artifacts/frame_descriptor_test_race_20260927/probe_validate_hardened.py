"""Adversarial and mutation checks for the hardened cleanup-recheck test.

Usage from a worktree root: PYTHONPATH=src:. python <this file> <hardened test file> <original test file>
Cases:
  late_waiter   - the second cleanup starts 0.5 s after the first (the first must wait, not fail).
  jitter        - 300 runs with a random 0-20 ms delay before each cleanup (arrival order varies).
  mutant        - FrameDescriptor.cleanup without its inner `_cleaned` recheck: the hardened test must fail
                  quickly; the original test is run against it too, to show what it catches.
"""

import importlib.util
import os
import random
import sys
import threading
import time
from typing import Callable, Dict, List

from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor

TEST_NAME = "test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock"


def load(path: str, name: str) -> Callable[[], None]:
    """Load one test module from a file path and return the test function."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, TEST_NAME)


def run(test: Callable[[], None]) -> str:
    """Run a test once and describe the outcome with its duration."""
    started = time.monotonic()
    try:
        test()
        outcome = "passed"
    except BaseException as error:
        outcome = f"{type(error).__name__}: {str(error).splitlines()[0][:90] if str(error) else ''}"
    return f"{outcome} in {time.monotonic() - started:.2f}s"


def mutant_cleanup(self: FrameDescriptor) -> None:
    """FrameDescriptor.cleanup with the inner recheck removed; everything else as in the source."""
    if self._cleaned:
        return
    with self._lock:
        self._cleaned = True
        if self._frame_overview is not None:
            self._frame_overview.cleanup()
        for conduit_record in self._conduit_records_by_id.values():
            conduit_record.cleanup()
        for spell_record in self._spell_records_by_key.values():
            spell_record.cleanup()
        self._conduit_records_by_id.clear()
        self._spell_records_by_key.clear()
        self._spell_keys_by_conduit_id.clear()
        self._spell_keys_by_spellbook_id.clear()
        del self._frame_handle
        del self._frame_configuration
        del self._frame_overview
        del self._conduit_records_by_id
        del self._spell_records_by_key
        del self._spell_keys_by_conduit_id
        del self._spell_keys_by_spellbook_id
        del self._frame_name
    del self._lock


def main() -> int:
    """Run the three cases and print their outcomes."""
    assert sys.version_info >= (3, 14), sys.version
    hardened = load(sys.argv[1], "hardened_module")
    original = load(sys.argv[2], "original_module")
    thread_errors: List[str] = []
    threading.excepthook = lambda args: thread_errors.append(type(args.exc_value).__name__)
    real_cleanup = FrameDescriptor.cleanup
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()}")

    calls: Dict[str, int] = {"n": 0}
    lock = threading.Lock()

    def late_second(self: FrameDescriptor) -> None:
        with lock:
            calls["n"] += 1
            call = calls["n"]
        if call % 2 == 0:
            time.sleep(0.5)
        real_cleanup(self)

    FrameDescriptor.cleanup = late_second
    print("late_waiter:", run(hardened))

    def jittered(self: FrameDescriptor) -> None:
        time.sleep(random.random() * 0.02)
        real_cleanup(self)

    FrameDescriptor.cleanup = jittered
    outcomes: Dict[str, int] = {}
    for _ in range(300):
        outcome = run(hardened).split(" in ")[0]
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    print("jitter x300:", outcomes)

    FrameDescriptor.cleanup = mutant_cleanup
    print("mutant, hardened test:", run(hardened))
    before = len(thread_errors)
    print("mutant, original test:", run(original), f"(thread errors raised meanwhile: {thread_errors[before:]})")
    FrameDescriptor.cleanup = real_cleanup
    print("real cleanup restored, hardened test:", run(hardened))
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
