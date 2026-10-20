"""
Opposite-direction ownership transfers with concurrent lookups and a deadlock watchdog (melder_1, 2026-10-10).

Ticket: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md

Shape: two dynamic roots A and B in one frame, each owning a stable spell and N movers. One thread transfers A's
movers to B while another transfers B's movers to A (the same pair of conduits in opposite directions); reader
threads look the two stable spells up on their Books (find_spell_by_id) and the first movers up through
Conduit.get_spell_by_id, until both transfer threads finish. Every thread starts on one Barrier; nothing sleeps.
With --fail-every K, every K-th transfer fails after its ownership flip (TransferOfOwnership._teardown_creations
raises), so its rollback runs while readers walk both Books.

Watchdog: every thread is joined with a 60 s bound; a thread still alive is reported as DEADLOCK and the process
exits at once. After each round: every mover is owned by exactly one Book, both Book locks can be taken from the
main thread (no leaked lock), and the roots are torn down.

Measurement, not a test: prints counts per round. Usage (PYTHONPATH=src:. in an export of the tree under test):
    python -X gil=0 opposite_transfer_watchdog.py --rounds 5 --spells 6 --readers 2 --fail-every 0 --label head
"""
import argparse
import collections
import os
import threading
from typing import Any, Counter, Dict, List

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import set_frame_system_state_for_spellbook_configuration

WATCHDOG_SECONDS: float = 60.0


class Stable:
    """Never transferred; the readers' contract target."""


class Mover:
    """Bound under a distinct binding name per mover and transferred between the roots."""


def _book() -> Spellbook:
    """A dynamic-posture Spellbook with one phase worker."""
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, "dynamic")
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def run_round(spells: int, readers: int, fail_every: int) -> Dict[str, Any]:
    """One round on a fresh Aether; returns its counts (exits the process on a watchdog hit)."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book_a, book_b = _book(), _book()
    stable_a = book_a.bind(spell=Stable, binding_name="stable_a", existence=Existence.many, permissions="create")
    stable_b = book_b.bind(spell=Stable, binding_name="stable_b", existence=Existence.many, permissions="create")
    a_ids = [book_a.bind(spell=Mover, binding_name=f"mover_a_{i}", existence=Existence.many, permissions="create")
             for i in range(spells)]
    b_ids = [book_b.bind(spell=Mover, binding_name=f"mover_b_{i}", existence=Existence.many, permissions="create")
             for i in range(spells)]
    root_a = book_a.conjure(name="A", dynamic=True)
    root_b = book_b.conjure(name="B", dynamic=True)
    expected = {stable_a: book_a.find_spell_by_id(stable_a), stable_b: book_b.find_spell_by_id(stable_b)}
    counts: Dict[str, Any] = {"transfers_ok": 0, "transfers_failed": collections.Counter(), "forced": 0,
                              "stable_ok": 0, "stable_bad": collections.Counter(), "moving_calls": 0,
                              "moving_raised": collections.Counter()}
    counts_lock = threading.Lock()
    calls = [0]
    real_teardown = TransferOfOwnership._teardown_creations

    def teardown(transfer: TransferOfOwnership, spell_obj: Any) -> None:
        with counts_lock:
            calls[0] += 1
            fail = fail_every > 0 and calls[0] % fail_every == 0
            if fail:
                counts["forced"] += 1
        if fail:
            raise RuntimeError("forced failure after the ownership flip")
        real_teardown(transfer, spell_obj)

    # Class attribute swap for this round only; restored after the watchdog joins.
    TransferOfOwnership._teardown_creations = teardown
    barrier = threading.Barrier(2 + readers)
    finished = threading.Event()
    remaining = [2]

    def transfer_all(source: Conduit, target: Conduit, ids: List[str]) -> None:
        barrier.wait()
        for spell_id in ids:
            try:
                source.transfer_spell_ownership(spell=spell_id, target_conduit=target)
                with counts_lock:
                    counts["transfers_ok"] += 1
            except Exception as error:  # counted, never hidden
                with counts_lock:
                    counts["transfers_failed"][f"{type(error).__name__}: {str(error)[:60]}"] += 1
        with counts_lock:
            remaining[0] -= 1
            if remaining[0] == 0:
                finished.set()

    def read() -> None:
        barrier.wait()
        ok = 0
        bad: Counter[str] = collections.Counter()
        moving = 0
        raised: Counter[str] = collections.Counter()
        while not finished.is_set():
            for book, spell_id in ((book_a, stable_a), (book_b, stable_b)):
                try:
                    found = book.find_spell_by_id(spell_id)
                    if found is expected[spell_id]:
                        ok += 1
                    else:
                        bad["None" if found is None else "another spell"] += 1
                except Exception as error:
                    bad[f"{type(error).__name__}: {error}"] += 1
            for spell_id in a_ids[:2] + b_ids[:2]:
                try:
                    root_a.get_spell_by_id(spell_id)
                    moving += 1
                except Exception as error:
                    raised[f"{type(error).__name__}: {error}"] += 1
        with counts_lock:
            counts["stable_ok"] += ok
            counts["stable_bad"].update(bad)
            counts["moving_calls"] += moving
            counts["moving_raised"].update(raised)

    threads = [threading.Thread(target=transfer_all, args=(root_a, root_b, a_ids), name="a-to-b", daemon=True),
               threading.Thread(target=transfer_all, args=(root_b, root_a, b_ids), name="b-to-a", daemon=True)]
    threads += [threading.Thread(target=read, name=f"reader-{i}", daemon=True) for i in range(readers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(WATCHDOG_SECONDS)
    alive = [thread.name for thread in threads if thread.is_alive()]
    if alive:
        print(f"DEADLOCK: threads still alive after {WATCHDOG_SECONDS:.0f} s: {alive}", flush=True)
        os._exit(3)
    TransferOfOwnership._teardown_creations = real_teardown
    owners = [(book_a.find_spell_by_id(i) is not None) + (book_b.find_spell_by_id(i) is not None)
              for i in a_ids + b_ids]
    counts["ownership_exactly_one"] = all(n == 1 for n in owners)
    locks_free = True
    for book in (book_a, book_b):
        if book._lock.acquire(True, 5.0):
            book._lock.release()
        else:
            locks_free = False
    counts["book_locks_free"] = locks_free
    root_b.permanent_cleanup()
    root_a.permanent_cleanup()
    return counts


def main() -> None:
    """Run the rounds and print one line per round."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--spells", type=int, default=6)
    parser.add_argument("--readers", type=int, default=2)
    parser.add_argument("--fail-every", type=int, default=0)
    parser.add_argument("--label", default="")
    args = parser.parse_args()
    for number in range(1, args.rounds + 1):
        c = run_round(args.spells, args.readers, args.fail_every)
        print(f"{args.label} round={number} transfers_ok={c['transfers_ok']} "
              f"transfers_failed={dict(c['transfers_failed'])} forced={c['forced']} "
              f"stable_ok={c['stable_ok']} stable_bad={dict(c['stable_bad'])} moving_calls={c['moving_calls']} "
              f"moving_raised={dict(c['moving_raised'])} ownership_exactly_one={c['ownership_exactly_one']} "
              f"book_locks_free={c['book_locks_free']}", flush=True)


if __name__ == "__main__":
    main()
