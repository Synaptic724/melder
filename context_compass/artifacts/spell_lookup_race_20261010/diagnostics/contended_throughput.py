"""
Contended throughput around Spellbook.find_spell_by_id (melder_1, 2026-10-10). Measurement, not a test.

Ticket: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md

The stress script's lookup counts are not a throughput measure: its readers run until the writers finish, so the
counts move with however the scheduler splits the CPU between them. This script fixes the window instead: on one
dynamic root, R reader threads call Conduit.get_spell_by_id on a stable spell and W writer threads bind and remove
their own spells, all released by one Barrier and stopped together when the main thread's window ends. It prints
reader lookups per second, writer bind+remove pairs per second, the reader failures seen in the window and the
number of garbage collections that started during it.

Usage (PYTHONPATH=src:. inside an export): python -X gil=0 contended_throughput.py --seconds 3 --label head
"""

import argparse
import gc
import sys
import threading
import time
from typing import List

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration


class Searched:
    """The spell the readers look up."""


class Churn:
    """Bound and removed by the writers."""


def main() -> int:
    """Run one fixed window and print the rates."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--seconds", type=float, default=3.0)
    parser.add_argument("--readers", type=int, default=2)
    parser.add_argument("--writers", type=int, default=2)
    parser.add_argument("--label", default="")
    args = parser.parse_args()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "dynamic")
    configuration.load_default_dictionary()
    book = Spellbook(configuration=configuration)
    searched_id = book.bind(spell=Searched, existence=Existence.many, permissions="create")
    conduit = book.conjure(name="root", dynamic=True)
    searched = book.find_spell_by_id(searched_id)
    collections: List[int] = [0]

    def count_collection(phase: str, info: dict) -> None:
        if phase == "start":
            collections[0] += 1

    stop = threading.Event()
    barrier = threading.Barrier(args.readers + args.writers + 1)
    lookups: List[int] = [0] * args.readers
    failures: List[int] = [0] * args.readers
    pairs: List[int] = [0] * args.writers

    def reader(slot: int) -> None:
        barrier.wait()
        count = bad = 0
        while not stop.is_set():
            count += 1
            try:
                if conduit.get_spell_by_id(searched_id) is not searched:
                    bad += 1
            except Exception:
                bad += 1
        lookups[slot], failures[slot] = count, bad

    def writer(slot: int) -> None:
        barrier.wait()
        count = 0
        while not stop.is_set():
            spell_id = book.bind(spell=Churn, binding_name=f"w{slot}_{count}", existence=Existence.many,
                                 permissions="create")
            book.cleanup_and_remove_spell(spell_id)
            count += 1
        pairs[slot] = count

    threads = [threading.Thread(target=reader, args=(n,)) for n in range(args.readers)]
    threads += [threading.Thread(target=writer, args=(n,)) for n in range(args.writers)]
    for thread in threads:
        thread.start()
    barrier.wait()
    gc.callbacks.append(count_collection)
    started = time.perf_counter()
    stop.wait(args.seconds)
    stop.set()
    for thread in threads:
        thread.join()
    elapsed = time.perf_counter() - started
    gc.callbacks.remove(count_collection)
    conduit.permanent_cleanup()
    print(f"{args.label:5s} gil_enabled={sys._is_gil_enabled()} window={elapsed:.2f}s "
          f"reader_lookups_per_s={sum(lookups) / elapsed:10.0f} writer_pairs_per_s={sum(pairs) / elapsed:8.0f} "
          f"reader_failures={sum(failures)} gc_collections={collections[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
