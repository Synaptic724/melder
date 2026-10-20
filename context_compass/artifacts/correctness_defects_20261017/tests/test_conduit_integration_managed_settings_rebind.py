"""
Integration: a managed spell's settings are not part of its spell_id
(STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool, part A).

Through a real dynamic Spellbook and its root conduit, so `cleanup_spell` and a late `bind` run on a live root: one
class bound managed at one address is one spell whatever its mode, limit, queue timeout or reset names (owner ruling,
2026-10-17: "the bind call itself shouldn't impact the actual SHA256"). Staging it again with only other settings is
refused as the same spell, with nothing changed. Changing its settings is `cleanup_spell`, then `bind`, which keeps the
spell_id and the pool: the pool takes the new settings, keeps every object alive and counted, and an object leased
before the change goes back to it. Run under `-X gil=0` and `-X gil=1`.
"""
from collections.abc import Iterator
from typing import Any, Dict, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity
from melder.aether.conduit.creations.release_managed_spell import ReleaseManagedSpell
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.utilities.custom_exceptions.managed_spell_exhausted_error import ManagedSpellExhaustedError
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration

pytestmark = pytest.mark.integration


class Anchor:
    """A plain unique binding so the root has an ordinary spell beside the managed one."""


class Worker:
    """The managed class: a disposal method that logs through the class."""

    log: List[str] = []

    def close(self) -> None:
        """Record one disposal."""
        Worker.log.append("close")


def _reset_aether() -> None:
    """Install a fresh Aether (and with it a fresh release registry) for Spellbook and Conduit."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def fresh_aether() -> Iterator[None]:
    """A fresh Aether and an empty log per test."""
    _reset_aether()
    Worker.log = []
    yield
    _reset_aether()


def _options(**settings: Any) -> Dict[str, Any]:
    """
    Bind options of Worker at its one address, with `settings` as its managed settings.

    Args:
        **settings: Managed bind options (mode, limit, timeout, reset names).

    Returns:
        Dict[str, Any]: Keyword arguments for `bind` and `bind_inactive`.
    """
    return dict(
        spell=Worker, spellframe="workers", binding_name="worker", existence=Existence.managed_spell_quantity,
        permissions="create", disposal_method_names=["close"], **settings,
    )


def _dynamic_root(**settings: Any) -> Tuple[Spellbook, Conduit, str]:
    """
    A conjured dynamic root with Anchor and Worker bound managed.

    Args:
        **settings: Worker's managed settings.

    Returns:
        Tuple[Spellbook, Conduit, str]: The Book, its root and Worker's spell_id.
    """
    configuration = SpellbookConfiguration(aether_frame="default")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(aetheric_frame="default", configuration=configuration)
    book.bind(spell=Anchor, existence=Existence.unique, permissions="create")
    spell_id = book.bind(**_options(**settings))
    root = book.conjure(dynamic=True, name="managed-settings")
    return book, root, spell_id


def _pool_of(root: Conduit, spell_id: str) -> ManagedSpellQuantity:
    """
    Return the pool the root's store holds for Worker.

    Args:
        root: The owning root.
        spell_id: Worker's spell_id.

    Returns:
        ManagedSpellQuantity: The pool.
    """
    pool = root._creations.get_managed_quantity(spell_id)
    assert pool is not None
    return pool


def _pooled_spell_ids() -> List[str]:
    """Return the spell_id of every pool of Worker the release registry holds."""
    return [entry["spell_id"] for entry in ReleaseManagedSpell().describe(Worker)]


def test_restaging_a_settings_only_version_is_refused_as_the_same_spell() -> None:
    """Worker limit 1 is active; Worker limit 2 on its index is the same spell: refused, and nothing changes."""
    book, root, spell_id = _dynamic_root(managed_spell_mode="limited_quantity", managed_spell_limit=1)
    try:
        spell = book.find_spell_by_spell_id(spell_id)
        index = spell.spell_index
        with pytest.raises(RuntimeError, match="Spell ID collision detected"):
            root.bind_inactive(
                spell_index=index, **_options(managed_spell_mode="limited_quantity", managed_spell_limit=2),
            )
        assert index.spells_in_index() == {spell_id}
        assert book.find_spell_by_spell_id(spell_id) is spell
        pool = _pool_of(root, spell_id)
        assert (pool.limit, pool.spell) == (1, spell)
        assert _pooled_spell_ids() == [spell_id]
    finally:
        root.cleanup()
        book.cleanup()


def test_rebinding_with_new_managed_settings_recomposes_its_pool() -> None:
    """cleanup_spell, then bind with limit 2: one spell_id and pool; it leases up to 2; the first object goes back."""
    book, root, spell_id = _dynamic_root(managed_spell_mode="limited_quantity", managed_spell_limit=1)
    try:
        first = root.meld(spell_id=spell_id)
        pool = _pool_of(root, spell_id)
        root.cleanup_spell(spell=book.find_spell_by_spell_id(spell_id))
        assert root.bind(**_options(managed_spell_mode="limited_quantity", managed_spell_limit=2)) == spell_id
        assert _pool_of(root, spell_id) is pool
        assert (pool.limit, pool.count) == (2, 1)
        second = root.meld(spell_id=spell_id)
        assert second is not first
        assert pool.count == 2
        with pytest.raises(ManagedSpellExhaustedError):
            root.meld(spell_id=spell_id)
        ReleaseManagedSpell().release(first)
        assert (pool.count, pool.idle_count) == (2, 1)
        assert root.meld(spell_id=spell_id) is first
        assert _pooled_spell_ids() == [spell_id]
    finally:
        root.cleanup()
        book.cleanup()


def test_a_mode_change_keeps_every_object_alive_and_counted() -> None:
    """elastic with three idle objects -> limited_quantity limit 1: nothing is destroyed at the rebind."""
    book, root, spell_id = _dynamic_root()
    try:
        objects = [root.meld(spell_id=spell_id) for _ in range(3)]
        for obj in objects:
            ReleaseManagedSpell().release(obj)
        pool = _pool_of(root, spell_id)
        assert (pool.count, pool.idle_count) == (3, 3)
        root.cleanup_spell(spell=book.find_spell_by_spell_id(spell_id))
        assert root.bind(**_options(managed_spell_mode="limited_quantity", managed_spell_limit=1)) == spell_id
        assert (pool.mode.name, pool.limit, pool.count, pool.idle_count, Worker.log) == (
            "limited_quantity", 1, 3, 3, [],
        )
        leased = root.meld(spell_id=spell_id)
        assert leased in objects
        ReleaseManagedSpell().release(leased)
        # The fixed capacity of 1 evicts the oldest idle object on each release above it.
        assert (pool.count, pool.idle_count, Worker.log) == (2, 2, ["close"])
    finally:
        root.cleanup()
        book.cleanup()
