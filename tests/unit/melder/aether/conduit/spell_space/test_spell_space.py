"""tests/aether/conduit/spell_space/test_spell_space.py

Validation: Not run.

These tests target `melder.aether.conduit.spell_space.spell_space.SpellSpace`.
They focus on SpellSpace lifecycle contracts, activation checks, and delegation behavior.
"""

from __future__ import annotations

from typing import Any, Optional

import pytest

from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError


class _CreationsStub:
    """Record spellspace cleanup calls for SpellSpace.reset/cleanup tests."""

    def __init__(self) -> None:
        """Initialize an empty record of cleared spellspace ids."""
        self.cleared_ids: list[str] = []

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """Record the spellspace id passed by SpellSpace.reset()."""
        self.cleared_ids.append(spellspace_id)


class _ConduitStub:
    """Minimal owner conduit stub for SpellSpace tests."""

    def __init__(self, *, creations: Optional[_CreationsStub], meld_result: Any = None) -> None:
        """Initialize the stub with an optional creations store and meld result."""
        self._creations = creations
        self._active_spellspace: Optional[SpellSpace] = None
        self._meld_calls: list[dict[str, Any]] = []
        self._meld_result = meld_result

    def set_active_spellspace(self, space: Optional[SpellSpace]) -> None:
        """Set the spellspace returned by get_active_spellspace()."""
        self._active_spellspace = space

    def get_active_spellspace(self) -> Optional[SpellSpace]:
        """Return the currently active spellspace (or None)."""
        return self._active_spellspace

    def _unregister_spellspace(self, space: SpellSpace) -> None:
        """
        Internal

        Clear the active spellspace reference if it matches.

        Args:
            space: The spellspace instance to unregister.
        """
        if self._active_spellspace is space:
            self._active_spellspace = None

    @property
    def meld_calls(self) -> list[dict[str, Any]]:
        """Return the recorded meld call arguments for assertions."""
        return self._meld_calls

    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
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
def creations_stub() -> _CreationsStub:
    """Provide a fresh creations stub for SpellSpace tests."""
    return _CreationsStub()


@pytest.fixture
def conduit_stub(creations_stub: _CreationsStub) -> _ConduitStub:
    """Provide a conduit stub wired with a creations stub."""
    return _ConduitStub(creations=creations_stub)


def test_init_requires_owner_conduit() -> None:
    """Verify SpellSpace rejects a None owner_conduit."""
    with pytest.raises(ValueError, match="owner_conduit must not be None"):
        SpellSpace(None)


def test_properties_expose_id_owner_and_version(conduit_stub: _ConduitStub) -> None:
    """Verify SpellSpace exposes stable id, owner, and starting version."""
    space = SpellSpace(conduit_stub)

    first_id = space.id
    assert isinstance(first_id, str)
    assert first_id != ""
    assert space.id == first_id
    assert space.owner_conduit is conduit_stub
    assert space.version == 0


def test_reset_clears_spellspace_instances_and_increments_version(
        conduit_stub: _ConduitStub,
        creations_stub: _CreationsStub,
) -> None:
    """Verify reset clears spellspace storage and increments version."""
    space = SpellSpace(conduit_stub)

    space.reset()

    assert creations_stub.cleared_ids == [space.id]
    assert space.version == 1


def test_reset_raises_when_owner_missing_spellspace_storage() -> None:
    """Verify reset raises when the owner conduit lacks spellspace storage."""
    conduit = _ConduitStub(creations=None)
    space = SpellSpace(conduit)

    with pytest.raises(SpellSpaceScopeError, match="does not expose spellspace storage"):
        space.reset()


def test_reset_raises_after_cleanup(conduit_stub: _ConduitStub) -> None:
    """Verify reset is blocked once SpellSpace is cleaned."""
    space = SpellSpace(conduit_stub)
    space.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        space.reset()


def test_meld_raises_when_not_active(conduit_stub: _ConduitStub) -> None:
    """Verify meld rejects calls when SpellSpace is not active on the owner."""
    space = SpellSpace(conduit_stub)

    with pytest.raises(SpellSpaceScopeError, match="active scope"):
        space.meld(spell_name="spell-x")


def test_meld_delegates_when_active_and_returns_result(conduit_stub: _ConduitStub) -> None:
    """Verify meld delegates to the owner when SpellSpace is active."""
    expected = object()
    conduit_stub._meld_result = expected
    space = SpellSpace(conduit_stub)
    conduit_stub.set_active_spellspace(space)

    result = space.meld(
        spell_name="spell-x",
        spell="spell-id",
        spellframe="frame-1",
        binding_name="bind-1",
        spell_override={"k": "v"},
    )

    assert result is expected
    assert len(conduit_stub.meld_calls) == 1
    assert conduit_stub.meld_calls[0] == {
        "spell_name": "spell-x",
        "spell": "spell-id",
        "spellframe": "frame-1",
        "binding_name": "bind-1",
        "spell_override": {"k": "v"},
    }


def test_meld_raises_after_cleanup(conduit_stub: _ConduitStub) -> None:
    """Verify meld is blocked once SpellSpace is cleaned."""
    space = SpellSpace(conduit_stub)
    space.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        space.meld(spell_name="spell-x")


def test_cleanup_calls_reset_drops_owner_reference_and_marks_cleaned(
        conduit_stub: _ConduitStub,
        creations_stub: _CreationsStub,
) -> None:
    """Verify cleanup clears spellspace instances and drops the owner reference."""
    space = SpellSpace(conduit_stub)
    space_id = space.id

    space.cleanup()

    assert space.cleaned is True
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.owner_conduit
    assert creations_stub.cleared_ids == [space_id]
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.version


def test_cleanup_idempotent_no_double_reset(
        conduit_stub: _ConduitStub,
        creations_stub: _CreationsStub,
) -> None:
    """Verify cleanup is idempotent and does not re-clear spellspace storage."""
    space = SpellSpace(conduit_stub)
    space_id = space.id

    space.cleanup()
    space.cleanup()

    assert creations_stub.cleared_ids == [space_id]
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.version


def test_cleanup_marks_cleaned_even_when_reset_raises() -> None:
    """Verify cleanup still marks cleaned and drops owner when reset fails."""
    conduit = _ConduitStub(creations=None)
    space = SpellSpace(conduit)
    space_id = space.id

    with pytest.raises(SpellSpaceScopeError, match="does not expose spellspace storage"):
        space.cleanup()

    assert space.cleaned is True
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.owner_conduit
    with pytest.raises(RuntimeError, match="already been cleaned"):
        _ = space.version
