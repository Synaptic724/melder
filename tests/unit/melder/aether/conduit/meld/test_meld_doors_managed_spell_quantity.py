"""
Unit tests of the meld doors' store readers for a managed spell (STORY-2026-10-15-managed_quantity_pool, S3).

A managed spell keeps no object in any store: its objects are leased from a pool in its owner root's store. So the
conduit door's purge answers zero from the caller's own store, the SpellSpace door keeps refusing it, the reuse-only
meld refuses it, and both live-creation probes answer from the owner store's pool (live while any object it built
is alive).
"""
from typing import Any

import pytest

from melder.aether.conduit.creations.conduit_creations import ConduitCreations
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from tests.unit.melder.aether.conduit.meld.test_concrete_meld_subclasses import (
    _make_conduit_meld,
    _make_spellspace_meld,
    _seed_spell,
    _SpellStub,
)


class _Pooled:
    """A pooled object."""

    def close(self) -> None:
        """Nothing to release."""


def _managed_spell(owner_creations: Any, owner_conduit_id: str = "owner") -> _SpellStub:
    """
    A managed spell stub owned by `owner_creations`, with the fields its pool reads.

    Args:
        owner_creations: The owner root's store.
        owner_conduit_id: The owner root's id.

    Returns:
        _SpellStub: The stub.
    """
    spell = _SpellStub(
        spell_id="managed-sid",
        existence=Existence.managed_spell_quantity,
        owner_creations=owner_creations,
        owner_conduit_id=owner_conduit_id,
    )
    spell.binding_name = None
    # The managed class: the key ReleaseManagedSpell routes releases by (S4).
    spell.spell = _Pooled
    spell.disposal_method_names = ["close"]
    spell.managed_spell_mode = ManagedSpellMode.elastic
    spell.managed_spell_limit = 256
    spell.managed_spell_timeout_seconds = None
    spell.managed_spell_reset_methods = ()
    return spell


def _with_objects(owner_creations: ConduitCreations, spell: _SpellStub, idle: int, out: int) -> None:
    """
    Ensure the spell's pool and give it `idle` idle objects and `out` objects out.

    Args:
        owner_creations: The owner store.
        spell: The managed spell.
        idle: Objects to leave idle.
        out: Objects to leave out.
    """
    pool = owner_creations.ensure_managed_quantity(spell)
    for _ in range(idle + out):
        assert pool.reserve() is None
    for _ in range(idle):
        pool.put_back(_Pooled())


def test_conduit_purge_of_a_managed_spell_returns_zero_from_the_callers_store() -> None:
    """No authority check and no disposal: purge has nothing to retire for a managed spell."""
    meld, _creations, spellbook = _make_conduit_meld(conduit_id="caller")
    owner_creations = ConduitCreations(conduit_id="owner")
    spell = _managed_spell(owner_creations)
    _with_objects(owner_creations, spell, idle=2, out=1)
    _seed_spell(spellbook, spell)
    assert meld.purge("managed-sid") == 0
    pool = owner_creations.get_managed_quantity("managed-sid")
    assert (pool.idle_count, pool.count) == (2, 3)


def test_spellspace_purge_keeps_refusing_a_managed_spell() -> None:
    """The SpellSpace door purges only its own lifetimes."""
    meld, _space, _owner, spellbook = _make_spellspace_meld()
    spell = _managed_spell(ConduitCreations(conduit_id="owner"))
    _seed_spell(spellbook, spell)
    with pytest.raises(RuntimeError, match="purge it from its authorized conduit"):
        meld.purge("managed-sid")


def test_meld_existing_spell_refuses_a_managed_spell() -> None:
    """There is no single stored object to return for a pool."""
    meld, _creations, spellbook = _make_conduit_meld()
    spell = _managed_spell(ConduitCreations(conduit_id="owner"))
    _seed_spell(spellbook, spell)
    with pytest.raises(RuntimeError, match="unsupported for existence 'managed_spell_quantity'"):
        meld.meld_existing_spell(spell="managed-sid")


def test_conduit_probe_reports_the_owner_pool() -> None:
    """Live while the pool's objects are alive; the count is idle plus out."""
    meld, _creations, spellbook = _make_conduit_meld(conduit_id="caller")
    owner_creations = ConduitCreations(conduit_id="owner")
    spell = _managed_spell(owner_creations)
    _with_objects(owner_creations, spell, idle=1, out=2)
    _seed_spell(spellbook, spell)
    assert meld.describe_live_creation_status(spell="managed-sid") == {
        "is_live": True,
        "spell_id": "managed-sid",
        "spell_name": "Spell",
        "existence": "managed_spell_quantity",
        "query_conduit_id": "caller",
        "storage_scope_kind": "managed_pool",
        "storage_owner_conduit_id": "owner",
        "active_spellspace_id": None,
        "creation_count": 3,
    }
    assert meld.has_live_creation(spell="managed-sid") is True


def test_conduit_probe_reports_an_empty_pool_as_not_live() -> None:
    """A pool that built nothing yet is not live."""
    meld, _creations, spellbook = _make_conduit_meld(conduit_id="caller")
    owner_creations = ConduitCreations(conduit_id="owner")
    spell = _managed_spell(owner_creations)
    owner_creations.ensure_managed_quantity(spell)
    _seed_spell(spellbook, spell)
    status = meld.describe_live_creation_status(spell="managed-sid")
    assert (status["is_live"], status["creation_count"], status["storage_scope_kind"]) == (False, 0, "managed_pool")


def test_conduit_probe_of_an_unstamped_managed_spell_is_not_live() -> None:
    """A version with no owner store (never stamped; since 0.2.8248 only after a stamp that raised) has no pool."""
    meld, _creations, spellbook = _make_conduit_meld(conduit_id="caller")
    spell = _managed_spell(None, owner_conduit_id=None)
    _seed_spell(spellbook, spell)
    status = meld.describe_live_creation_status(spell="managed-sid")
    assert (status["is_live"], status["creation_count"], status["storage_owner_conduit_id"]) == (False, 0, None)


def test_spellspace_probe_reports_the_owner_pool() -> None:
    """The SpellSpace door reads the same pool: managed objects are root-owned, never space-local."""
    meld, _space, _owner, spellbook = _make_spellspace_meld()
    owner_creations = ConduitCreations(conduit_id="owner")
    spell = _managed_spell(owner_creations)
    _with_objects(owner_creations, spell, idle=0, out=1)
    _seed_spell(spellbook, spell)
    assert meld.describe_live_creation_status(spell="managed-sid") == {
        "is_live": True,
        "spell_id": "managed-sid",
        "spell_name": "Spell",
        "existence": "managed_spell_quantity",
        "query_conduit_id": "conduit-1",
        "storage_scope_kind": "managed_pool",
        "storage_owner_conduit_id": "owner",
        "active_spellspace_id": None,
        "creation_count": 1,
    }


def test_spellspace_probe_of_an_empty_pool_is_not_live() -> None:
    """No object built, not live, from the SpellSpace door too."""
    meld, _space, _owner, spellbook = _make_spellspace_meld()
    owner_creations = ConduitCreations(conduit_id="owner")
    spell = _managed_spell(owner_creations)
    owner_creations.ensure_managed_quantity(spell)
    _seed_spell(spellbook, spell)
    assert meld.has_live_creation(spell="managed-sid") is False
