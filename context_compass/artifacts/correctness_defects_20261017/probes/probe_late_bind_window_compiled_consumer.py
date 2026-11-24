"""Probe (melder_0, 2026-11-24; EPIC-2026-10-17-correctness_defects, item C6, the known limit of #330's fix): is a
consumer the binding thread compiled over a window spell served to another thread's meld while the window is open?

World: one dynamic frame with caching off. `Needy(a: Alpha, b: Beta)` is bound before conjure, with neither class
bound, so both parameters are unresolved inputs and conjure succeeds. A late bind of Alpha then commits, which marks
Needy `gated` (its socket waits under Alpha's address). Then an explicit late-bind window opens on the main thread
(`with book.transaction("bind")`) and binds Beta, so Beta is a window spell until the block ends. Every case runs in
its own process:
  W1   inside the window the binding thread melds Needy, which compiles it over Beta; then a second thread melds Needy.
  W1b  as W1, but the binding thread melds Beta first, then Needy.
  W2   control: the binding thread does not meld Needy; the second thread melds the gated Needy.
  W3   control: the second thread melds Beta itself.
#330's rule says a meld on another thread that reaches a window spell is refused with MeldExecutionError. The second
thread's meld is joined with a timeout, so a meld that waits for the window instead shows as still running when the
window ends. Beta records the thread that built it. Lineage validity reads are internal, for the diagnosis only.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_late_bind_window_compiled_consumer.py W1
"""
import sys
import threading
from typing import Dict

from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Alpha:
    """Bound by a late bind that commits before the window opens."""

    def __init__(self) -> None:
        """Record the thread that built this object."""
        self.built_on = threading.current_thread().name


class Beta:
    """The window spell: bound inside the explicit late-bind window."""

    def __init__(self) -> None:
        """Record the thread that built this object."""
        self.built_on = threading.current_thread().name


class Needy:
    """The consumer: bound before conjure, waiting on both classes."""

    def __init__(self, a: Alpha, b: Beta) -> None:
        """Keep both dependencies."""
        self.a = a
        self.b = b


def validity(book: Spellbook, target: type) -> str:
    """Return the lineage validity of `target`'s spell in `book` (internal read)."""
    spell = book.find_spell_by_spell_id(Bind.spell_id_inspector(target))
    state = spell.system_state
    return "no state" if state is None else state.validity.name


def meld_on_second_thread(root: Conduit, target: type, outcome: Dict[str, str]) -> threading.Thread:
    """Start a thread named second-thread that melds `target` and records what happened in `outcome`."""

    def body() -> None:
        """Meld `target` and describe the result or the error."""
        try:
            built = root.meld(target)
            if isinstance(built, Needy):
                outcome["result"] = f"built Needy; its Beta was built on {built.b.built_on}"
            else:
                outcome["result"] = f"built {type(built).__name__} on {built.built_on}"
        except Exception as error:
            outcome["result"] = f"{type(error).__name__}: {str(error)[:170]}"

    thread = threading.Thread(target=body, name="second-thread")
    thread.start()
    return thread


def run(case: str) -> None:
    """Build the world and run one case."""
    print(f"--- {case}")
    book = Spellbook(aetheric_frame="probe-c6", configuration=SpellbookConfiguration("probe-c6").with_defaults())
    book.configure_aether_frame(
        system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    book.bind(spell=Needy, existence=Existence.many)
    root = book.conjure(dynamic=True, name="probe-c6-root")
    book.bind(spell=Alpha, existence=Existence.many)
    print("after Alpha's late bind committed: Needy", validity(book, Needy))
    outcome: Dict[str, str] = {}
    thread = None
    with book.transaction("bind"):
        book.bind(spell=Beta, existence=Existence.many)
        states = book.find_spell_by_spell_id(Bind.spell_id_inspector(Beta))._spell_system_states
        print("inside the window: Beta is marked late-bound:",
              Bind.spell_id_inspector(Beta) in states.late_bind_thread_ids)
        if case == "W1b":
            own_beta = root.meld(Beta)
            print("binding thread melds Beta: built on", own_beta.built_on)
        if case in ("W1", "W1b"):
            own = root.meld(Needy)
            print("binding thread melds Needy: built; its Beta was built on", own.b.built_on)
            print("Needy after the binding thread's meld:", validity(book, Needy))
        target = Beta if case == "W3" else Needy
        thread = meld_on_second_thread(root, target, outcome)
        thread.join(timeout=5.0)
        if thread.is_alive():
            print(f"second thread melding {target.__name__}: still running when the window ends (it waits)")
        else:
            print(f"second thread melding {target.__name__}, inside the window:", outcome["result"])
    print("window committed")
    if thread is not None and thread.is_alive():
        thread.join(timeout=10.0)
        print("second thread, after the window:", outcome.get("result", "still running"))


run(sys.argv[1])
