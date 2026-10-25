"""
Integration: purge and the live-creation probes never miss a version while notches move it
(STORY-2026-10-25-probe_and_purge_reach_every_version, failure mode F15).

A notch moves a version between its Book's active and parked maps under the Book lock, taking it out of one map before
it puts it in the other, and the conduit then moves each linked borrower's copy the same way under the borrower's Book
lock. `has_live_creation`, `describe_live_creation_status` and `purge` given a spell_id read the active maps without a
lock and, on a miss, read every map of the Book once under its lock, where a version is in exactly one map. So a probe
or a purge racing notches to and from its version always finds it - from the lender and from a borrower whose index
link follows the notches. Before the story a parked spell_id raised KeyError "[MELD] No spell found with spell_id".

Real threads against real notches, so the test is integration; run it with the GIL off (`-X gil=0`) and on.
"""

import time
from collections.abc import Iterator
from threading import Event, Thread
from typing import Any, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._spell_identity_test_support import version_of


class Resource:
    """
    Purpose: A `unique` resource whose two versions are notched back and forth; disposal is observable.
    Contract: `cleanup` counts calls; owns no external resource.
    """

    version: int = 1

    def __init__(self) -> None:
        """
        Purpose: Start undisposed.
        Returns: None.
        """
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """
        Purpose: Count one disposal.
        Returns: None.
        """
        self.cleanup_calls += 1


class Ticket:
    """
    Purpose: A `many` spell with no objects, purged during the race to exercise purge's discovery alone.
    Contract: Plain; no disposal method, so nothing is recorded and every purge returns 0.
    """

    version: int = 1


@pytest.fixture(autouse=True)
def fresh_world() -> Iterator[None]:
    """
    Purpose: Isolate the test: fresh Nexus and Aether, rebound on Spellbook and Conduit, before and after.
    Yields: None while the test owns its world.
    """
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _book(*, first: bool = True) -> Spellbook:
    """
    Purpose: One Book of the "default" frame with disposal names ["cleanup"] and one phase worker.
    Args:
        first: True for the frame's first Book, which settles the frame dynamic with caching off.
    Returns:
        Spellbook: The Book, not conjured.
    """
    configuration = SpellbookConfiguration("default")
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame="default", configuration=configuration)
    if first:
        book.configure_aether_frame(
            system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
        )
    return book


@pytest.mark.parametrize("prober", ["lender", "index_borrower"])
def test_probes_and_purges_never_miss_a_version_while_it_is_notched(prober: str) -> None:
    """
    Purpose: F15 - probes and purges by spell_id never raise for a version a notch is moving.
    Contract: Two indexes are notched back and forth - at least 40 times each, and until each of two prober threads
        has completed 20 rounds, so the probes overlap the notches with the GIL on too - while the probers probe both
        versions of the `unique` index (each has a live object, so every probe is True and names its own version)
        and purge both versions of the `many` index (no objects, so every purge returns 0). No call raises, no answer
        is wrong, and no object is disposed.
    Args:
        prober: "lender" probes through the lender's root; "index_borrower" through a borrower whose index links
            follow the notches.
    Returns: None.
    """
    book = _book()
    v1_id = book.bind(spell=Resource, existence=Existence.unique, permissions="create")
    w1_id = book.bind(spell=Ticket, existence=Existence.many, permissions="create")
    root = book.conjure(dynamic=True, name="lender")
    resource_index = root.get_spell_by_spell_id(v1_id).spell_index
    ticket_index = root.get_spell_by_spell_id(w1_id).spell_index
    v2_id = root.bind_inactive(
        spell=version_of(Resource, version=2), spell_index=resource_index, existence=Existence.unique,
        permissions="create",
    )
    w2_id = root.bind_inactive(
        spell=version_of(Ticket, version=2), spell_index=ticket_index, existence=Existence.many,
        permissions="create",
    )
    borrower = _book(first=False).conjure(dynamic=True, name="borrower")
    try:
        root.link(borrower)
        borrower.add_index_to_contract(index=resource_index, conduit=root, permissions="create")
        borrower.add_index_to_contract(index=ticket_index, conduit=root, permissions="create")
        first = root.meld(spell_id=v1_id)
        root.notch_spell(spell_index=resource_index, spell_id=v2_id)
        second = root.meld(spell_id=v2_id)
        scope = root if prober == "lender" else borrower
        errors: List[Tuple[str, Any]] = []
        progress = [0, 0]
        turns: List[int] = []
        done = Event()

        def notch_back_and_forth() -> None:
            """Notch both indexes, alternating versions, until 40 turns and 20 prober rounds each (60 s cap)."""
            turn = 0
            deadline = time.monotonic() + 60.0
            try:
                while (turn < 40 or min(progress) < 20) and time.monotonic() < deadline:
                    root.notch_spell(spell_index=resource_index, spell_id=v1_id if turn % 2 == 0 else v2_id)
                    root.notch_spell(spell_index=ticket_index, spell_id=w1_id if turn % 2 == 0 else w2_id)
                    turn += 1
            except BaseException as error:
                errors.append(("notch", error))
            finally:
                turns.append(turn)
                done.set()

        def probe_and_purge(slot: int) -> None:
            """Probe and purge every version until the notches are done; record any raise or wrong answer."""
            try:
                while not done.is_set():
                    for spell_id in (v1_id, v2_id):
                        if scope.has_live_creation(spell=spell_id) is not True:
                            errors.append(("not live", spell_id))
                        if scope.describe_live_creation_status(spell=spell_id)["spell_id"] != spell_id:
                            errors.append(("wrong version", spell_id))
                    for spell_id in (w1_id, w2_id):
                        if scope.purge(spell_id=spell_id) != 0:
                            errors.append(("purged objects", spell_id))
                    progress[slot] += 1
            except BaseException as error:
                errors.append(("probe", error))

        threads = [Thread(target=probe_and_purge, args=(slot,)) for slot in range(2)]
        threads.append(Thread(target=notch_back_and_forth))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=120)
        assert not any(thread.is_alive() for thread in threads)
        assert errors == []
        assert turns[0] >= 40 and min(progress) >= 20
        assert (first.cleanup_calls, second.cleanup_calls) == (0, 0)
    finally:
        borrower.cleanup()
        root.cleanup()
        book.cleanup()
