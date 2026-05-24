from __future__ import annotations

from typing import Any, Optional, Union

from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool


class _CreationsStub:
    """Minimal creations stub for direct SpellSpacePool tests."""

    def __init__(self, *, owner_conduit_id: str) -> None:
        """Initialize the stub with owner identity and empty state."""
        self._owner_conduit_id = owner_conduit_id
        self.cleared_ids: list[str] = []
        self._active_spellspace: Optional[SpellSpace] = None

    def get_active_spellspace(self) -> Optional[SpellSpace]:
        """Return the currently active spellspace."""
        return self._active_spellspace

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """Record the cleared spellspace id."""
        self.cleared_ids.append(spellspace_id)


class _MeldStub:
    """Minimal meld stub for direct SpellSpacePool tests."""

    def __init__(self, *, meld_result: Any = None) -> None:
        """Initialize the stub with an optional meld result."""
        self._meld_result = meld_result
        self._meld_calls: list[dict[str, Any]] = []

    def meld(
            self,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[Union[str, object]] = None,
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
    creations = _CreationsStub(owner_conduit_id=owner_conduit_id)
    meld = _MeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        meld=meld,
        creations=creations,
        spellspace_registry=registry,
        baseline_idle=1,
        max_idle=1,
    )

    space = pool.create_object()

    assert space.owner_conduit_id == owner_conduit_id
    assert space._meld is meld
    assert space._creations is creations
    assert space._spellspace_registry is registry
    assert space._spellspace_pool is pool


def test_spellspace_pool_prepare_object_readds_spellspace_to_registry() -> None:
    """prepare_object should reactivate an idle spellspace in the registry."""
    owner_conduit_id = "conduit-test"
    creations = _CreationsStub(owner_conduit_id=owner_conduit_id)
    meld = _MeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        meld=meld,
        creations=creations,
        spellspace_registry=registry,
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.create_object()

    registry.discard(space)
    prepared = pool.prepare_object(space)

    assert prepared is space
    assert space in registry


def test_spellspace_pool_destroy_object_uses_permanent_cleanup() -> None:
    """destroy_object should permanently clean a spellspace."""
    owner_conduit_id = "conduit-test"
    creations = _CreationsStub(owner_conduit_id=owner_conduit_id)
    meld = _MeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        meld=meld,
        creations=creations,
        spellspace_registry=registry,
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire()

    pool.destroy_object(space)

    assert space.cleaned is True
    assert registry == set()
    assert creations.cleared_ids == [space.id]


def test_spellspace_pool_cleanup_destroys_idle_spellspaces() -> None:
    """pool cleanup should permanently clean retained idle spellspaces."""
    owner_conduit_id = "conduit-test"
    creations = _CreationsStub(owner_conduit_id=owner_conduit_id)
    meld = _MeldStub()
    registry: set[SpellSpace] = set()
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        meld=meld,
        creations=creations,
        spellspace_registry=registry,
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire()
    space_id = space.id
    space.cleanup()

    pool.cleanup()

    assert space.cleaned is True
    assert registry == set()
    assert creations.cleared_ids == [space_id, space_id]
