"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A7): Book teardown with parked versions.

What it checks, each case in a fresh Aether and its own dynamic frame with caching off. A keeper Book is conjured in
the same frame first, so the frame outlives the torn-down Book. The Book is torn down through its root conduit
(`conduit.cleanup()`, which reaches `Spellbook.cleanup`):
  T1  control: English active alone - after teardown its Spell and index are cleaned.
  T2  English active, French parked on English's index - is French cleaned, and can it be cleaned afterwards?
  T3  French separated into the index `remove_from_spell_index` mints - is that index cleaned?
  T4  a notch across keys (English 'greeter' -> Spanish 'spanish') before teardown - who holds ('greeter') after,
      and can another Book bind it?
  T5  a managed version parked beside the active one - are both pools gone from ReleaseManagedSpell after teardown?

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_book_teardown_parked.py
"""
from typing import Protocol

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
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
    """Version 2 under another binding name."""

    def greet(self) -> str:
        """Return the Spanish greeting."""
        return "hola"


class Italian:
    """Another Book's binding after the teardown."""

    def greet(self) -> str:
        """Return the Italian greeting."""
        return "ciao"


class Keeper:
    """The keeper Book's one spell."""


class Pooled:
    """A managed class with two versions."""


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def book(frame: str) -> Spellbook:
    """A Spellbook on `frame` with its own default configuration."""
    return Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())


def frame_with_keeper(frame: str) -> None:
    """Settle the frame dynamic (caching off) and conjure a keeper Book so the frame outlives the probed Book."""
    keeper = book(frame)
    keeper.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                  system_caching_enabled=False)
    keeper.bind(spell=Keeper, existence=Existence.many, permissions="create")
    keeper.conjure(dynamic=True, name="keeper")


def greeter(spellbook: Spellbook, cls: type, name: str) -> str:
    """Bind `cls` active under (Greeter, name) as `many`."""
    return spellbook.bind(spell=cls, spellframe=Greeter, binding_name=name, existence=Existence.many,
                          permissions="create")


def stage(conduit: Conduit, cls: type, name: str, index) -> str:
    """Stage `cls` parked under (Greeter, name) on `index`."""
    return conduit.bind_inactive(spell=cls, spell_index=index, spellframe=Greeter, binding_name=name,
                                 existence=Existence.many, permissions="create")


def probed_book(frame: str):
    """The probed Book with English active, conjured as root 'lender'."""
    frame_with_keeper(frame)
    spellbook = book(frame)
    english_id = greeter(spellbook, English, "greeter")
    conduit = spellbook.conjure(dynamic=True, name="lender")
    english = spellbook.find_spell_by_id(english_id)
    return spellbook, conduit, english


def teardown(conduit: Conduit) -> None:
    """Tear the probed Book down through its root conduit; print what the teardown raised, if anything."""
    try:
        conduit.cleanup()
        print("    root conduit torn down")
    except Exception as error:
        print(f"    root teardown raised {type(error).__name__}: {str(error)[:150]}")


def state(label: str, obj) -> None:
    """Print whether a Spell or SpellIndex is cleaned."""
    print(f"    {label} cleaned: {obj.cleaned}")


def try_cleanup(label: str, spell) -> None:
    """Try to clean a Spell directly; print the outcome."""
    try:
        spell.cleanup()
        print(f"    {label}.cleanup() returned; cleaned: {spell.cleaned}")
    except Exception as error:
        print(f"    {label}.cleanup() raised {type(error).__name__}: {str(error)[:150]}")


def t1() -> None:
    """Control: one active version."""
    print("T1 control: English active alone")
    spellbook, conduit, english = probed_book("t1")
    index = english.spell_index
    teardown(conduit)
    state("English (active)", english)
    state("English's index", index)


def t2() -> None:
    """A parked version on the active version's index."""
    print("T2 English active, French parked on English's index")
    spellbook, conduit, english = probed_book("t2")
    index = english.spell_index
    french_id = stage(conduit, French, "greeter", index)
    french = spellbook._inactive_spells[french_id]
    teardown(conduit)
    state("English (active)", english)
    state("French (parked)", french)
    state("the shared index", index)
    try_cleanup("French", french)


def t3() -> None:
    """A parked version alone in a minted index."""
    print("T3 French separated into the index remove_from_spell_index mints")
    spellbook, conduit, english = probed_book("t3")
    index = english.spell_index
    french_id = stage(conduit, French, "greeter", index)
    conduit.remove_from_spell_index(spell_id=french_id, source_index=index)
    french = spellbook._inactive_spells[french_id]
    minted = french.spell_index
    print(f"    French's index is a new one: {minted is not index}")
    teardown(conduit)
    state("French (parked)", french)
    state("the minted index", minted)
    state("English's index", index)


def t4() -> None:
    """A notch across keys, then teardown."""
    print("T4 notch English ('greeter') -> Spanish ('spanish'), then teardown")
    spellbook, conduit, english = probed_book("t4")
    index, key = english.spell_index, english._key
    frame = spellbook._aetheric_frame
    spanish_id = stage(conduit, Spanish, "spanish", index)
    conduit.notch_spell(spell_index=index, spell_id=spanish_id)
    holder = frame.get_lookup(key)
    print(f"    before teardown, ('greeter') held by English: {holder == english.spell_id}")
    teardown(conduit)
    holder = frame.get_lookup(key)
    print(f"    after teardown, ('greeter') held by English (its Book gone): {holder == english.spell_id}")
    other = book("t4")
    try:
        greeter(other, Italian, "greeter")
        print("    another Book's bind of (Greeter, 'greeter') ACCEPTED")
    except RuntimeError as error:
        print(f"    another Book's bind of (Greeter, 'greeter') refused: {str(error)[:150]}")


def t5() -> None:
    """Managed pools of an active and a parked version."""
    print("T5 a managed class with one version active and one parked, then teardown")
    frame_with_keeper("t5")
    spellbook = book("t5")
    active_id = spellbook.bind(spell=Pooled, spellframe="pools", binding_name="pooled",
                               existence=Existence.managed_spell_quantity, permissions="create",
                               managed_spell_mode="limited_quantity", managed_spell_limit=1)
    conduit = spellbook.conjure(dynamic=True, name="lender")
    index = spellbook.find_spell_by_id(active_id).spell_index
    conduit.bind_inactive(spell=Pooled, spell_index=index, spellframe="pools", binding_name="pooled",
                          existence=Existence.managed_spell_quantity, permissions="create",
                          managed_spell_mode="limited_quantity", managed_spell_limit=2)
    print(f"    pools of Pooled before teardown: {len(ReleaseManagedSpell().describe(Pooled))}")
    teardown(conduit)
    print(f"    pools of Pooled after teardown: {len(ReleaseManagedSpell().describe(Pooled))}")


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (t1, t2, t3, t4, t5):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
