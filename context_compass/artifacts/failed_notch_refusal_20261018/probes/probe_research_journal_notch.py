"""Probe (melder_1, 2026-10-18; STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers): what the research
journal keeps for a notch, with MutationResearch active.

  J1  a sound version (French) notched in: the acts journaled for French.
  J2  a broken version (SelfMade, a constructor taking its own class) notched in: notch_spell raises; the acts
      journaled for SelfMade - does the record keep a promotion that the error says failed?

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_research_journal_notch.py
"""
from typing import Protocol

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract every version implements."""

    def greet(self) -> str: ...


class English:
    """Version 1, active."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class French:
    """A sound version 2."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class SelfMade:
    """A broken version 2: its constructor takes its own class."""

    def __init__(self, other: SelfMade) -> None:
        """Keep the other instance."""
        self.other = other

    def greet(self) -> str:
        """Return a greeting."""
        return "hi"


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


def acts(aether: Aether, spell_id: str) -> list:
    """The acts the default research set journaled for `spell_id`."""
    history = aether.mutation_research.research_set().history(spell_id)
    return [entry["act"] for entry in history["transitions"]]


def case(label: str, frame: str, staged: type) -> None:
    """Bind English, stage `staged` on its index, notch to it, print the outcome and the journal."""
    aether = fresh_aether()
    book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                system_caching_enabled=False)
    english_id = book.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence=Existence.many,
                           permissions="create")
    root = book.conjure(dynamic=True, name="root")
    index = book.find_spell_by_spell_id(english_id).spell_index
    staged_id = root.bind_inactive(spell=staged, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                   existence=Existence.many, permissions="create")
    print(label)
    print(f"  before: {staged.__name__} acts {acts(aether, staged_id)}; English acts {acts(aether, english_id)}")
    try:
        root.notch_spell(spell_index=index, spell_id=staged_id)
        print(f"  notch_spell(-> {staged.__name__}) returned")
    except Exception as error:
        print(f"  notch_spell(-> {staged.__name__}) raised {type(error).__name__}: {str(error).splitlines()[0]}")
    selected = "English" if index.selected_spell_id == english_id else staged.__name__
    print(f"  index selects {selected}")
    print(f"  after: {staged.__name__} acts {acts(aether, staged_id)}; English acts {acts(aether, english_id)}")
    root.cleanup()
    aether.mutation_research.deactivate()


def main() -> None:
    """Run both cases, each in its own fresh Aether."""
    for label, frame, staged in (("J1 sound version (French)", "j1", French),
                                 ("J2 broken version (SelfMade)", "j2", SelfMade)):
        try:
            case(label, frame, staged)
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    Aether._reset_singleton_for_tests()


if __name__ == "__main__":
    main()
