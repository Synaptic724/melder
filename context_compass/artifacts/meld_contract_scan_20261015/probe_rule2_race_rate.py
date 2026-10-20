"""Measure the meld-vs-notch race (RISK of 2026-10-16T14:08:56Z) on one tree: N runs of the integration race (melder_1).

Each run: a fresh Aether, the lender/borrower world of the integration file (`_lend`), four threads melding the
borrower's SpellContract consumer while the lender notches its provider 20 times (A, B, A, ...). Per run it counts the
melds that returned each version, the refusals (SpellbookValidationError) and any other exception that ended a
thread, and the version the first meld after the race returns (the last notch selects A).

usage: python -X gil=0|1 <this script> <tree root> <runs>
"""
import collections
import sys
import threading
import time

TREE = sys.argv[1]
RUNS = int(sys.argv[2])
sys.path[:0] = [f"{TREE}/src", TREE]

from tests.integration.melder.conduit import test_conduit_integration_notch_revalidation as t  # noqa: E402
from melder.aether.aether import Aether  # noqa: E402
from melder.aether.spellbook.spellbook import Spellbook  # noqa: E402
from melder.aether.conduit.conduit import Conduit  # noqa: E402
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError  # noqa: E402


def fresh() -> None:
    """Give the run a fresh Aether, as the integration file's autouse fixture does."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def one_run() -> tuple:
    """Run the race once; return (counts, unexpected, final, seconds)."""
    fresh()
    started = time.perf_counter()
    world = t._lend("race", t.ImplA)
    stop = threading.Event()
    counts: collections.Counter = collections.Counter()
    unexpected: list = []
    guard = threading.Lock()

    def loop() -> None:
        while not stop.is_set():
            try:
                version = world.meld_ping()
                with guard:
                    counts[version] += 1
            except SpellbookValidationError:
                with guard:
                    counts["refused"] += 1
            except BaseException as exc:
                with guard:
                    unexpected.append(f"{type(exc).__name__}: {str(exc)[:90]}")
                return

    threads = [threading.Thread(target=loop) for _ in range(4)]
    try:
        assert world.meld_ping() == "A"
        for thread in threads:
            thread.start()
        b_id = world.notch_to(t.ImplB)
        versions = [b_id, world.provider_id] * 10
        for version_id in versions[1:]:
            world.notch_back(version_id)
    finally:
        stop.set()
        for thread in threads:
            thread.join(timeout=60)
    try:
        final = world.meld_ping()
    except BaseException as exc:
        final = type(exc).__name__
    world.cleanup()
    return counts, unexpected, final, time.perf_counter() - started


totals: collections.Counter = collections.Counter()
bad_runs = 0
finals: collections.Counter = collections.Counter()
kinds: collections.Counter = collections.Counter()
print(f"tree={TREE} runs={RUNS} gil_enabled={sys._is_gil_enabled()}")
for run in range(1, RUNS + 1):
    counts, unexpected, final, seconds = one_run()
    totals.update(counts)
    finals[final] += 1
    if unexpected:
        bad_runs += 1
        kinds.update(unexpected)
    print(f"run {run:2d}: {dict(sorted(counts.items()))} unexpected={len(unexpected)} final={final} "
          f"{seconds:.2f}s")
print(f"runs with an unexpected exception: {bad_runs} of {RUNS}")
for kind, count in kinds.most_common():
    print(f"  {count} x {kind}")
print(f"melds: {dict(sorted(totals.items()))}")
print(f"first meld after the race: {dict(finals)}")
