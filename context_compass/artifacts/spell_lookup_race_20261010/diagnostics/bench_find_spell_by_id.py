"""
Single-thread latency of Spellbook.find_spell_by_id (melder_1, 2026-10-10). Measurement, not a test.

Ticket: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md

For each book size n, an unconjured Spellbook binds n spells (one class under n binding names); the script times
find_spell_by_id for the first-bound spell (the walk stops at step 1) and the last-bound spell (the walk visits all
n indexes), and a miss (an id no index owns). timeit with 7 repeats; the minimum and the median ns per call are
printed. Run it on the commit under test and on the candidate export alternately, in the same GIL mode.

Usage (PYTHONPATH=src:. inside an export): python -X gil=0 bench_find_spell_by_id.py --sizes 1 8 64 512
"""

import argparse
import statistics
import sys
import timeit
from typing import List

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration


class Bound:
    """One class bound under n binding names."""


def _fresh_book() -> Spellbook:
    """A fresh Aether and an unconjured automatic-posture Spellbook."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "automatic")
    configuration.load_default_dictionary()
    return Spellbook(configuration=configuration)


def _ns_per_call(book: Spellbook, spell_id: str) -> List[float]:
    """Seven timeit repeats of find_spell_by_id(spell_id), in ns per call."""
    timer = timeit.Timer(lambda: book.find_spell_by_id(spell_id))
    number, _ = timer.autorange()
    number = max(number, 1)
    return [seconds * 1e9 / number for seconds in timer.repeat(repeat=7, number=number)]


def main() -> int:
    """Bind, time and print one line per (size, case)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--sizes", type=int, nargs="+", default=[1, 8, 64, 512])
    parser.add_argument("--label", default="")
    args = parser.parse_args()
    import melder
    print(f"# {args.label} melder {melder.__version__} python {sys.version.split()[0]} "
          f"gil_enabled={sys._is_gil_enabled()}")
    for size in args.sizes:
        book = _fresh_book()
        ids = [book.bind(spell=Bound, binding_name=f"b{i}", existence=Existence.many, permissions="create")
               for i in range(size)]
        for case, spell_id in (("first", ids[0]), ("last", ids[-1]), ("miss", "0" * 64)):
            samples = _ns_per_call(book, spell_id)
            print(f"{args.label:5s} n={size:4d} {case:5s} min={min(samples):10.1f} ns "
                  f"median={statistics.median(samples):10.1f} ns")
        book.cleanup()
    return 0


if __name__ == "__main__":
    sys.exit(main())
