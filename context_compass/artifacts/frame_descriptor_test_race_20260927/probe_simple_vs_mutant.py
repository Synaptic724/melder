"""Can the simple-form cleanup test tell a working inner recheck from a missing one? melder_0, 2026-09-27.

Usage from a worktree root: PYTHONPATH=src:. python <this file> <test file> [runs]
Both cleanups below copy FrameDescriptor.cleanup and add one Barrier right after the outer `_cleaned` check, so
both threads always get past it and the second one really reaches the lock - the interleaving the inner recheck
exists for. `real` keeps the inner recheck; `mutant` drops it. For each, the test runs `runs` times; the tally
shows the test outcome and what the second cleanup did inside the descriptor.
"""

import importlib.util
import os
import sys
import threading
from typing import Callable, Dict, List

from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor

TEST_NAME = "test_descriptor_exposes_frame_name_and_cleanup_rechecks_cleaned_inside_lock"


def load(path: str) -> Callable[[], None]:
    """Load the test module from its file path and return the test function."""
    spec = importlib.util.spec_from_file_location("simple_form_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, TEST_NAME)


def make_cleanup(recheck: bool, events: List[str]) -> Callable[[FrameDescriptor], None]:
    """Return FrameDescriptor.cleanup with a two-party gate after the outer check, with or without the recheck."""
    gates: Dict[int, threading.Barrier] = {}
    gates_lock = threading.Lock()

    def cleanup(self: FrameDescriptor) -> None:
        if self._cleaned:
            events.append("returned at the outer check")
            return
        with gates_lock:
            gate = gates.setdefault(id(self), threading.Barrier(2))
        gate.wait(timeout=5.0)
        try:
            with self._lock:
                if recheck and self._cleaned:
                    events.append("returned at the inner recheck")
                    return
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
            events.append("tore down")
        except AttributeError as error:
            events.append(f"AttributeError: {error}")
            raise

    return cleanup


def main() -> int:
    """Run the test against both cleanups and print the tallies."""
    assert sys.version_info >= (3, 14), sys.version
    test = load(sys.argv[1])
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    real_cleanup = FrameDescriptor.cleanup
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} runs={runs}")
    for label, recheck in (("real (inner recheck kept)", True), ("mutant (inner recheck removed)", False)):
        events: List[str] = []
        FrameDescriptor.cleanup = make_cleanup(recheck, events)
        outcomes: Dict[str, int] = {}
        for _ in range(runs):
            try:
                test()
                outcome = "test passed"
            except BaseException as error:
                outcome = f"test failed: {type(error).__name__}"
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        tally: Dict[str, int] = {}
        for event in events:
            tally[event] = tally.get(event, 0) + 1
        print(f"{label}: {outcomes}; cleanup calls: {tally}")
    FrameDescriptor.cleanup = real_cleanup
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
