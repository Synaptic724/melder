"""Probe (melder_0, 2026-11-24; EPIC-2026-10-17-correctness_defects, items C2, C3 and C4): what the frame's
spell-index gate registry and `SpellSystemStates._dirty_indexes` hold as indexes come and go.

One dynamic frame with caching off; Book A binds Root0 before conjure. Then, after conjure:
  step 1  five post-conjure `bind_inactive`s stage edited versions of Root0 on its index (each is bound on an index
          of its own, stamped there, then folded onto Root0's index);
  step 2  five post-conjure binds of new classes, each removed again with `cleanup_spell`;
  step 3  a notch makes the last staged version active, and it is melded.
After each step: the live index ids the frame registers for A's root, the gate registry's keys (C2: a gate whose
key is no live index id is left behind), and `_dirty_indexes` (C4: written on every registration and mark; is it
bounded by the live indexes, and does anything drain it?). After step 3 (C3): whether the active staged version's
own gate (`Spell._creation_gate`, the one its meld doors admit on and its rebuild window drains) is the gate
registered under its current index id or one left under an index id that no longer exists. Every read is
internal, for the diagnosis; the steps are public calls.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_gate_registry_and_dirty_set.py
"""
from typing import Any, List, Set

from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Root0:
    """Version 0 of the staged index, bound bare before conjure."""

    version = 0


def root0_version(number: int) -> type:
    """Return an edited Root0: the same name and binding, a different class-level value, so a new spell_id."""
    return type("Root0", (), {"version": number, "__module__": __name__, "__qualname__": "Root0"})


def temporary_class(number: int) -> type:
    """Return a new class of its own name, bound once and cleaned up again in step 2."""
    return type(f"Temp{number}", (), {"__module__": __name__, "__qualname__": f"Temp{number}"})


def report(label: str, book: Spellbook, root: Conduit) -> None:
    """Print the live index ids, the gate registry and the dirty set after one step (internal reads)."""
    frame = Spellbook._aether._aetheric_frames["probe-gates"]
    live: Set[str] = {index.id for index in frame._spell_registry.get(root.id, set())}
    gates = frame._dev_ops_manager.creation_gate_controller._spell_index_creation_gates
    states = book._spell_system_states
    dirty: Set[str] = set(states._dirty_indexes)
    print(f"{label}: live indexes {len(live)}; gates {len(gates)}, of them under no live index "
          f"{len(set(gates) - live)}; dirty set {len(dirty)}, of them no live index {len(dirty - live)}")


def run() -> None:
    """Build the world and run the three steps."""
    book = Spellbook(aetheric_frame="probe-gates", configuration=SpellbookConfiguration("probe-gates").with_defaults())
    book.configure_aether_frame(
        system_state="dynamic", disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    book.bind(spell=Root0, existence=Existence.many)
    root = book.conjure(dynamic=True, name="probe-gates-root")
    root.meld(Root0)
    report("after conjure and a meld of Root0", book, root)
    index = book.find_spell_by_spell_id(Bind.spell_id_inspector(Root0)).spell_index
    staged: List[str] = []
    for number in range(1, 6):
        staged.append(book.bind_inactive(spell=root0_version(number), spell_index=index, existence=Existence.many))
    report("step 1, after five post-conjure bind_inactive", book, root)
    for number in range(1, 6):
        temp = temporary_class(number)
        book.bind(spell=temp, existence=Existence.many)
        root.meld(temp)
        root.cleanup_spell(spell=book.find_spell_by_spell_id(Bind.spell_id_inspector(temp)))
    report("step 2, after five binds removed by cleanup_spell", book, root)
    root.notch_spell(spell_index=index, spell_id=staged[-1])
    built: Any = root.meld(Root0)
    print("step 3, notched to the last staged version and melded: version", built.version)
    report("step 3", book, root)
    version = book.find_spell_by_spell_id(staged[-1])
    controller = Spellbook._aether._aetheric_frames["probe-gates"]._dev_ops_manager.creation_gate_controller
    own_gate = version._creation_gate
    keys = [key for key, gate in controller._spell_index_creation_gates.items() if gate is own_gate]
    print("C3: the version's own gate is the one registered under its current index id:",
          own_gate is controller.get_spell_index_gate(version.spell_index.id))
    print("C3: the version's own gate is registered under:",
          "its current index" if keys == [version.spell_index.id] else f"{len(keys)} key(s), none its index")
    print("C4: dirty-set readers - consume_dirty_indexes is never called by melder; a manual call drains",
          len(book._spell_system_states.consume_dirty_indexes()), "ids")


run()
