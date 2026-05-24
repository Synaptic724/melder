"""tests/aether/conduit/spell_space/test_spell_space.py

Validation: Not run.

These tests target `melder.aether.conduit.spell_space.spell_space.SpellSpace`.
They focus on explicit-collaborator lifecycle, activation checks, and
delegation behavior.
"""

from __future__ import annotations

from typing import Any, Optional, Union

import pytest

from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)


class _CreationsStub:
    """Record spellspace cleanup calls and active-scope state for tests."""

    def __init__(self, *, owner_conduit_id: str) -> None:
        """Initialize the stub with owner identity and empty state."""
        self._owner_conduit_id = owner_conduit_id
        self.cleared_ids: list[str] = []
        self._active_spellspace: Optional[SpellSpace] = None

    @property
    def owner_conduit_id(self) -> str:
        """Return the owning conduit id for the stub."""
        return self._owner_conduit_id

    def set_active_spellspace(self, space: Optional[SpellSpace]) -> None:
        """Set the active spellspace returned by the stub."""
        self._active_spellspace = space

    def get_active_spellspace(self) -> Optional[SpellSpace]:
        """Return the currently active spellspace."""
        return self._active_spellspace

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """Record the spellspace id passed by SpellSpace.reset()."""
        self.cleared_ids.append(spellspace_id)


class _MeldStub:
    """Minimal meld stub that records delegation arguments."""

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


class _PoolStub:
    """Minimal spellspace pool stub for direct SpellSpace tests."""

    def __init__(self) -> None:
        """Initialize the stub with empty release bookkeeping."""
        self.released_ids: list[str] = []

    def release(self, obj: SpellSpace) -> None:
        """Record the release without mutating the spellspace a second time."""
        self.released_ids.append(obj.id)


@pytest.fixture
def owner_conduit_id() -> str:
    """Provide a stable owner conduit id for SpellSpace tests."""
    return "conduit-test"


@pytest.fixture
def creations_stub(owner_conduit_id: str) -> _CreationsStub:
    """Provide a fresh creations stub for SpellSpace tests."""
    return _CreationsStub(owner_conduit_id=owner_conduit_id)


@pytest.fixture
def meld_stub() -> _MeldStub:
    """Provide a fresh meld stub for SpellSpace tests."""
    return _MeldStub()


@pytest.fixture
def spellspace_registry() -> set[SpellSpace]:
    """Provide a fresh spellspace registry set for SpellSpace tests."""
    return set()


@pytest.fixture
def pool_stub() -> _PoolStub:
    """Provide a fresh direct pool stub for SpellSpace tests."""
    return _PoolStub()


def test_properties_expose_id_and_owner_conduit_id(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify SpellSpace exposes stable id and owner id."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )

    first_id = space.id
    assert isinstance(first_id, str)
    assert first_id != ""
    assert space.id == first_id
    assert space.owner_conduit_id == owner_conduit_id


def test_cleanup_clears_spellspace_instances_and_returns_to_pool(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify cleanup clears spellspace storage and returns the spellspace to the pool."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )
    spellspace_registry.add(space)
    space_id = space.id

    space.cleanup()

    assert creations_stub.cleared_ids == [space_id]
    assert pool_stub.released_ids == [space_id]
    assert space not in spellspace_registry


def test_meld_raises_when_not_active(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify meld rejects calls when SpellSpace is not the active scope."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )

    with pytest.raises(SpellSpaceScopeError, match="active scope"):
        space.meld(spell_name="spell-x")


def test_meld_delegates_when_active_and_returns_result(
        owner_conduit_id: str,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify meld delegates to the injected Meld runtime when active."""
    expected = object()
    meld_stub = _MeldStub(meld_result=expected)
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )
    creations_stub.set_active_spellspace(space)

    result = space.meld(
        spell_name="spell-x",
        spell="spell-id",
        spellframe="frame-1",
        binding_name="bind-1",
        spell_override={"k": "v"},
    )

    assert result is expected
    assert len(meld_stub.meld_calls) == 1
    assert meld_stub.meld_calls[0] == {
        "spell_name": "spell-x",
        "spell": "spell-id",
        "spellframe": "frame-1",
        "binding_name": "bind-1",
        "spell_override": {"k": "v"},
    }


def test_cleanup_calls_reset_unregisters_and_marks_cleaned(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
        pool_stub: _PoolStub,
) -> None:
    """Verify normal cleanup returns the spellspace to the pool."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
        spellspace_pool=pool_stub,
    )
    spellspace_registry.add(space)
    space_id = space.id

    space.cleanup()

    assert space.cleaned is False
    assert space not in spellspace_registry
    assert creations_stub.cleared_ids == [space_id]
    assert pool_stub.released_ids == [space_id]


def test_cleanup_returns_spellspace_to_pool(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify normal cleanup returns a pooled spellspace to the idle pool."""
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire()
    space_id = space.id

    space.cleanup()

    assert space.cleaned is False
    assert pool.idle_count == 1
    assert space not in spellspace_registry
    assert creations_stub.cleared_ids == [space_id]


def test_pool_reuses_spellspace_after_cleanup(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify a pooled spellspace is reused after normal cleanup."""
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
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


def test_permanent_cleanup_bypasses_pool_reuse(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify permanent cleanup destroys instead of retaining to the pool."""
    pool = SpellSpacePool(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
        baseline_idle=1,
        max_idle=1,
    )
    space = pool.acquire()
    space_id = space.id

    space.permanent_cleanup()

    assert space.cleaned is True
    assert pool.idle_count == 0
    assert space not in spellspace_registry
    assert creations_stub.cleared_ids == [space_id]
