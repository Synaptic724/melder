"""
Uninstrumented stress for Spellbook.find_spell_by_id (melder_1, 2026-10-10). Supplementary evidence only.

Ticket: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md

Shape (mirrors the MelderOps MissionBuilder test): one dynamic root conduit owns `Searched`, bound before conjure.
Writer threads bind and remove their own spells on that root (bind after conjure, then cleanup_and_remove_spell);
reader threads look `Searched` up through Conduit.get_spell_by_id until the writers finish. Every thread starts on
one threading.Barrier; nothing sleeps. A reader outcome is "ok" when the lookup returns the Searched spell; any
other result or exception is counted under its type and message. Writer exceptions are counted separately.

This is a measurement, not a test: rates depend on the machine, the interpreter build and the GIL mode, so the
script prints counts and always exits 0. The deterministic evidence is test_find_spell_by_id_race.py.

Usage (from a git-archive export of the commit under test, PYTHONPATH=src:.):
    python -X gil=0 stress_find_spell_by_id.py --rounds 20 --writers 4 --readers 4 --iterations 60
"""

import argparse
import collections
import sys
import threading
import time
from typing import Counter, Dict, List, Optional

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration


class Searched:
    """The spell every reader looks up; bound before conjure and never changed."""


class Churn:
    """Bound and removed by the writers under a distinct binding name each time."""


class Round:
    """
    One stress round on a fresh Aether and a fresh dynamic root.

    Contract:
        - `run` starts writers and readers on one Barrier, joins them, tears the root down and returns the counts.
        - Readers stop when every writer has finished (an Event set by the last writer), never on a timer.
    """

    def __init__(self, writers: int, readers: int, iterations: int) -> None:
        self._writers = writers
        self._readers = readers
        self._iterations = iterations
        self.reader_outcomes: Counter[str] = collections.Counter()
        self.writer_errors: Counter[str] = collections.Counter()
        self.lookups = 0
        self._counts_lock = threading.Lock()
        self._writers_left = writers
        self._writers_done = threading.Event()
        self._barrier = threading.Barrier(writers + readers)
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether
        configuration = SpellbookConfiguration()
        set_frame_system_state_for_spellbook_configuration(configuration, "dynamic")
        configuration.load_default_dictionary()
        self._book = Spellbook(configuration=configuration)
        self._searched_id = self._book.bind(spell=Searched, existence=Existence.many, permissions="create")
        self._conduit = self._book.conjure(name="root", dynamic=True)
        searched: Optional[Spell] = self._book.find_spell_by_id(self._searched_id)
        assert searched is not None
        self._searched = searched

    def _writer(self, number: int) -> None:
        """Bind and remove `iterations` Churn spells; count any exception."""
        self._barrier.wait()
        try:
            for iteration in range(self._iterations):
                spell_id = self._book.bind(
                    spell=Churn,
                    binding_name=f"churn_{number}_{iteration}",
                    existence=Existence.many,
                    permissions="create",
                )
                self._book.cleanup_and_remove_spell(spell_id)
        except Exception as error:
            with self._counts_lock:
                self.writer_errors[f"{type(error).__name__}: {error}"] += 1
        finally:
            with self._counts_lock:
                self._writers_left -= 1
                if self._writers_left == 0:
                    self._writers_done.set()

    def _reader(self) -> None:
        """Look Searched up until the writers finish; count each outcome."""
        local: Counter[str] = collections.Counter()
        lookups = 0
        self._barrier.wait()
        while not self._writers_done.is_set():
            lookups += 1
            try:
                found = self._conduit.get_spell_by_id(self._searched_id)
                local["ok" if found is self._searched else f"wrong result: {found!r}"] += 1
            except Exception as error:
                local[f"{type(error).__name__}: {error}"] += 1
        with self._counts_lock:
            self.reader_outcomes.update(local)
            self.lookups += lookups

    def run(self) -> None:
        """Run the round to completion and tear the root down."""
        threads: List[threading.Thread] = [
            threading.Thread(target=self._writer, args=(number,), name=f"writer-{number}")
            for number in range(self._writers)
        ]
        threads += [threading.Thread(target=self._reader, name=f"reader-{n}") for n in range(self._readers)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self._conduit.permanent_cleanup()


def main() -> int:
    """Parse arguments, run the rounds, print per-round and total counts."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--rounds", type=int, default=20)
    parser.add_argument("--writers", type=int, default=4)
    parser.add_argument("--readers", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=60)
    args = parser.parse_args()
    import melder
    print(f"melder {melder.__version__} from {melder.__file__}")
    print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} "
          f"rounds={args.rounds} writers={args.writers} readers={args.readers} iterations={args.iterations}")
    totals: Counter[str] = collections.Counter()
    writer_totals: Counter[str] = collections.Counter()
    lookups = 0
    failing_rounds = 0
    started = time.perf_counter()
    for number in range(args.rounds):
        stress = Round(args.writers, args.readers, args.iterations)
        stress.run()
        bad: Dict[str, int] = {k: v for k, v in stress.reader_outcomes.items() if k != "ok"}
        failing_rounds += 1 if bad or stress.writer_errors else 0
        print(f"round {number:3d}: lookups={stress.lookups} ok={stress.reader_outcomes['ok']} "
              f"failures={sum(bad.values())} {dict(bad) if bad else ''}"
              f"{' writer_errors=' + str(dict(stress.writer_errors)) if stress.writer_errors else ''}")
        totals.update(stress.reader_outcomes)
        writer_totals.update(stress.writer_errors)
        lookups += stress.lookups
    failures = sum(v for k, v in totals.items() if k != "ok")
    print(f"TOTAL rounds={args.rounds} failing_rounds={failing_rounds} lookups={lookups} ok={totals['ok']} "
          f"failures={failures} ({100.0 * failures / max(lookups, 1):.4f}% of lookups) "
          f"seconds={time.perf_counter() - started:.1f}")
    for outcome, count in sorted(totals.items(), key=lambda item: -item[1]):
        if outcome != "ok":
            print(f"  reader {count:7d}  {outcome}")
    for outcome, count in sorted(writer_totals.items(), key=lambda item: -item[1]):
        print(f"  writer {count:7d}  {outcome}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
