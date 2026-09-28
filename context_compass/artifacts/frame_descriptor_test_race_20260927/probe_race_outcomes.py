"""Count how two racing FrameDescriptor cleanups end, over many runs.

Usage from a worktree root: PYTHONPATH=src python <this file> <runs>
Each run starts two threads on a Barrier; each thread records 'returned' or the exception type it raised.
"""

import collections
import os
import sys
import threading
from typing import Counter, List

from melder.nexus.frame_descriptor.frame_descriptor import FrameDescriptor


def one_race() -> str:
    """Run one two-thread cleanup race and return its outcome, e.g. 'returned+AttributeError'."""
    descriptor = FrameDescriptor("ops")
    start = threading.Barrier(2)
    outcomes: List[str] = []

    def run_cleanup() -> None:
        start.wait(timeout=10.0)
        try:
            descriptor.cleanup()
            outcomes.append("returned")
        except BaseException as error:
            outcomes.append(type(error).__name__)

    threads = [threading.Thread(target=run_cleanup, daemon=True) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15.0)
    if any(thread.is_alive() for thread in threads):
        return "stuck"
    return "+".join(sorted(outcomes)) + ("" if descriptor.cleaned else " (NOT cleaned)")


def main() -> int:
    """Tally the outcomes of the requested number of races."""
    assert sys.version_info >= (3, 14), sys.version
    runs = int(sys.argv[1])
    tally: Counter[str] = collections.Counter(one_race() for _ in range(runs))
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} runs={runs} outcomes={dict(tally)}")
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
