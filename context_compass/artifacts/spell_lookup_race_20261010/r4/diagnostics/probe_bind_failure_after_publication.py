"""
Probe: a bind that fails after it published into the active maps (melder_1, 2026-10-10).

Ticket: context_compass/tickets/tasks/2026-10-10_investigate_spell_lookup_by_id_race_task.md

Forces Spellbook._register_owned_spell_id to raise for one bind - the statement R5 moved inside its publication
lock - and reports, on the tree under test: the error bind raised, whether another thread can take the Book lock
afterwards (bounded 5 s: a leaked lock would fail it), what the half-published entry looks like (the existing
rollback contract: bind does not unpublish once registration started), and whether a later bind and lookups work.

Usage (PYTHONPATH=src:. in an export): python -X gil=0 probe_bind_failure_after_publication.py --label head
"""
import argparse
import threading
from typing import Any, Dict

from melder import Aether, Conduit, Spellbook


class Kept:
    """Bound before the failing bind; must stay resolvable."""


class Failing:
    """The bind forced to fail after publication."""


class After:
    """Bound after the failure; must bind normally."""


def run(label: str) -> Dict[str, Any]:
    """Run the probe once and return what it saw."""
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook(aetheric_frame=f"bind-failure-{label}")
    kept_id = book.bind(spell=Kept, existence="many")
    real_register = Spellbook._register_owned_spell_id
    armed = [True]

    def register(spellbook: Spellbook, spell_id: str, spell: Any) -> None:
        if armed[0] and spell.spell_name == "Failing":
            armed[0] = False
            raise RuntimeError("forced failure after publication")
        real_register(spellbook, spell_id, spell)

    Spellbook._register_owned_spell_id = register
    outcome: Dict[str, Any] = {"label": label}
    try:
        book.bind(spell=Failing, existence="many")
        outcome["bind"] = "returned"
    except Exception as error:  # the error is the evidence
        outcome["bind"] = f"raised {type(error).__name__}: {error}"
    finally:
        Spellbook._register_owned_spell_id = real_register
    acquired = threading.Event()

    def take_lock() -> None:
        if book._lock.acquire(True, 5.0):
            book._lock.release()
            acquired.set()

    worker = threading.Thread(target=take_lock, name="lock-check")
    worker.start()
    worker.join(10.0)
    outcome["book_lock_free_from_another_thread"] = acquired.is_set()
    failing = [spell for spell in book.spells.values() if spell.spell_name == "Failing"]
    outcome["failing_entry_left_in_active_map"] = len(failing)
    outcome["failing_found_by_id"] = (
        book.find_spell_by_id(failing[0].spell_id) is failing[0] if failing else "no entry"
    )
    outcome["kept_found"] = book.find_spell_by_id(kept_id) is not None
    after_id = book.bind(spell=After, existence="many")
    outcome["later_bind_found"] = book.find_spell_by_id(after_id) is not None
    book.cleanup()
    return outcome


def main() -> None:
    """Parse arguments and print the outcome."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    print(run(parser.parse_args().label))


if __name__ == "__main__":
    main()
