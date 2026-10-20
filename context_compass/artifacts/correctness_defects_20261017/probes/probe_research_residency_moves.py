"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A8): MutationResearch residency of moved
and separated versions.

One fresh Aether with MutationResearch configured and active (no record hydration) and a dynamic frame with caching
off; English ('greeter') is bound active, French staged on its index under its own binding name ('french', so the
notch inside the minted index claims no signature English holds). After each step it prints
`residency_view(...)['runtime']` and the index it names for each version, beside where the Book keeps it:
  V1  control: English active, French parked on English's index.
  V2  French separated into the index `remove_from_spell_index` mints.
  V3  French notched active inside that minted index (English stays active in its own).
  V4  control: a third version parked on English's index, then English's index unchanged.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_research_residency_moves.py
"""
from typing import Protocol

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract every greeter version implements."""

    def greet(self) -> str: ...


class English:
    """Version 1, bound active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """Version 2, staged, then separated and notched in its own index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class German:
    """Version 3, staged on English's index for the control."""

    def greet(self) -> str:
        """Return the German greeting."""
        return "hallo"


def fresh_aether() -> Aether:
    """Install a fresh Aether, rebind it on Spellbook and Conduit, and activate MutationResearch."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    root = aether.mutation_research
    root.configure(root.create_configuration().with_defaults().activate())
    root.activate(hydrate_from_record=False)
    return aether


def report(step: str, aether: Aether, spellbook: Spellbook, names: dict) -> None:
    """Print each version's residency verdict and index beside the Book's own answer."""
    print(f"  [{step}]")
    labels = {}
    for spell_id, name in names.items():
        spell = spellbook._spells_by_id.get(spell_id) or spellbook._inactive_spells.get(spell_id)
        labels[spell.spell_index.id] = labels.get(spell.spell_index.id, f"index{len(labels) + 1}")
    for spell_id, name in names.items():
        spell = spellbook._spells_by_id.get(spell_id) or spellbook._inactive_spells.get(spell_id)
        book_state = "active" if spell_id in spellbook._spells_by_id else "parked"
        view = aether.mutation_research.residency_view(spell_id)
        index_label = labels.get(view["index_id"], "none" if view["index_id"] is None else "other")
        print(f"    {name}: Book says {book_state} in {labels[spell.spell_index.id]};"
              f" residency_view says {view['runtime']} in {index_label}")


def main() -> None:
    """Run the four steps in one fresh world."""
    aether = fresh_aether()
    spellbook = Spellbook(aetheric_frame="v", configuration=SpellbookConfiguration("v").with_defaults())
    spellbook.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                     system_caching_enabled=False)
    english_id = spellbook.bind(spell=English, spellframe=Greeter, binding_name="greeter",
                                existence=Existence.many, permissions="create")
    conduit = spellbook.conjure(dynamic=True, name="root")
    index = spellbook.find_spell_by_id(english_id).spell_index
    french_id = conduit.bind_inactive(spell=French, spell_index=index, spellframe=Greeter, binding_name="french",
                                      existence=Existence.many, permissions="create")
    names = {english_id: "English", french_id: "French"}
    report("V1 French parked on English's index", aether, spellbook, names)
    conduit.remove_from_spell_index(spell_id=french_id, source_index=index)
    report("V2 French separated into a minted index", aether, spellbook, names)
    minted = spellbook._inactive_spells[french_id].spell_index
    conduit.notch_spell(spell_index=minted, spell_id=french_id)
    report("V3 French notched active inside the minted index", aether, spellbook, names)
    german_id = conduit.bind_inactive(spell=German, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                      existence=Existence.many, permissions="create")
    names[german_id] = "German"
    report("V4 German parked on English's index", aether, spellbook, names)
    Aether._reset_singleton_for_tests()


if __name__ == "__main__":
    main()
