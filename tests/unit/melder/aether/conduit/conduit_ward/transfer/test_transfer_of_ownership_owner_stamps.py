"""
Unit tests: the owner stamp follows a lineage through an ownership transfer (STORY-2026-10-15-managed_ownership_transfer).

Scope:
    `TransferOfOwnership` stamps the active member onto the target through `_restamp` and re-stamps every moved
    parked member that carries a stamp; each stamp registers the rollback that stamps the member back onto the source
    and, for a managed version whose pool the stamp composed in the target store, the rollback that discards exactly
    that pool. Rows (`_move_creations`, `_teardown_creations` and their rollbacks) are unchanged.

    The fakes come from test_transfer_of_ownership.py; this file adds a store with a pool map and `managed` rows and a
    spell whose `_add_owned_conduit` writes the stamp the real one writes and composes the pool for a managed version.
"""
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import pytest

from melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership import TransferOfOwnership
from melder.aether.spellbook.existence.existence import Existence
from tests.unit.melder.aether.conduit.conduit_ward.transfer.test_transfer_of_ownership import (
    DEFAULT_SPELL_ID,
    SOURCE_ID,
    TARGET_ID,
    FakeCreations,
    build_environment,
    build_spell,
)

LogEntry = Tuple[str, str, str]


class _FakePool:
    """A pool stand-in: the identity a stamp composes and the cleanup a rollback calls."""

    def __init__(self, spell_id: str) -> None:
        """
        Keep the id; not cleaned.

        Args:
            spell_id: The version the pool serves.
        """
        self.spell_id = spell_id
        self.cleaned = False

    def cleanup(self) -> None:
        """Mark the pool cleaned."""
        self.cleaned = True


class _ManagedCreations(FakeCreations):
    """FakeCreations plus the pool map: ensure (a stamp), get, discard and `managed` rows on extract and restore."""

    def __init__(self, name: str, log: List[LogEntry]) -> None:
        """
        Start empty.

        Args:
            name: "source" or "target", written to the log.
            log: The shared ordered log.
        """
        super().__init__()
        self.name = name
        self.log = log
        self.pools: Dict[str, _FakePool] = {}

    def ensure_managed_quantity(self, spell: Any) -> _FakePool:
        """Return the version's pool, composing it on first use (what a stamp of a managed version does)."""
        pool = self.pools.get(spell.spell_id)
        if pool is None:
            pool = _FakePool(spell.spell_id)
            self.pools[spell.spell_id] = pool
            self.log.append(("compose", self.name, spell.spell_id))
        return pool

    def get_managed_quantity(self, spell_id: str) -> Optional[_FakePool]:
        """Return the pool under the id, or None."""
        return self.pools.get(spell_id)

    def discard_managed_quantity(self, spell_id: str, pool: _FakePool) -> bool:
        """Remove the pool when it is the one under the id (identity); report whether it was removed."""
        if self.pools.get(spell_id) is not pool:
            self.log.append(("discard-miss", self.name, spell_id))
            return False
        del self.pools[spell_id]
        self.log.append(("discard", self.name, spell_id))
        return True

    def extract_spell_creations(self, spell_id: str) -> List[Any]:
        """Extract the plain rows and the pool as a `managed` row."""
        rows = list(super().extract_spell_creations(spell_id))
        pool = self.pools.pop(spell_id, None)
        if pool is not None:
            rows.append({"scope": "managed", "stored": pool})
        self.log.append(("extract", self.name, spell_id))
        return rows

    def restore_spell_creations(self, spell_id: str, extracted: List[Any]) -> None:
        """Restore the rows; a `managed` row replaces a different pool, which is cleaned (as the real restore)."""
        plain: List[Any] = []
        for row in extracted:
            if isinstance(row, dict) and row.get("scope") == "managed":
                replaced = self.pools.get(spell_id)
                if replaced is not None and replaced is not row["stored"]:
                    replaced.cleanup()
                self.pools[spell_id] = row["stored"]
            else:
                plain.append(row)
        super().restore_spell_creations(spell_id, plain)
        self.log.append(("restore", self.name, spell_id))


def _stamper(spell: SimpleNamespace, log: List[LogEntry]) -> Any:
    """
    Return an `_add_owned_conduit` for the fake spell that writes what the real one writes.

    Args:
        spell: The fake spell.
        log: The shared ordered log ("stamp", spell id, conduit id).

    Returns:
        Callable: The stamping function.
    """

    def _add_owned_conduit(
            conduit_id: str,
            conduit_name: Optional[str] = None,
            creations: Any = None,
            *,
            dynamic_environment: bool,
            creation_gate_controller: Any,
            caching_enabled: bool,
    ) -> None:
        log.append(("stamp", spell.spell_id, conduit_id))
        spell._owner_conduit_id = conduit_id
        spell._owner_conduit_name = conduit_name
        spell._owner_creations = creations
        spell._dynamic_environment = dynamic_environment
        spell._creation_gate_controller = creation_gate_controller
        spell._caching_enabled = caching_enabled
        if spell.existence is Existence.managed_spell_quantity and creations is not None:
            creations.ensure_managed_quantity(spell)

    return _add_owned_conduit


def _parked_id(number: int) -> str:
    """The id of the parked version `number` (1-based)."""
    return f"{DEFAULT_SPELL_ID}-v{number + 1}"


def _stamp_with(spell: SimpleNamespace, conduit: Any) -> None:
    """Stamp a fake spell with a fake root the way conjure does."""
    spell._add_owned_conduit(
        conduit._id,
        conduit._name,
        conduit._creations,
        dynamic_environment=True,
        creation_gate_controller=conduit._creation_gate_controller,
        caching_enabled=True,
    )


def _environment(
        *,
        existence: Existence = Existence.managed_spell_quantity,
        parked: int = 0,
        parked_stamped: bool = True,
        target_holds: Tuple[str, ...] = (),
) -> SimpleNamespace:
    """
    A transfer harness: the active member and `parked` parked members, stamped by the source like conjure stamps.

    Args:
        existence: Every member's Existence.
        parked: How many parked members the index holds.
        parked_stamped: Whether the parked members carry the source's stamp (False: never stamped - before 0.2.8248
            a version staged before conjure, since then one whose stamp raised at conjure).
        target_holds: The spell_ids the target store already holds a pool for.

    Returns:
        SimpleNamespace: build_environment's fields plus `log`, `parked` and the two stores.
    """
    log: List[LogEntry] = []
    env = build_environment()
    source_store = _ManagedCreations("source", log)
    target_store = _ManagedCreations("target", log)
    env.source._creations = source_store
    env.target._creations = target_store
    env.source_creations = source_store
    env.target_creations = target_store
    for book in (env.source._spellbook, env.target._spellbook):
        book._inactive_spells = {}
        book._spell_ids = set()
    env.spell.existence = existence
    env.spell._add_owned_conduit = _stamper(env.spell, log)
    _stamp_with(env.spell, env.source)
    env.parked = []
    for number in range(1, parked + 1):
        member = build_spell(spell_id=_parked_id(number), owner_id=SOURCE_ID, spell_index=env.spell_index,
                             existence=existence)
        member._add_owned_conduit = _stamper(member, log)
        member._spellbook = env.source._spellbook
        member._spell_system_states = env.states_system
        env.spell_index.add_member(member.spell_id)
        env.source._spellbook._inactive_spells[member.spell_id] = member
        env.source._spellbook._spell_ids.add(member.spell_id)
        if parked_stamped:
            _stamp_with(member, env.source)
        env.parked.append(member)
    for spell_id in target_holds:
        target_store.pools[spell_id] = _FakePool(spell_id)
    log.clear()
    env.log = log
    return env


def _transfer(env: SimpleNamespace, *, move: bool = True) -> TransferOfOwnership:
    """A transfer of the harness's lineage from the source to the target."""
    return TransferOfOwnership(
        source_conduit=env.source,
        target_conduit=env.target,
        spell=env.spell,
        move_creations=move,
    )


def _fail_after_the_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every transfer fail at its impact gating, after its rows moved."""

    def boom(self: TransferOfOwnership, **kwargs: Any) -> None:
        raise RuntimeError("forced failure after the rows")

    monkeypatch.setattr(TransferOfOwnership, "_gate_transfer_impacts", boom)


def test_the_flip_stamps_the_active_member_onto_the_target_store() -> None:
    """Owner id, name and store are the target's, and the target store holds the version's pool."""
    env = _environment()
    _transfer(env)._flip_registry_and_spellbooks(env.spell)
    assert env.spell._owner_creations is env.target._creations
    assert env.spell._owner_conduit_id == TARGET_ID
    assert env.target._creations.get_managed_quantity(DEFAULT_SPELL_ID) is not None


def test_the_stamp_carries_the_owner_root_gate_controller_and_its_books_caching_posture(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The flip stamps with the target's gate controller and caching posture; the rollback with the source's."""
    env = _environment()
    monkeypatch.setattr(env.target._spellbook, "_resolve_system_caching_enabled", lambda: False)
    transfer = _transfer(env)
    transfer._flip_registry_and_spellbooks(env.spell)
    assert env.spell._creation_gate_controller is env.target._creation_gate_controller
    assert env.spell._caching_enabled is False
    transfer._rollback()
    assert env.spell._creation_gate_controller is env.source._creation_gate_controller
    assert env.spell._caching_enabled is True


def test_a_rollback_after_the_flip_stamps_the_active_member_back_onto_the_source() -> None:
    """The member names the source's store again, and the source's pool is the one it had."""
    env = _environment()
    source_pool = env.source._creations.get_managed_quantity(DEFAULT_SPELL_ID)
    transfer = _transfer(env)
    transfer._flip_registry_and_spellbooks(env.spell)
    transfer._rollback()
    assert env.spell._owner_creations is env.source._creations
    assert env.spell._owner_conduit_id == SOURCE_ID
    assert env.source._creations.get_managed_quantity(DEFAULT_SPELL_ID) is source_pool
    assert not source_pool.cleaned


def test_a_rollback_after_the_flip_discards_and_cleans_the_pool_the_stamp_composed() -> None:
    """The pool the target's stamp composed leaves the target store and is cleaned."""
    env = _environment()
    transfer = _transfer(env)
    transfer._flip_registry_and_spellbooks(env.spell)
    composed = env.target._creations.get_managed_quantity(DEFAULT_SPELL_ID)
    transfer._rollback()
    assert env.target._creations.get_managed_quantity(DEFAULT_SPELL_ID) is None
    assert composed is not None and composed.cleaned


def test_a_rollback_after_the_flip_keeps_a_pool_the_target_already_held() -> None:
    """A pool the target held before the stamp is never discarded or cleaned."""
    env = _environment(target_holds=(DEFAULT_SPELL_ID,))
    held = env.target._creations.get_managed_quantity(DEFAULT_SPELL_ID)
    transfer = _transfer(env)
    transfer._flip_registry_and_spellbooks(env.spell)
    transfer._rollback()
    assert env.target._creations.get_managed_quantity(DEFAULT_SPELL_ID) is held
    assert held is not None and not held.cleaned
    assert not [entry for entry in env.log if entry[0].startswith("discard")]


def test_a_rollback_after_the_flip_stamps_back_a_non_managed_member_without_a_discard() -> None:
    """A `unique` member is stamped back onto the source; no pool is composed or discarded."""
    env = _environment(existence=Existence.unique)
    transfer = _transfer(env)
    transfer._flip_registry_and_spellbooks(env.spell)
    assert env.spell._owner_creations is env.target._creations
    transfer._rollback()
    assert env.spell._owner_creations is env.source._creations
    assert not [entry for entry in env.log if entry[0] in ("compose", "discard", "discard-miss")]


def test_a_stamp_that_raises_is_still_stamped_back_and_its_pool_discarded() -> None:
    """The stamp-back is registered before the stamp and the discard after it even when it raised."""
    env = _environment()
    stamp = env.spell._add_owned_conduit

    def failing(conduit_id: str, conduit_name: Optional[str] = None, creations: Any = None, **kwargs: Any) -> None:
        stamp(conduit_id, conduit_name, creations, **kwargs)
        if conduit_id == TARGET_ID:
            raise RuntimeError("stamp failed after composing the pool")

    env.spell._add_owned_conduit = failing
    transfer = _transfer(env)
    with pytest.raises(RuntimeError, match="Failed to flip spellbooks"):
        transfer._flip_registry_and_spellbooks(env.spell)
    composed = env.target._creations.get_managed_quantity(DEFAULT_SPELL_ID)
    transfer._rollback()
    assert env.spell._owner_creations is env.source._creations
    assert env.target._creations.get_managed_quantity(DEFAULT_SPELL_ID) is None
    assert composed is not None and composed.cleaned


def test_migrate_restamps_a_stamped_parked_member_onto_the_target() -> None:
    """The parked member names the target's store, and the target store holds its version's pool."""
    env = _environment(parked=1)
    member = env.parked[0]
    _transfer(env)._migrate_inactive_members(env.spell)
    assert member._owner_creations is env.target._creations
    assert member._owner_conduit_id == TARGET_ID
    assert env.target._creations.get_managed_quantity(member.spell_id) is not None
    assert member.spell_id in env.target._spellbook._inactive_spells


def test_migrate_leaves_a_parked_member_staged_before_conjure_unstamped() -> None:
    """A member that never carried a stamp moves as before: maps and owner id, no store, no pool."""
    env = _environment(parked=1, parked_stamped=False)
    member = env.parked[0]
    _transfer(env)._migrate_inactive_members(env.spell)
    assert member._owner_creations is None
    assert member._owner_conduit_id == TARGET_ID
    assert env.target._creations.get_managed_quantity(member.spell_id) is None
    assert not [entry for entry in env.log if entry[0] == "stamp"]


def test_migrate_restamps_parked_members_of_every_existence() -> None:
    """`unique` parked members are stamped onto the target's store too; nothing composes a pool for them."""
    env = _environment(existence=Existence.unique, parked=2)
    _transfer(env)._migrate_inactive_members(env.spell)
    assert all(member._owner_creations is env.target._creations for member in env.parked)
    assert not [entry for entry in env.log if entry[0] == "compose"]


def test_a_rollback_after_migrate_stamps_parked_members_back_onto_the_source() -> None:
    """Every re-stamped parked member names the source's store again and is back in the source Book."""
    env = _environment(parked=2)
    transfer = _transfer(env)
    transfer._migrate_inactive_members(env.spell)
    transfer._rollback()
    assert all(member._owner_creations is env.source._creations for member in env.parked)
    assert all(member._owner_conduit_id == SOURCE_ID for member in env.parked)
    assert set(env.source._spellbook._inactive_spells) == {member.spell_id for member in env.parked}
    assert env.target._spellbook._inactive_spells == {}


def test_a_rollback_after_migrate_discards_the_parked_pools_the_stamps_composed() -> None:
    """The composed target pools are discarded and cleaned; the source's parked pools are untouched."""
    env = _environment(parked=2)
    source_pools = [env.source._creations.get_managed_quantity(member.spell_id) for member in env.parked]
    transfer = _transfer(env)
    transfer._migrate_inactive_members(env.spell)
    composed = [env.target._creations.get_managed_quantity(member.spell_id) for member in env.parked]
    transfer._rollback()
    assert all(env.target._creations.get_managed_quantity(member.spell_id) is None for member in env.parked)
    assert all(pool is not None and pool.cleaned for pool in composed)
    assert [env.source._creations.get_managed_quantity(m.spell_id) for m in env.parked] == source_pools
    assert not any(pool.cleaned for pool in source_pools)


def test_a_rollback_after_migrate_keeps_a_parked_pool_the_target_already_held() -> None:
    """A parked version's pool the target held before the stamp stays in the target, uncleaned."""
    env = _environment(parked=1, target_holds=(_parked_id(1),))
    held = env.target._creations.get_managed_quantity(_parked_id(1))
    transfer = _transfer(env)
    transfer._migrate_inactive_members(env.spell)
    transfer._rollback()
    assert env.target._creations.get_managed_quantity(_parked_id(1)) is held
    assert held is not None and not held.cleaned
    assert env.parked[0]._owner_creations is env.source._creations


def test_a_parked_stamp_that_raises_is_rolled_back_with_the_members_before_it() -> None:
    """The second member's stamp raises: both members are stamped back and both composed pools discarded."""
    env = _environment(parked=2)
    second = env.parked[1]
    stamp = second._add_owned_conduit

    def failing(conduit_id: str, conduit_name: Optional[str] = None, creations: Any = None, **kwargs: Any) -> None:
        stamp(conduit_id, conduit_name, creations, **kwargs)
        if conduit_id == TARGET_ID:
            raise RuntimeError("parked stamp failed")

    second._add_owned_conduit = failing
    transfer = _transfer(env)
    with pytest.raises(RuntimeError, match="parked stamp failed"):
        transfer._migrate_inactive_members(env.spell)
    transfer._rollback()
    assert all(member._owner_creations is env.source._creations for member in env.parked)
    assert all(env.target._creations.get_managed_quantity(member.spell_id) is None for member in env.parked)


def test_a_successful_move_leaves_every_stamp_and_pool_on_the_target() -> None:
    """After a move every stamped member names the target's store, which holds the source's pools."""
    env = _environment(parked=1)
    source_pools = {sid: env.source._creations.get_managed_quantity(sid) for sid in (DEFAULT_SPELL_ID, _parked_id(1))}
    _transfer(env).execute()
    assert env.spell._owner_creations is env.target._creations
    assert env.parked[0]._owner_creations is env.target._creations
    for spell_id, pool in source_pools.items():
        assert env.target._creations.get_managed_quantity(spell_id) is pool
        assert env.source._creations.get_managed_quantity(spell_id) is None
        assert pool is not None and not pool.cleaned


def test_a_successful_transfer_without_a_move_gives_the_parked_member_a_fresh_target_pool() -> None:
    """No move: the parked member names the target's store and its fresh pool; the source keeps its old one."""
    env = _environment(parked=1)
    old_parked = env.source._creations.get_managed_quantity(_parked_id(1))
    _transfer(env, move=False).execute()
    fresh = env.target._creations.get_managed_quantity(_parked_id(1))
    assert env.parked[0]._owner_creations is env.target._creations
    assert fresh is not None and fresh is not old_parked
    assert env.source._creations.get_managed_quantity(_parked_id(1)) is old_parked
    assert old_parked is not None and not old_parked.cleaned


def test_a_failed_move_leaves_every_stamp_and_pool_with_the_source(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rows and stamps go back: the source holds its own pool objects, uncleaned; the target holds none."""
    env = _environment(parked=1)
    source_pools = {sid: env.source._creations.get_managed_quantity(sid) for sid in (DEFAULT_SPELL_ID, _parked_id(1))}
    _fail_after_the_rows(monkeypatch)
    with pytest.raises(RuntimeError, match="forced failure after the rows"):
        _transfer(env).execute()
    assert env.spell._owner_creations is env.source._creations
    assert env.parked[0]._owner_creations is env.source._creations
    for spell_id, pool in source_pools.items():
        assert env.source._creations.get_managed_quantity(spell_id) is pool
        assert env.target._creations.get_managed_quantity(spell_id) is None
        assert pool is not None and not pool.cleaned


def test_a_failed_transfer_without_a_move_discards_the_composed_pools(monkeypatch: pytest.MonkeyPatch) -> None:
    """No move: the composed target pools (active and parked) are discarded and cleaned; the source's stay."""
    env = _environment(parked=1)
    source_pools = {sid: env.source._creations.get_managed_quantity(sid) for sid in (DEFAULT_SPELL_ID, _parked_id(1))}
    _fail_after_the_rows(monkeypatch)
    transfer = _transfer(env, move=False)
    with pytest.raises(RuntimeError, match="forced failure after the rows"):
        transfer.execute()
    discarded = [entry for entry in env.log if entry[0] == "discard"]
    assert sorted(discarded) == sorted([("discard", "target", DEFAULT_SPELL_ID), ("discard", "target", _parked_id(1))])
    for spell_id, pool in source_pools.items():
        assert env.source._creations.get_managed_quantity(spell_id) is pool
        assert env.target._creations.get_managed_quantity(spell_id) is None
        assert pool is not None and not pool.cleaned
    assert env.spell._owner_creations is env.source._creations


def test_a_failed_move_puts_the_rows_back_before_stamping_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rollback order: each member's rows return to the source before its stamp-back runs."""
    env = _environment(parked=1)
    _fail_after_the_rows(monkeypatch)
    with pytest.raises(RuntimeError, match="forced failure after the rows"):
        _transfer(env).execute()
    for spell_id in (DEFAULT_SPELL_ID, _parked_id(1)):
        restored = max(i for i, entry in enumerate(env.log) if entry == ("restore", "source", spell_id))
        stamped_back = max(i for i, entry in enumerate(env.log) if entry == ("stamp", spell_id, SOURCE_ID))
        assert restored < stamped_back
    stamp_backs = [entry for entry in env.log if entry[0] == "stamp" and entry[2] == SOURCE_ID]
    assert stamp_backs[-1] == ("stamp", DEFAULT_SPELL_ID, SOURCE_ID)
