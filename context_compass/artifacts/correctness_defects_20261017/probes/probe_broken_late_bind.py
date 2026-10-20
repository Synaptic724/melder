"""Probe (melder_0, 2026-10-17; EPIC-2026-10-17-correctness_defects, sweep A11): what a late bind whose commit
validation fails leaves registered, and how an agent gets past it.

A post-conjure `Spellbook.bind` stages the new spell on its bind transaction; the commit runs phases 1-4 for it
(`ChangeControlManager._default_structural_validator`), so a structurally broken class fails there, after the bind
has registered it. Each case in a fresh Aether and its own dynamic frame with caching off; the Book binds English
active under (Greeter, 'greeter') and conjures, then binds late:
  B1  control: a sound class (Spanish) under (Greeter, 'spanish').
  B2  a broken class (SelfMade: its constructor takes its own class, SELF_DEPENDENCY) under (Greeter, 'broken') -
      what bind raises, what stays registered, what a meld by address answers, whether a fixed class can bind the
      address, and whether staging the fixed class on the broken spell's index and notching to it works.
  B3  B2, then `cleanup_spell` of the broken spell and a bind of the fixed class at the address.

Read-only on src/: run from this folder with the repository's src first on sys.path, e.g.
    PYTHONPATH=<repo>/src python -X gil=0 probes/probe_broken_late_bind.py
"""
from typing import Protocol

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


class Greeter(Protocol):
    """The contract every greeter implements."""

    def greet(self) -> str: ...


class English:
    """Bound before conjure."""

    def greet(self) -> str:
        """Return the English greeting."""
        return "hello"


class Spanish:
    """A sound late bind."""

    def greet(self) -> str:
        """Return the Spanish greeting."""
        return "hola"


class SelfMade:
    """A broken late bind: its constructor takes its own class (SELF_DEPENDENCY at Phase 4)."""

    def __init__(self, other: SelfMade) -> None:
        """Keep the other instance."""
        self.other = other

    def greet(self) -> str:
        """Return a greeting."""
        return "hi"


class FixedMade:
    """The fixed version of SelfMade."""

    def greet(self) -> str:
        """Return a greeting."""
        return "hi"


def fresh_aether() -> None:
    """Install a fresh Aether and rebind it on Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def world(frame: str):
    """A dynamic Book with English active, conjured as 'lender'."""
    spellbook = Spellbook(aetheric_frame=frame, configuration=SpellbookConfiguration(frame).with_defaults())
    spellbook.configure_aether_frame(system_state="dynamic", disposal=None, disposal_method_names=None,
                                     system_caching_enabled=False)
    spellbook.bind(spell=English, spellframe=Greeter, binding_name="greeter", existence=Existence.many,
                   permissions="create")
    conduit = spellbook.conjure(dynamic=True, name="lender")
    return spellbook, conduit


def attempt(label: str, fn):
    """Run `fn`; print what it returned or raised; return the result or None."""
    try:
        result = fn()
        shown = result if isinstance(result, str) and len(result) < 40 else type(result).__name__
        print(f"    {label} -> {shown}")
        return result
    except Exception as error:
        print(f"    {label} raised {type(error).__name__}: {str(error).splitlines()[0][:150]}")
        return None


def late_bind(spellbook: Spellbook, cls: type, name: str):
    """Bind `cls` late under (Greeter, name)."""
    return spellbook.bind(spell=cls, spellframe=Greeter, binding_name=name, existence=Existence.many,
                          permissions="create")


def registered(spellbook: Spellbook, cls: type):
    """The Book's active Spell bound for `cls`, if any."""
    for spell in list(spellbook._spells_by_id.values()):
        if spell.spell is cls:
            return spell
    return None


def report(step: str, spellbook: Spellbook, conduit: Conduit, cls: type, name: str):
    """Print what the Book and the frame hold for `cls` and what a meld by address answers."""
    print(f"  [{step}]")
    spell = registered(spellbook, cls)
    print(f"    {cls.__name__} active in the Book: {spell is not None}")
    if spell is not None:
        holder = spellbook._aetheric_frame.get_lookup(spell._key)
        print(f"    frame claim for its address held by it: {holder == spell.spell_id}")
        states = [s for s in spellbook._spell_system_states.iter_states() if s.spell_index_id == spell.spell_index.id]
        print(f"    lineage registered: {[s.validity.name for s in states]}")
    attempt(f"meld(spellframe=Greeter, binding_name='{name}')",
            lambda: type(conduit.meld(spellframe=Greeter, binding_name=name)).__name__)
    return spell


def b1() -> None:
    """Control: a sound late bind."""
    print("B1 control: late bind of a sound class (Spanish) under (Greeter, 'spanish')")
    spellbook, conduit = world("b1")
    attempt("bind(Spanish)", lambda: late_bind(spellbook, Spanish, "spanish") and "spell_id")
    report("after", spellbook, conduit, Spanish, "spanish")


def broken(frame: str):
    """B2's world after the failed bind."""
    spellbook, conduit = world(frame)
    attempt("bind(SelfMade)", lambda: late_bind(spellbook, SelfMade, "broken") and "spell_id")
    spell = report("after the failed bind", spellbook, conduit, SelfMade, "broken")
    return spellbook, conduit, spell


def b2() -> None:
    """A broken late bind, then the versioned way past it."""
    print("B2 late bind of a broken class (SelfMade) under (Greeter, 'broken')")
    spellbook, conduit, spell = broken("b2")
    attempt("bind(FixedMade) at (Greeter, 'broken')", lambda: late_bind(spellbook, FixedMade, "broken") and "spell_id")
    index = attempt("find_spell_index(Greeter, 'SelfMade', 'broken')",
                    lambda: spellbook.find_spell_index(Greeter, "SelfMade", "broken"))
    if index is None:
        return
    fixed_id = attempt("conduit.bind_inactive(FixedMade, spell_index=that index)",
                       lambda: conduit.bind_inactive(spell=FixedMade, spell_index=index, spellframe=Greeter,
                                                     binding_name="broken", existence=Existence.many,
                                                     permissions="create"))
    if fixed_id is None:
        return
    attempt("notch_spell(-> FixedMade)", lambda: conduit.notch_spell(spell_index=index, spell_id=fixed_id) and "Spell")
    report("after the notch", spellbook, conduit, FixedMade, "broken")


def b3() -> None:
    """A broken late bind, then cleanup_spell and a fresh bind."""
    print("B3 B2's failed bind, then cleanup_spell of SelfMade and bind(FixedMade) at the address")
    spellbook, conduit, spell = broken("b3")
    if spell is None:
        return
    attempt("conduit.cleanup_spell(SelfMade)", lambda: conduit.cleanup_spell(spell=spell))
    attempt("bind(FixedMade) at (Greeter, 'broken')", lambda: late_bind(spellbook, FixedMade, "broken") and "spell_id")
    report("after", spellbook, conduit, FixedMade, "broken")


def main() -> None:
    """Run every case in its own fresh Aether."""
    for case in (b1, b2, b3):
        fresh_aether()
        try:
            case()
        except Exception as error:
            print(f"  CASE RAISED {type(error).__name__}: {error}")
        print()
    fresh_aether()


if __name__ == "__main__":
    main()
