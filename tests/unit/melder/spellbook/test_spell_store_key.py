"""
Unit tests - `Spell.store_key`: the key every Creations store files a Spell's objects under.

STORY-2026-10-25-creations_store_slots_by_binding. The key is `<spell_id>:<binding_hash>`: the spell_id (the code)
and the binding hash (how it is bound), so two bindings of one class file apart and the same binding files where it
did. It is built with the Spell and kept after cleanup, like `spell_id` and `binding_manifest`.
"""
from typing import Any, List, Optional

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_types.spell_types import SpellType

SPELL_ID = "c" * 64


class _States:
    """SpellSystemStates stand-in: Spell construction and cleanup only record structural marks."""

    def mark_structural_change(self, spell_index: Any, reason: Any = None) -> None:
        """Accept a mark."""


class _BookStub:
    """Spellbook stand-in that drives the Spell's own cleanup."""

    def __init__(self) -> None:
        self._spell_system_states = _States()

    def cleanup_and_remove_spell(self, spell: Spell) -> None:
        """Clean the spell as its Book would."""
        spell._spellbook_cleanup = True
        spell.cleanup()


class _Svc:
    """A class to bind."""


def _spell(existence: Existence = Existence.unique, disposal: Optional[List[str]] = None,
           binding_name: Optional[str] = "svc") -> Spell:
    """Build one Spell of `_Svc` at the spellframe "svc"."""
    return Spell(
        spell=_Svc,
        spell_index=SpellIndex(SPELL_ID),
        spellframe="svc",
        binding_name=binding_name,
        spell_name="_Svc",
        existence=existence,
        spell_type=SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
        spell_id=SPELL_ID,
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=_BookStub(),
        disposal_method_names=disposal,
    )


def test_the_store_key_is_the_spell_id_and_the_binding_hash() -> None:
    """`store_key` joins the spell_id and the binding hash with ':'."""
    spell = _spell(disposal=["close"])
    assert spell.store_key == f"{SPELL_ID}:{spell.binding_hash}"


def test_the_same_binding_gives_the_same_store_key() -> None:
    """Equal code bound the same way files where it did (the 2026-10-03 slot)."""
    assert _spell(disposal=["close"]).store_key == _spell(disposal=["close"]).store_key


def test_another_binding_gives_another_store_key() -> None:
    """A change of existence, disposal names or address is another slot."""
    base = _spell(disposal=["close"]).store_key
    assert _spell(existence=Existence.many, disposal=["close"]).store_key != base
    assert _spell(disposal=["shutdown"]).store_key != base
    assert _spell(disposal=None).store_key != base
    assert _spell(disposal=["close"], binding_name="other").store_key != base


def test_the_store_key_is_kept_after_cleanup() -> None:
    """A cleaned Spell still names the slot its objects are in."""
    spell = _spell(disposal=["close"])
    key = spell.store_key
    spell._spellbook_cleanup = True
    spell.cleanup()
    assert spell.store_key == key
