"""Probe (melder_1, 2026-10-19; STORY-2026-10-17-staged_version_releases_active_signature): melder_0's claims cases
C1-C4 and C6 (probes/probe_signature_claims.py of the correctness sweep) rewritten for the current names
(`find_spell_by_spell_id` since 0.2.8253). Each case runs in a fresh Aether and its own dynamic frame, caching off.

  C1  bind_inactive after conjure; the staged version shares the active version's key.
  C2  the same before conjure, then conjure.
  C3  remove the staged version into its own index, then add it back (after a notch to it and back).
  C4  cleanup_spell of the staged version alone in the index remove_from_spell_index minted.
  C6  staging into Book L a version keyed like Book O's active spell.
For each step: who holds the signature frame-wide, whether the Book's address map routes the key to the active
version's index, what a meld by address and `find_spell_index` answer, and whether another Book can bind the
signature. Read-only on src/: run with the repository's src first on sys.path, -X gil=0 and -X gil=1.
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
    """Another Book's spell, or a third party."""

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


def report(step: str, spellbook: Spellbook, conduit: Optional[Conduit], key, index, names: dict) -> None:
    """Print who holds `key` frame-wide, where the Book routes it, and what the address lookups answer."""
    holder = spellbook._aetheric_frame.get_lookup(key)
    routed = spellbook._lookup_spells.get(key)
    print(f"  [{step}] frame claim: {label(names, holder)}; book route to the index: {routed is index}")
    if conduit is not None:
        try:
            obj = conduit.meld(spellframe=Greeter, binding_name="greeter")
            print(f"    meld by address -> {type(obj).__name__}")
        except Exception as error:
            print(f"    meld by address raised {type(error).__name__}: {str(error)[:90]}")
    try:
        found = spellbook.find_spell_index(Greeter, "English", "greeter")
        print(f"    find_spell_index is the index: {found is index}")
    except Exception as error:
        print(f"    find_spell_index raised {type(error).__name__}: {error}")


def try_bind(spellbook: Spellbook, cls: type, name: str, names: dict, key) -> None:
    """Try to bind `cls` active under (Greeter, name) in `spellbook`; print the outcome."""
    try:
        spell_id = bind(spellbook, cls, name)
        names[spell_id] = cls.__name__
        print(f"    another Book's bind of (Greeter, '{name}') ACCEPTED; frame claim now:"
              f" {label(names, spellbook._aetheric_frame.get_lookup(key))}")
    except RuntimeError as error:
        print(f"    another Book's bind of (Greeter, '{name}') refused: {str(error)[:80]}")


def world(frame: str):
    """English active on its index in a conjured dynamic Book, plus a second Book in the frame."""
    lender_book = book(frame)
    dynamic(lender_book)
    other_book = book(frame)
    names = {}
    english_id = bind(lender_book, English, "greeter")
    names[english_id] = "English"
    lender = lender_book.conjure(dynamic=True, name="lender")
    english = lender_book.find_spell_by_spell_id(english_id)
    return lender_book, other_book, lender, english, names


def c1() -> None:
    """bind_inactive after conjure, same key."""
    print("C1 bind_inactive after conjure; same key")
    lender_book, other_book, lender, english, names = world("c1")
    index, key = english.spell_index, english._key
    report("before", lender_book, None, key, index, names)
    names[stage(lender, French, "greeter", index)] = "French"
    report("after bind_inactive(French)", lender_book, lender, key, index, names)
    try_bind(other_book, Spanish, "greeter", names, key)


def c2() -> None:
    """bind_inactive before conjure, same key."""
    print("C2 bind_inactive before conjure; same key")
    lender_book = book("c2")
    dynamic(lender_book)
    names = {}
    english_id = bind(lender_book, English, "greeter")
    names[english_id] = "English"
    english = lender_book.find_spell_by_spell_id(english_id)
    index, key = english.spell_index, english._key
    names[stage(lender_book, French, "greeter", index)] = "French"
    lender = lender_book.conjure(dynamic=True, name="lender")
    report("after bind_inactive(French), then conjure", lender_book, lender, key, index, names)


def healed(frame: str):
    """C1's world with French staged, then a notch to French and back to English."""
    lender_book, other_book, lender, english, names = world(frame)
    index = english.spell_index
    french_id = stage(lender, French, "greeter", index)
    names[french_id] = "French"
    lender.notch_spell(spell_index=index, spell_id=french_id)
    lender.notch_spell(spell_index=index, spell_id=english.spell_id)
    return lender_book, other_book, lender, english, names, french_id


def c3() -> None:
    """Index move that empties a parked-only index."""
    print("C3 remove French into its own index, then add it back")
    lender_book, other_book, lender, english, names, french_id = healed("c3")
    index, key = english.spell_index, english._key
    report("after the notch to French and back", lender_book, None, key, index, names)
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    lender.add_to_spell_index(spell_id=french_id, target_index=index)
    report("after remove_from_spell_index, add_to_spell_index back", lender_book, lender, key, index, names)
    try_bind(other_book, Spanish, "greeter", names, key)


def c4() -> None:
    """cleanup_spell of a parked version alone in its minted index."""
    print("C4 cleanup_spell of French alone in the minted index")
    lender_book, other_book, lender, english, names, french_id = healed("c4")
    index, key = english.spell_index, english._key
    lender.remove_from_spell_index(spell_id=french_id, source_index=index)
    lender.cleanup_spell(spell_id=french_id) if False else lender.cleanup_spell(
        spell=lender_book._inactive_spells[french_id])
    report("after cleanup_spell(French)", lender_book, lender, key, index, names)
    try_bind(other_book, Spanish, "greeter", names, key)


def c6() -> None:
    """Staging a version whose key another Book's active spell holds."""
    print("C6 Book L stages French keyed like Book O's active Spanish")
    lender_book, other_book, lender, english, names = world("c6")
    spanish_id = bind(other_book, Spanish, "spanish")
    names[spanish_id] = "Spanish (Book O, active)"
    spanish_key = other_book.find_spell_by_spell_id(spanish_id)._key
    names[stage(lender, French, "spanish", english.spell_index)] = "French (Book L, parked)"
    print(f"  frame claim {spanish_key}: {label(names, lender_book._aetheric_frame.get_lookup(spanish_key))}")
    try_bind(book("c6"), Italian, "spanish", names, spanish_key)


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (c1, c2, c3, c4, c6):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
    fresh_aether()


if __name__ == "__main__":
    main()
