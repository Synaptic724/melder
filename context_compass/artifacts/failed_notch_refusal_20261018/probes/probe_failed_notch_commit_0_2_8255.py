"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A9): what a notch whose commit validation
fails leaves behind.

Copied by melder_1 on 2026-10-18 to re-run it on 0.2.8255 (STORY-2026-10-17-failed_notch_keeps_switch_without_
borrowers): one call renamed, `find_spell_by_id` -> `find_spell_by_spell_id` (0.2.8253, no alias); for an active
spell_id both return the same Spell. Nothing else changed.

Each case in a fresh Aether and its own dynamic frame with caching off. A lender Book binds English active on an
index; a borrower links and contracts the whole index (`add_index_to_contract`); a second version is staged on the
index (`Conduit.bind_inactive`) and the lender notches to it. A notch to a never-compiled version runs phases 1-4 at
its transaction's commit, so a structurally broken version fails there, after the seam has switched the index.
  N1  control: the staged version is sound (French) - owner and borrower both follow.
  N2  the staged version is broken (SelfMade: its constructor takes its own class, SELF_DEPENDENCY) - what notch_spell
      raises, which version the lender's index selects, what the borrower holds, and what melds answer.
  N3  N2, then a notch back to English - does it restore owner and borrower?

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_failed_notch_commit.py
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
    """A broken version 2: its constructor takes its own class (SELF_DEPENDENCY at Phase 4)."""

    def __init__(self, other: SelfMade) -> None:
        """Keep the other instance."""
        self.other = other

    def greet(self) -> str:
        """Return a greeting."""
        return "hi"


class Note:
    """A plain spell so the borrower Book has something to conjure."""


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def world(frame: str, staged: type):
    """English active on the lender's index, the borrower contracting the whole index, `staged` parked on it."""
    lender_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    lender_book.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                      system_caching_enabled=False)
    borrower_book = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    english_id = lender_book.bind(spell=English, spellframe=Greeter, binding_name="greeter",
                                  existence=Existence.many, permissions="create")
    borrower_book.bind(spell=Note, existence=Existence.many, permissions="create")
    lender = lender_book.conjure(dynamic=True, name="lender")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    index = lender_book.find_spell_by_spell_id(english_id).spell_index
    lender.link(borrower)
    with borrower.transaction("link", conduits=[borrower, lender]):
        assert borrower.add_index_to_contract(index=index, conduit=lender, permissions="create")
    staged_id = lender.bind_inactive(spell=staged, spell_index=index, spellframe=Greeter, binding_name="greeter",
                                     existence=Existence.many, permissions="create")
    names = {english_id: "English", staged_id: staged.__name__}
    return lender_book, borrower_book, lender, borrower, index, english_id, staged_id, names


def view(step: str, lender_book: Spellbook, borrower_book: Spellbook, lender: Conduit, index, names: dict) -> None:
    """Print the lender's selection and active/parked versions, and the borrower's copies."""
    selected = names.get(index.selected_spell_id, index.selected_spell_id)
    active = sorted(names.get(i, i[:10]) for i in lender_book._spells_by_id if i in names)
    parked = sorted(names.get(i, i[:10]) for i in lender_book._inactive_spells if i in names)
    b_active = sorted(names.get(i, i[:10]) for i in borrower_book._contracted_spells_by_id.get(lender._id, {}))
    b_parked = sorted(names.get(i, i[:10]) for i in borrower_book._inactive_contracted_spells.get(lender._id, {}))
    print(f"  [{step}]")
    print(f"    lender: index selects {selected}; active {active}; parked {parked}")
    print(f"    borrower: active copies {b_active}; parked copies {b_parked}")


def notch(lender: Conduit, index, spell_id: str, label: str) -> None:
    """Notch to `spell_id`; print the outcome."""
    try:
        lender.notch_spell(spell_index=index, spell_id=spell_id)
        print(f"    notch_spell(-> {label}) returned")
    except Exception as error:
        print(f"    notch_spell(-> {label}) raised {type(error).__name__}: {str(error).splitlines()[0][:150]}")


def meld(conduit: Conduit, label: str, **kwargs) -> None:
    """Meld; print what came back or what was raised."""
    try:
        obj = conduit.meld(**kwargs)
        print(f"    {label} -> {type(obj).__name__}")
    except Exception as error:
        print(f"    {label} raised {type(error).__name__}: {str(error).splitlines()[0][:150]}")


def n1() -> None:
    """Control: a sound version."""
    print("N1 control: notch to a sound staged version (French)")
    lender_book, borrower_book, lender, borrower, index, english_id, staged_id, names = world("n1", French)
    view("before the notch", lender_book, borrower_book, lender, index, names)
    notch(lender, index, staged_id, "French")
    view("after the notch", lender_book, borrower_book, lender, index, names)


def broken_notch(frame: str):
    """N2's world and its failed notch."""
    lender_book, borrower_book, lender, borrower, index, english_id, staged_id, names = world(frame, SelfMade)
    view("before the notch", lender_book, borrower_book, lender, index, names)
    notch(lender, index, staged_id, "SelfMade")
    view("after the failed notch", lender_book, borrower_book, lender, index, names)
    return lender_book, borrower_book, lender, borrower, index, english_id, staged_id, names


def n2() -> None:
    """A broken version."""
    print("N2 notch to a staged version that fails structural validation (SelfMade, SELF_DEPENDENCY)")
    lender_book, borrower_book, lender, borrower, index, english_id, staged_id, names = broken_notch("n2")
    meld(lender, "lender meld(spellframe=Greeter, binding_name='greeter')", spellframe=Greeter,
         binding_name="greeter")
    meld(lender, "lender meld(spell_id=English)", spell_id=english_id)


def n3() -> None:
    """A broken version, then a notch back."""
    print("N3 N2, then a notch back to English")
    lender_book, borrower_book, lender, borrower, index, english_id, staged_id, names = broken_notch("n3")
    notch(lender, index, english_id, "English")
    view("after the notch back", lender_book, borrower_book, lender, index, names)
    meld(lender, "lender meld(spell_id=English)", spell_id=english_id)


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (n1, n2, n3):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
