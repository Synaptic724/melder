from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Optional, Union

from melder.aether.conduit.creations.cluster_creations import ClusterCreations
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool
from melder.aether.conduit.spell_space.spell_space_thread_state import (
    SpellSpaceThreadState,
)


class _ConduitCreationsStub:
    """Minimal conduit-owned creations stub for direct SpellSpacePool tests."""

    def __init__(self, *, owner_conduit_id: str) -> None:
        """Initialize the stub with owner identity and empty state."""
        self._owner_conduit_id = owner_conduit_id
        self._creations: dict[str, Any] = {}
        # Mirror ConduitCreations: a conduit's creations is its own lineage root.
        self._root_creations = self

    @property
    def owner_conduit_id(self) -> str:
        """Return the stable owner conduit id."""
        return self._owner_conduit_id


class _ConduitMeldStub:
    """Minimal conduit-facing meld stub for direct SpellSpacePool tests."""

    def __init__(self, *, meld_result: Any = None) -> None:
        """Initialize the stub with an optional meld result."""
        self._meld_result = meld_result
        self._meld_calls: list[dict[str, Any]] = []
        self._spellbook = SimpleNamespace(
            _spells={},
            _contracted_spells={},
            _spells_by_id={},
            _contracted_spells_by_id={},
            _spell_id_pool={},
            _lookup_spells={},
            _lookup_contracted_spells={},
        )
        self._conduit_id = "conduit-test"
        self._resolution_conduit_id = "conduit-test"
        self._dynamic_environment = False
        self._meld_hooks: dict[str, list[Any]] = {}
        self._root_creations = _ConduitCreationsStub(owner_conduit_id="conduit-test")
        self._cluster_creations = ClusterCreations()

    def meld(
            self,
            spell: Optional[Union[str, object]] = None,
            *,
            spell_name: Optional[str] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[Union[dict, list, tuple]] = None,
    ) -> Any:
        """Record meld call arguments and return the configured result."""
        self._meld_calls.append(
            {
                "spell_name": spell_name,
                "spell": spell,
                "spellframe": spellframe,
                "binding_name": binding_name,
                "spell_override": spell_override,
            }
        )
        return self._meld_result


def test_spellspace_pool_create_object_binds_fixed_runtime_collaborators() -> None:
    """create_object should build a spellspace with the pool's fixed collaborators."""
    owner_conduit_id = "conduit-test"
    creations = _ConduitCreationsStub(owner_conduit_id=owner_conduit_id)
    conduit_meld = _ConduitMeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld,
        owner_conduit_creations=creations,
        spellspace_registry=registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )

    space = pool.create_object()

    assert space.owner_conduit_id == owner_conduit_id
    assert space._owner_conduit_creations is creations
    assert space._meld._owner_conduit_creations is creations
    assert space._meld._spellbook is conduit_meld._spellbook
    assert space._meld._conduit_id == conduit_meld._conduit_id
    assert space._creations.owner_conduit_id == owner_conduit_id
    assert space._creations.id == space.id
    assert space._spellspace_registry is registry
    assert space._spellspace_pool is pool


def test_spellspace_pool_prepare_object_readds_spellspace_to_registry() -> None:
    """prepare_object should reactivate an idle spellspace in the registry."""
    owner_conduit_id = "conduit-test"
    creations = _ConduitCreationsStub(owner_conduit_id=owner_conduit_id)
    conduit_meld = _ConduitMeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld,
        owner_conduit_creations=creations,
        spellspace_registry=registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.create_object()

    registry.discard(space)
    prepared = pool.prepare_object(space)

    assert prepared is space
    assert space in registry


def test_spellspace_pool_acquire_untracked_skips_registry_reactivation() -> None:
    """acquire_untracked should reuse a spellspace without re-adding it to the registry."""
    owner_conduit_id = "conduit-test"
    creations = _ConduitCreationsStub(owner_conduit_id=owner_conduit_id)
    conduit_meld = _ConduitMeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld,
        owner_conduit_creations=creations,
        spellspace_registry=registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )
    first = pool.acquire()
    first.cleanup()

    acquired = pool.acquire_untracked()

    assert acquired is first
    assert acquired not in registry


def test_spellspace_pool_destroy_object_uses_permanent_cleanup() -> None:
    """destroy_object should permanently clean a spellspace."""
    owner_conduit_id = "conduit-test"
    creations = _ConduitCreationsStub(owner_conduit_id=owner_conduit_id)
    conduit_meld = _ConduitMeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld,
        owner_conduit_creations=creations,
        spellspace_registry=registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire()

    pool.destroy_object(space)

    assert space.cleaned is True
    assert registry == set()
    assert not hasattr(space, "_creations")
    assert not hasattr(space, "_owner_conduit_creations")


def test_spellspace_pool_cleanup_destroys_idle_spellspaces() -> None:
    """pool cleanup should permanently clean retained idle spellspaces."""
    owner_conduit_id = "conduit-test"
    creations = _ConduitCreationsStub(owner_conduit_id=owner_conduit_id)
    conduit_meld = _ConduitMeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld,
        owner_conduit_creations=creations,
        spellspace_registry=registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire()
    space_id = space.id
    space.cleanup()

    pool.cleanup()

    assert space.cleaned is True
    assert registry == set()
    assert not hasattr(space, "_creations")
    assert not hasattr(space, "_owner_conduit_creations")
    assert space.id == space_id
