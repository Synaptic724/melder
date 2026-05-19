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


def test_init_requires_owner_conduit_id(
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify SpellSpace rejects an empty owner_conduit_id."""
    with pytest.raises(ValueError, match="owner_conduit_id must not be empty"):
        SpellSpace(
            owner_conduit_id="",
            meld=meld_stub,
            creations=creations_stub,
            spellspace_registry=spellspace_registry,
        )


def test_properties_expose_id_owner_conduit_id_and_version(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify SpellSpace exposes stable id, owner id, and starting version."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
    )

    first_id = space.id
    assert isinstance(first_id, str)
    assert first_id != ""
    assert space.id == first_id
    assert space.owner_conduit_id == owner_conduit_id
    assert space.version == 0


def test_reset_clears_spellspace_instances_and_increments_version(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify reset clears spellspace storage and increments version."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
    )

    space.reset()

    assert creations_stub.cleared_ids == [space.id]
    assert space.version == 1


def test_reset_raises_after_cleanup(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify reset is blocked once SpellSpace is cleaned."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
    )
    spellspace_registry.add(space)
    space.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        space.reset()


def test_meld_raises_when_not_active(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify meld rejects calls when SpellSpace is not the active scope."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
    )

    with pytest.raises(SpellSpaceScopeError, match="active scope"):
        space.meld(spell_name="spell-x")


def test_meld_delegates_when_active_and_returns_result(
        owner_conduit_id: str,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify meld delegates to the injected Meld runtime when active."""
    expected = object()
    meld_stub = _MeldStub(meld_result=expected)
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
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


def test_meld_raises_after_cleanup(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify meld is blocked once SpellSpace is cleaned."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
    )
    spellspace_registry.add(space)
    space.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        space.meld(spell_name="spell-x")


def test_cleanup_calls_reset_unregisters_and_marks_cleaned(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify cleanup clears instances, unregisters, and drops collaborators."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
    )
    spellspace_registry.add(space)
    space_id = space.id

    space.cleanup()

    assert space.cleaned is True
    assert space not in spellspace_registry
    assert creations_stub.cleared_ids == [space_id]
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.owner_conduit_id
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.version


def test_cleanup_idempotent_no_double_reset(
        owner_conduit_id: str,
        meld_stub: _MeldStub,
        creations_stub: _CreationsStub,
        spellspace_registry: set[SpellSpace],
) -> None:
    """Verify cleanup is idempotent and does not re-clear spellspace storage."""
    space = SpellSpace(
        owner_conduit_id=owner_conduit_id,
        meld=meld_stub,
        creations=creations_stub,
        spellspace_registry=spellspace_registry,
    )
    spellspace_registry.add(space)
    space_id = space.id

    space.cleanup()
    space.cleanup()

    assert creations_stub.cleared_ids == [space_id]
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.version
