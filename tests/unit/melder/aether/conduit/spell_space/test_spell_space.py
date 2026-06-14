"""tests/aether/conduit/spell_space/test_spell_space.py

Validation: Not run.

These tests target `melder.aether.conduit.spell_space.spell_space.SpellSpace`.
They focus on the current explicit-collaborator constructor, cleanup lanes,
pool reuse behavior, and front-door delegation behavior.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Optional, Union

import pytest

from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool
from melder.aether.conduit.spell_space.spell_space_thread_state import (
    SpellSpaceThreadState,
)


class _ConduitCreationsStub:
    """Minimal conduit-owned creations stub for direct SpellSpace tests."""

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
    """Minimal conduit-facing meld stub for SpellSpace construction."""

    def __init__(self) -> None:
        """Initialize the stub with the shared-core meld attributes."""
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


class _SpellSpaceMeldDelegateStub:
    """Minimal owned meld stub that records `SpellSpace.meld(...)` delegation."""

    def __init__(self, *, meld_result: Any = None) -> None:
        """Initialize the stub with an optional meld result."""
        self._meld_result = meld_result
        self._meld_calls: list[dict[str, Any]] = []

    @property
    def meld_calls(self) -> list[dict[str, Any]]:
        """Return the recorded meld call arguments."""
        return self._meld_calls

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


class _PoolStub:
    """Minimal spellspace pool stub for direct SpellSpace tests."""

    def __init__(self) -> None:
        """Initialize the stub with empty release bookkeeping."""
        self.released_ids: list[str] = []

    def release(self, obj: SpellSpace) -> None:
        """Record one released spellspace id."""
        self.released_ids.append(obj.id)


@pytest.fixture
def owner_conduit_id() -> str:
    """Provide a stable owner conduit id for SpellSpace tests."""
    return "conduit-test"


@pytest.fixture
def owner_conduit_creations_stub(
        owner_conduit_id: str,
) -> _ConduitCreationsStub:
    """Provide a fresh conduit-owned creations stub for SpellSpace tests."""
    return _ConduitCreationsStub(owner_conduit_id=owner_conduit_id)


@pytest.fixture
def conduit_meld_stub() -> _ConduitMeldStub:
    """Provide a fresh conduit-facing meld stub for SpellSpace tests."""
    return _ConduitMeldStub()


@pytest.fixture
def spellspace_registry() -> set[SpellSpace]:
    """Provide a fresh spellspace registry set for SpellSpace tests."""
    return set()


@pytest.fixture
def pool_stub() -> _PoolStub:
    """Provide a fresh direct pool stub for SpellSpace tests."""
    return _PoolStub()


def _build_space(
        *,
        owner_conduit_id: str,
        conduit_meld: _ConduitMeldStub,
        owner_conduit_creations: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
        spellspace_pool: _PoolStub,
        spellspace_stack_state: Optional[SpellSpaceThreadState] = None,
) -> SpellSpace:
    """Build one direct SpellSpace under the current constructor contract.

    A fresh `SpellSpaceThreadState` is supplied by default because the
    constructor requires the injected per-thread stack collaborator; tests
    exercising the managed context-manager lane can pass their own holder to
    observe push/pop behavior.
    """
    return SpellSpace(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld,
        owner_conduit_creations=owner_conduit_creations,
        spellspace_registry=spellspace_registry,
        spellspace_pool=spellspace_pool,
        spellspace_stack_state=(
            spellspace_stack_state
            if spellspace_stack_state is not None
            else SpellSpaceThreadState()
        ),
    )


def test_properties_expose_id_owner_and_current_collaborators(
        owner_conduit_id: str,
        conduit_meld_stub: _ConduitMeldStub,
        owner_conduit_creations_stub: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify SpellSpace exposes stable ids and current collaborator ownership."""
    space = _build_space(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld_stub,
        owner_conduit_creations=owner_conduit_creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )

    first_id = space.id
    assert isinstance(first_id, str)
    assert first_id != ""
    assert space.id == first_id
    assert space.owner_conduit_id == owner_conduit_id
    assert space._owner_conduit_creations is owner_conduit_creations_stub
    assert space._creations.owner_conduit_id == owner_conduit_id
    assert space._creations.id == first_id


def test_cleanup_clears_local_creations_unregisters_and_returns_to_pool(
        owner_conduit_id: str,
        conduit_meld_stub: _ConduitMeldStub,
        owner_conduit_creations_stub: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify normal cleanup clears local creations and returns to the pool."""
    space = _build_space(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld_stub,
        owner_conduit_creations=owner_conduit_creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )
    spellspace_registry.add(space)
    created = object()
    space._creations._creations["spell-id"] = created
    assert space._creations.get_creation("spell-id") is created

    space.cleanup()

    assert space._creations.get_creation("spell-id") is None
    assert pool_stub.released_ids == [space.id]
    assert space not in spellspace_registry
    assert space.cleaned is False


def test_meld_delegates_to_owned_meld_runtime_and_returns_result(
        owner_conduit_id: str,
        conduit_meld_stub: _ConduitMeldStub,
        owner_conduit_creations_stub: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify SpellSpace.meld delegates through the owned front door."""
    space = _build_space(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld_stub,
        owner_conduit_creations=owner_conduit_creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )
    expected = object()
    delegate = _SpellSpaceMeldDelegateStub(meld_result=expected)
    space._meld = delegate

    result = space.meld(
        spell_name="spell-x",
        spell="spell-id",
        spellframe="frame-1",
        binding_name="bind-1",
        spell_override={"k": "v"},
    )

    assert result is expected
    assert delegate.meld_calls == [
        {
            "spell_name": "spell-x",
            "spell": "spell-id",
            "spellframe": "frame-1",
            "binding_name": "bind-1",
            "spell_override": {"k": "v"},
        }
    ]


def test_cleanup_keeps_reusable_spellspace_surface_alive(
        owner_conduit_id: str,
        conduit_meld_stub: _ConduitMeldStub,
        owner_conduit_creations_stub: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify normal cleanup keeps owned collaborators for later pool reuse."""
    space = _build_space(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld_stub,
        owner_conduit_creations=owner_conduit_creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )
    spellspace_registry.add(space)

    space.cleanup()

    assert hasattr(space, "_creations")
    assert hasattr(space, "_meld")
    assert hasattr(space, "_spellspace_pool")
    assert space.cleaned is False


def test_cleanup_returns_spellspace_to_pool(
        owner_conduit_id: str,
        conduit_meld_stub: _ConduitMeldStub,
        owner_conduit_creations_stub: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify normal cleanup returns a pooled spellspace to the idle pool."""
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld_stub,
        owner_conduit_creations=owner_conduit_creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire()
    created = object()
    space._creations._creations["spell-id"] = created
    assert space._creations.get_creation("spell-id") is created

    space.cleanup()

    assert pool.idle_count == 1
    assert space not in spellspace_registry
    assert space._creations.get_creation("spell-id") is None
    assert space.cleaned is False


def test_recycle_from_managed_context_returns_untracked_spellspace_to_pool(
        owner_conduit_id: str,
        conduit_meld_stub: _ConduitMeldStub,
        owner_conduit_creations_stub: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify managed recycle clears local state and returns to the pool."""
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld_stub,
        owner_conduit_creations=owner_conduit_creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire_untracked()
    created = object()
    space._creations._creations["spell-id"] = created
    assert space._creations.get_creation("spell-id") is created

    space.recycle_from_managed_context()

    assert pool.idle_count == 1
    assert space._creations.get_creation("spell-id") is None
    assert space not in spellspace_registry
    assert space.cleaned is False


def test_pool_reuses_spellspace_after_cleanup(
        owner_conduit_id: str,
        conduit_meld_stub: _ConduitMeldStub,
        owner_conduit_creations_stub: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify a pooled spellspace is reused after normal cleanup."""
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld_stub,
        owner_conduit_creations=owner_conduit_creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )
    first = pool.acquire()
    first_id = first.id

    first.cleanup()
    second = pool.acquire()

    assert second is first
    assert second.id == first_id
    assert second.cleaned is False
    assert second in spellspace_registry


def test_permanent_cleanup_bypasses_pool_reuse_and_drops_owned_fields(
        owner_conduit_id: str,
        conduit_meld_stub: _ConduitMeldStub,
        owner_conduit_creations_stub: _ConduitCreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify permanent cleanup destroys instead of retaining to the pool."""
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        conduit_meld=conduit_meld_stub,
        owner_conduit_creations=owner_conduit_creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_stack_state=SpellSpaceThreadState(),
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire()

    space.permanent_cleanup()

    assert space.cleaned is True
    assert pool.idle_count == 0
    assert space not in spellspace_registry
    assert not hasattr(space, "_creations")
    assert not hasattr(space, "_owner_conduit_creations")
    assert not hasattr(space, "_spellspace_pool")
