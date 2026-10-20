"""Run a list of pytest ids under a wall-clock budget and resume where the last call stopped.

A device_bash call lasts at most 180 s and kills its children when it returns, so a long tree is run as
several calls of this script with the same arguments: each call runs every id not yet recorded as finished
in the earlier part logs (`<prefix>_partNN.txt`, `pytest -v` output), inside one pytest process, and stops at
the budget. A test interrupted by the budget is run again by the next call.

Usage: python resumable_pytest_shard.py <gil 0|1> <ids file> <log prefix> [budget seconds]
"""
import pathlib
import re
import subprocess
import sys

OUTCOME = re.compile(r"^(tests/\S.*?) (PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b")


def finished_ids(prefix: pathlib.Path) -> dict:
    """Return id -> outcome for every test a previous part log recorded as finished."""
    done = {}
    for log in sorted(prefix.parent.glob(prefix.name + "_part*.txt")):
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            match = OUTCOME.match(line)
            if match:
                done[match.group(1)] = match.group(2)
    return done


def main() -> int:
    gil, ids_file, prefix_text = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
    budget = float(sys.argv[4]) if len(sys.argv) > 4 else 160.0
    prefix = pathlib.Path(prefix_text)
    wanted = [line.strip() for line in ids_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    done = finished_ids(prefix)
    remaining = [test_id for test_id in wanted if test_id not in done]
    if not remaining:
        outcomes = {}
        for outcome in done.values():
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        print(f"COMPLETE: {len(wanted)} ids; outcomes {outcomes}")
        return 0
    part = len(list(prefix.parent.glob(prefix.name + "_part*.txt")))
    log_path = prefix.parent / f"{prefix.name}_part{part:02d}.txt"
    command = [sys.executable, "-X", f"gil={gil}", "-m", "pytest", "-v", "-p", "no:cacheprovider", *remaining]
    with log_path.open("w", encoding="utf-8") as log:
        try:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=budget)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = None
    now_done = finished_ids(prefix)
    progressed = len(now_done) - len(done)
    left = len([test_id for test_id in wanted if test_id not in now_done])
    print(f"part {part:02d}: exit {code}; finished {progressed} this call; {left} of {len(wanted)} left; log {log_path.name}")
    if progressed == 0:
        print("NO PROGRESS: the first remaining test outlasts the budget or failed to start; read the log.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
