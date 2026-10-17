"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A1): binding-signature claims around
staged versions.

What it checks, each case in a fresh Aether and its own dynamic frame with caching off:
  C1  bind_inactive after conjure, staged version sharing the active version's key.
  C2  the same before conjure, then conjure.
  C3  an index move: remove the staged version into its own index, add it back.
  C4  cleanup_spell of a staged version that sits alone in the index remove_from_spell_index minted.
  C5  a notch between two versions whose keys differ.
  C6  staging into one Book a version whose key another Book's active spell holds.
  C7  a notch inside the index remove_from_spell_index minted, while the sibling keeps the same key active.
For each step it prints who holds the signature frame-wide (LookupContainer), whether the Book's address map
(`_lookup_spells`) still routes the key to the active version's index, and what a meld by address and
`find_spell_index` answer. A second Book then tries to bind the same signature where the case calls for it.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_signature_claims.py
"""
from typing import Optional, Protocol

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
    """Version 2, staged on English's index."""

    def greet(self) -> str:
        """Return the French greeting."""
        return "bonjour"


class Spanish:
    """A version, or another Book's spell, depending on the case."""

    def greet(self) -> str:
        """Return the Spanish greeting."""
        return "hola"


class Italian:
    """A third party binding the signature after a case's step."""

    def greet(self) -> str:
        """Return the Italian greeting."""
        return "ciao"


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def book(frame: str) -> Spellbook:
    """A Spellbook on `frame` with its own default configuration."""
    return Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())


def dynamic(spellbook: Spellbook) -> None:
    """Settle the frame dynamic with caching off."""
    spellbook.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                     system_caching_enabled=False)


def bind(spellbook: Spellbook, cls: type, name: str) -> str:
    """Bind `cls` active under (Greeter, name) as `many`."""
    return spellbook.bind(spell=cls, spellframe=Greeter, binding_name=name, existence=Existence.many,
                          permissions="create")


def stage(owner, cls: type, name: str, index) -> str:
    """Stage `cls` parked under (Greeter, name) on `index` through `owner` (a Conduit or a Spellbook)."""
    return owner.bind_inactive(spell=cls, spell_index=index, spellframe=Greeter, binding_name=name,
                               existence=Existence.many, permissions="create")


def label(names: dict, spell_id: Optional[str]) -> str:
    """Name a spell_id by the class it was bound for."""
    return "none" if spell_id is None else names.get(spell_id, spell_id[:10])


def report(step: str, spellbook: Spellbook, conduit: Optional[Conduit], key, index, names: dict,
           name: str = "greeter", cls_name: str = "English") -> None:
    """Print who holds `key` frame-wide, where the Book routes it, and what the address lookups answer."""
    holder = spellbook._aetheric_frame.get_lookup(key)
    routed = spellbook._lookup_spells.get(key)
    active = spellbook._spells.get(index)
    print(f"  [{step}]")
    print(f"    frame claim {key}: {label(names, holder)}")
    print(f"    book address map routes it to the index: {routed is index}"
          f" (index active: {label(names, active.spell_id if active is not None else None)})")
    if conduit is not None:
        try:
            obj = conduit.meld(spellframe=Greeter, binding_name=name)
            print(f"    meld(spellframe=Greeter, binding_name='{name}') -> {type(obj).__name__}")
        except Exception as error:
            print(f"    meld(spellframe=Greeter, binding_name='{name}') raised {type(error).__name__}: {error}")
    try:
        found = spellbook.find_spell_index(Greeter, cls_name, name)
        print(f"    find_spell_index(Greeter, '{cls_name}', '{name}') is the index: {found is index}")
    except Exception as error:
        print(f"    find_spell_index(Greeter, '{cls_name}', '{name}') raised {type(error).__name__}: {error}")


def try_bind(spellbook: Spellbook, cls: type, name: str, names: dict, key) -> None:
    """Try to bind `cls` active under (Greeter, name) in `spellbook`; print the outcome and the claim after."""
    try:
        spell_id = bind(spellbook, cls, name)
        names[spell_id] = cls.__name__
        print(f"    another bind of (Greeter, '{name}') ACCEPTED ({cls.__name__}); frame claim now:"
              f" {label(names, spellbook._aetheric_frame.get_lookup(key))}")
    except RuntimeError as error:
        print(f"    another bind of (Greeter, '{name}') refused: {str(error)[:150]}")


def world(frame: str):
    """English active on its index in a conjured dynamic Book, plus a second Book in the frame."""
    lender_book = book(frame)
    dynamic(lender_book)
    other_book = book(frame)
    names = {}
    english_id = bind(lender_book, English, "greeter")
    names[english_id] = "English"
    lender = lender_book.conjure(dynamic=True, name="lender")
    english = lender_book.find_spell_by_id(english_id)
    return lender_book, other_book, lender, english, names


def c1() -> None:
    """bind_inactive after conjure, same key."""
    print("C1 bind_inactive after conjure; the staged version shares the active version's key")
    lender_book, other_book, lender, english, names = world("c1")
    index, key = english.spell_index, english._key
    report("before", lender_book, lender, key, index, names)
    french_id = stage(lender, French, "greeter", index)
    names[french_id] = "French"
    print(f"    staged French's key == English's key: {lender_book._inactive_spells[french_id]._key == key}")
    report("after bind_inactive(French)", lender_book, lender, key, index, names)
    try_bind(other_book, Spanish, "greeter", names, key)
    print(f"    English still the index's active version: {lender_book._spells.get(index) is english}")


def c2() -> None:
    """bind_inactive before conjure, same key."""
    print("C2 bind_inactive before conjure; same key")
    fresh = "c2"
    lender_book = book(fresh)
    dynamic(lender_book)
    names = {}
    english_id = bind(lender_book, English, "greeter")
    names[english_id] = "English"
    english = lender_book.find_spell_by_id(english_id)
    index, key = english.spell_index, english._key
    report("before (no conduit yet)", lender_book, None, key, index, names)
    french_id = stage(lender_book, French, "greeter", index)
    names[french_id] = "French"
    report("after bind_inactive(French), before conjure", lender_book, None, key, index, names)
    lender = lender_book.conjure(dynamic=True, name="lender")
    report("after conjure", lender_book, lender, key, index, names)


def healed_world(frame: str):
    """C1's world with French staged, then healed by a notch to French and back to English."""
    lender_book, other_book, lender, english, names = world(frame)
    index, key = english.spell_index, english._key
    french_id = stage(lender, French, "greeter", index)
    names[french_id] = "French"
    lender.notch_spell(spell_index=index, spell_id=french_id)
    lender.notch_spell(spell_index=index, spell_id=english._spell_id if hasattr(english, "_spell_id") else
                       english.spell_id)
    return lender_book, other_book, lender, english, names, french_id


def c3() -> None:
    """Index move that empties a parked-only index."""
    print("C3 index moves: remove French into its own index, then add it back")
    lender_book, other_book, lender, english, names, french_id = healed_world("c3")
    index, key = english.spell_index, english._key
    report("healed (notch to French and back)", lender_book, lender, key, index, names)
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    report("after remove_from_spell_index(French)", lender_book, lender, key, index, names)
    lender.add_to_spell_index(spell_id=french_id, target_index=index)
    report("after add_to_spell_index(French) back", lender_book, lender, key, index, names)
    try_bind(other_book, Spanish, "greeter", names, key)


def c4() -> None:
    """cleanup_spell of a parked version alone in its minted index."""
    print("C4 cleanup_spell of French alone in the index remove_from_spell_index minted")
    lender_book, other_book, lender, english, names, french_id = healed_world("c4")
    index, key = english.spell_index, english._key
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    report("after remove_from_spell_index(French)", lender_book, lender, key, index, names)
    lender.cleanup_spell(spell=lender_book._inactive_spells[french_id])
    report("after cleanup_spell(French)", lender_book, lender, key, index, names)
    try_bind(other_book, Spanish, "greeter", names, key)


def c5() -> None:
    """Notch between versions with different keys."""
    print("C5 notch across keys: English (Greeter, 'greeter') -> Spanish (Greeter, 'spanish') on one index")
    lender_book, other_book, lender, english, names = world("c5")
    index, key = english.spell_index, english._key
    spanish_id = stage(lender, Spanish, "spanish", index)
    names[spanish_id] = "Spanish"
    spanish_key = lender_book._inactive_spells[spanish_id]._key
    lender.notch_spell(spell_index=index, spell_id=spanish_id)
    print(f"    after the notch: English parked: {english.spell_id in lender_book._inactive_spells}")
    report("old key after notch", lender_book, lender, key, index, names)
    report("new key after notch", lender_book, lender, spanish_key, index, names, name="spanish",
           cls_name="Spanish")
    try_bind(other_book, Italian, "greeter", names, key)


def c6() -> None:
    """Staging a version whose key another Book's active spell holds."""
    print("C6 staging in Book L a version keyed like Book O's active spell")
    lender_book, other_book, lender, english, names = world("c6")
    spanish_id = bind(other_book, Spanish, "spanish")
    names[spanish_id] = "Spanish (Book O, active)"
    spanish_key = other_book.find_spell_by_id(spanish_id)._key
    print(f"    before: frame claim {spanish_key}: {label(names, lender_book._aetheric_frame.get_lookup(spanish_key))}")
    french_id = stage(lender, French, "spanish", english.spell_index)
    names[french_id] = "French (Book L, parked)"
    print(f"    after Book L stages French as (Greeter, 'spanish'): frame claim {spanish_key}:"
          f" {label(names, lender_book._aetheric_frame.get_lookup(spanish_key))}")
    print(f"    Spanish still active in Book O: {spanish_id in other_book._spells_by_id}")
    third = book("c6")
    try_bind(third, Italian, "spanish", names, spanish_key)


def c7() -> None:
    """Notch inside the minted index while the sibling keeps the same key active."""
    print("C7 notch French active inside its own minted index; English stays active with the same key")
    lender_book, other_book, lender, english, names, french_id = healed_world("c7")
    index, key = english.spell_index, english._key
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    minted = lender_book._inactive_spells[french_id].spell_index
    lender.notch_spell(spell_index=minted, spell_id=french_id)
    print(f"    English active in its index: {lender_book._spells.get(index) is english};"
          f" French active in the minted index: {lender_book._spells.get(minted) is not None}")
    report("English's index after the notch", lender_book, lender, key, index, names)


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (c1, c2, c3, c4, c5, c6, c7):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
