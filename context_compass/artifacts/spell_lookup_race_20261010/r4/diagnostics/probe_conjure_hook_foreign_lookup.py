"""
Probe: can a conduit lifecycle hook that runs inside conjure wait for a lookup made on another thread?

A user `on_conduit_post_created` hook starts a thread that calls `Spellbook.find_spell_by_id` on the conjuring
Book and waits for it. Conjure runs its hooks while it holds the Book lock
(`Spellbook._conjure_within_transaction_window`), so a lookup that takes the Book lock cannot finish until the
hook returns. The hook's wait is bounded (`--wait` seconds) only so a blocked run terminates; it is a deadlock
detector, not a timing assumption: on a tree whose lookup takes no Book lock the event is set long before it.

Run from a tree root: PYTHONPATH=src python probe_conjure_hook_foreign_lookup.py --label <tree> [--wait 5]
"""
import argparse
import threading
import time
from typing import Any, Dict

from melder import Aether, Conduit, Spellbook


class Provider:
    """A plain spell target."""

    def __init__(self) -> None:
        """No collaborators."""


def run(label: str, wait_seconds: float) -> Dict[str, Any]:
    """Conjure one Book whose post-created hook waits on a foreign-thread lookup; report what happened."""
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    book = Spellbook(aetheric_frame=f"hook-foreign-lookup-{label}")
    spell_id = book.bind(spell=Provider, existence="many", spellframe="providers", binding_name="provider")
    outcome: Dict[str, Any] = {"label": label}
    done = threading.Event()

    def lookup() -> None:
        try:
            found = book.find_spell_by_id(spell_id)
            outcome["lookup"] = "found" if found is not None else "None"
        except BaseException as exc:  # report, never hide
            outcome["lookup"] = f"raised {exc!r}"
        finally:
            done.set()

    def on_post_created(_conduit: Any) -> None:
        worker = threading.Thread(target=lookup, name="foreign-lookup", daemon=True)
        started = time.perf_counter()
        worker.start()
        outcome["finished_while_hook_waited"] = done.wait(wait_seconds)
        outcome["hook_wait_s"] = round(time.perf_counter() - started, 3)

    book.get_configuration().add_hooks(book._id, on_conduit_post_created=on_post_created)
    root = book.conjure(name="root")
    outcome["finished_after_conjure"] = done.wait(30.0)
    root.cleanup()
    return outcome


def main() -> None:
    """Parse arguments and print the outcome."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--wait", type=float, default=5.0)
    args = parser.parse_args()
    print(run(args.label, args.wait))


if __name__ == "__main__":
    main()
