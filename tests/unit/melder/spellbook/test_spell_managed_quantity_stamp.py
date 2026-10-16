"""
Unit tests: stamping an owner gives a managed spell its pool (STORY-2026-10-15-managed_quantity_pool, S3).

`Spell._add_owned_conduit` is every owner stamp - conjure, a post-conjure bind or bind_inactive, the transfer flip.
For a managed version it asks the owner root's store for the version's pool (`ensure_managed_quantity`, idempotent);
every other existence is stamped exactly as before.
"""
from typing import Any, List

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.creations.conduit_creations import ConduitCreations
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.synchronization.creation_gate_controller import CreationGateController


class _States:
    """SpellSystemStates stand-in: Spell construction only reads the reference."""


class _SpellbookStub:
    """Minimal owner: the Spell reads `_spell_system_states` and asks the Book to remove it on cleanup."""

    def __init__(self) -> None:
        """Hold a states stand-in."""
        self._spell_system_states = _States()

    def cleanup_and_remove_spell(self, spell: Spell) -> None:
        """Run the local teardown the way the Book does."""
        spell._spellbook_cleanup = True
        spell.cleanup()


class Pooled:
    """A managed target class."""

    def close(self) -> None:
        """Release nothing."""


class _RecordingStore:
    """Store stand-in recording each ensure request."""

    def __init__(self) -> None:
        """Start with no requests."""
        self.ensured: List[Any] = []

    def ensure_managed_quantity(self, spell: Any) -> None:
        """Record the request."""
        self.ensured.append(spell)


def _spell(existence: Existence = Existence.managed_spell_quantity, **options: Any) -> Spell:
    """
    Build one class Spell.

    Args:
        existence: Its Existence.
        **options: Managed options for the constructor.

    Returns:
        Spell: The Spell.
    """
    if existence is Existence.managed_spell_quantity:
        options.setdefault("managed_spell_mode", ManagedSpellMode.elastic)
        options.setdefault("managed_spell_limit", 256)
    return Spell(
        spell=Pooled,
        spell_index=SpellIndex("managed-version"),
        spellframe=None,
        binding_name=None,
        spell_name="Pooled",
        existence=existence,
        spell_type=SpellType.SPELL,
        spell_id="managed-version",
        permissions=Permissions.create,
        aetheric_frame="default",
        spellbook=_SpellbookStub(),
        disposal_method_names=["close"],
        **options,
    )


def _stamp(spell: Spell, creations: Any) -> None:
    """
    Stamp the spell's owner the way conjure does.

    Args:
        spell: The Spell.
        creations: The owner root's store.
    """
    spell._add_owned_conduit(
        "root-1",
        "root",
        creations,
        dynamic_environment=False,
        creation_gate_controller=CreationGateController(),
        caching_enabled=False,
    )


def test_stamping_a_managed_spell_ensures_its_pool() -> None:
    """The owner store is asked once per stamp for the version's pool."""
    spell = _spell()
    store = _RecordingStore()
    try:
        _stamp(spell, store)
        assert store.ensured == [spell]
        assert spell._owner_creations is store
    finally:
        spell.cleanup()


def test_stamping_into_a_real_root_store_creates_the_pool_there() -> None:
    """The pool lands in the owner root's store under the spell_id, composed from the Spell."""
    spell = _spell(managed_spell_mode=ManagedSpellMode.limited_quantity, managed_spell_limit=5)
    store = ConduitCreations(conduit_id="root-1")
    try:
        _stamp(spell, store)
        pool = store.get_managed_quantity("managed-version")
        assert (pool.spell, pool.mode, pool.limit, pool.owner_conduit_id) == (
            spell, ManagedSpellMode.limited_quantity, 5, "root-1",
        )
        _stamp(spell, store)
        assert store.get_managed_quantity("managed-version") is pool
    finally:
        store.cleanup()
        spell.cleanup()


def test_stamping_a_non_managed_spell_asks_for_no_pool() -> None:
    """Every other existence is stamped as before."""
    spell = _spell(existence=Existence.unique)
    store = _RecordingStore()
    try:
        _stamp(spell, store)
        assert store.ensured == []
    finally:
        spell.cleanup()


def test_stamping_without_a_store_asks_for_no_pool() -> None:
    """A stamp that carries no store (no owner scope to hold a pool) composes nothing."""
    spell = _spell()
    try:
        _stamp(spell, None)
        assert spell._owner_creations is None
    finally:
        spell.cleanup()
