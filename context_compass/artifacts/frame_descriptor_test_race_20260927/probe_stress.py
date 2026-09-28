"""Stress one test function by calling it in a loop, counting failures, without pytest.

Usage from a worktree root: PYTHONPATH=src:. python <this file> <test file> <test name> <max runs> <seconds>
Failed runs of the original test leave a thread blocked for good, so the process ends with os._exit.
"""

import importlib.util
import os
import sys
import threading
import time
from typing import Dict


def main() -> int:
    """Run the named test until the run or time budget is spent; print runs, failures and thread errors."""
    assert sys.version_info >= (3, 14), sys.version
    path, name, max_runs, seconds = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
    spec = importlib.util.spec_from_file_location("stressed_test_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    test = getattr(module, name)
    counts: Dict[str, int] = {"thread_errors": 0}
    threading.excepthook = lambda args: counts.__setitem__("thread_errors", counts["thread_errors"] + 1)
    runs = 0
    failures: Dict[str, int] = {}
    started = time.monotonic()
    while runs < max_runs and time.monotonic() - started < seconds:
        try:
            test()
        except BaseException as error:
            key = type(error).__name__
            failures[key] = failures.get(key, 0) + 1
        runs += 1
    elapsed = time.monotonic() - started
    print(
        f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} test={name} runs={runs} "
        f"failures={failures} thread_errors={counts['thread_errors']} "
        f"stuck_threads={threading.active_count() - 1} seconds={elapsed:.1f}"
    )
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    main()
