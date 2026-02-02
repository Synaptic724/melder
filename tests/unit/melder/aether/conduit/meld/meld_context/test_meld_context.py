import logging
from types import SimpleNamespace
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.meld.meld_context.meld_context import MeldContext
from melder.utilities.interfaces.interfaces import IChannelLogger
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
)


class _ChannelLoggerStub:
    """
    Minimal stub that satisfies IChannelLogger structural checks.

    This provides all protocol attributes and a setLevel method so SafeLogger
    can initialize without raising.
    """

    def __init__(self) -> None:
        """
        Initialize the stub with protocol attributes and a setLevel hook.
        """
        for name in IChannelLogger.__protocol_attrs__:
            setattr(self, name, MagicMock())
        self.setLevel = MagicMock()


def _make_root_spell(
    *,
    creations: Any = None,
    conduit_id: str | None = "conduit-1",
    conduit_name: str | None = "alpha",
    aetheric_frame: str | None = "default",
) -> SimpleNamespace:
    """
    Build a minimal spell stub with the attributes MeldContext expects.

    Contract:
        - Provides owner creations, conduit metadata, and frame fields.

    Args:
        creations (Any): The creations container to expose on the spell.
        conduit_id (str | None): Optional conduit id for metadata.
        conduit_name (str | None): Optional conduit name for metadata.
        aetheric_frame (str | None): Optional frame metadata.

    Returns:
        SimpleNamespace: Spell-like object with the expected attributes.
    """
    return SimpleNamespace(
        _owner_creations=creations,
        _owner_conduit_id=conduit_id,
        _owner_conduit_name=conduit_name,
        aetheric_frame=aetheric_frame,
    )


def test_init_requires_root_spell_raises_valueerror() -> None:
    """
    Verify MeldContext rejects missing root_spell inputs.

    Contract:
        - root_spell cannot be None.

    Raises:
        AssertionError: If root_spell None does not raise.
    """
    with pytest.raises(ValueError, match="root_spell cannot be None"):
        MeldContext(root_spell=None)


def test_root_spell_property_returns_value() -> None:
    """
    Verify root_spell property returns the provided spell object.

    Contract:
        - root_spell returns the same object supplied at initialization.

    Raises:
        AssertionError: If root_spell does not match the input.
    """
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.root_spell is root_spell
    finally:
        context.cleanup()


def test_creations_property_returns_owner_creations() -> None:
    """
    Verify creations property returns the root spell's owner creations.

    Contract:
        - creations returns root_spell._owner_creations.
        - owner_creations returns root_spell._owner_creations.

    Raises:
        AssertionError: If creations does not match the spell's owner creations.
    """
    creations = object()
    root_spell = _make_root_spell(creations=creations)
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.creations is creations
        assert context.owner_creations is creations
    finally:
        context.cleanup()


def test_caller_creations_defaults_to_owner_creations() -> None:
    """
    Verify caller_creations defaults to owner creations when not provided.

    Contract:
        - caller_creations returns the same object as owner_creations by default.

    Raises:
        AssertionError: If caller_creations does not default to owner_creations.
    """
    creations = object()
    root_spell = _make_root_spell(creations=creations)
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.caller_creations is creations
    finally:
        context.cleanup()


def test_caller_creations_uses_explicit_value() -> None:
    """
    Verify caller_creations uses the explicit value when provided.

    Contract:
        - caller_creations returns the provided object.
        - owner_creations remains bound to root_spell._owner_creations.

    Raises:
        AssertionError: If caller_creations does not reflect the explicit value.
    """
    owner_creations = object()
    caller_creations = object()
    root_spell = _make_root_spell(creations=owner_creations)
    context = MeldContext(
        root_spell=root_spell,
        caller_creations=caller_creations,
    )
    try:
        assert context.owner_creations is owner_creations
        assert context.caller_creations is caller_creations
    finally:
        context.cleanup()


def test_caller_creations_lock_held_defaults_false() -> None:
    """
    Verify caller_creations_lock_held defaults to False.

    Contract:
        - caller_creations_lock_held is False when not provided.

    Raises:
        AssertionError: If the default is not False.
    """
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.caller_creations_lock_held is False
    finally:
        context.cleanup()


def test_caller_creations_lock_held_is_stored() -> None:
    """
    Verify caller_creations_lock_held preserves explicit values.

    Contract:
        - caller_creations_lock_held returns the provided boolean.

    Raises:
        AssertionError: If the flag does not match the input.
    """
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(
        root_spell=root_spell,
        caller_creations_lock_held=True,
    )
    try:
        assert context.caller_creations_lock_held is True
    finally:
        context.cleanup()


def test_conduit_id_property_returns_value() -> None:
    """
    Verify conduit_id property returns the owner conduit id.

    Contract:
        - conduit_id returns root_spell._owner_conduit_id.

    Raises:
        AssertionError: If conduit_id does not match the spell metadata.
    """
    root_spell = _make_root_spell(conduit_id="conduit-9")
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.conduit_id == "conduit-9"
    finally:
        context.cleanup()


def test_conduit_name_property_returns_value() -> None:
    """
    Verify conduit_name property returns the owner conduit name.

    Contract:
        - conduit_name returns root_spell._owner_conduit_name.

    Raises:
        AssertionError: If conduit_name does not match the spell metadata.
    """
    root_spell = _make_root_spell(conduit_name="omega")
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.conduit_name == "omega"
    finally:
        context.cleanup()


def test_aetheric_frame_property_returns_value() -> None:
    """
    Verify aetheric_frame property returns the spell's frame.

    Contract:
        - aetheric_frame returns root_spell.aetheric_frame.

    Raises:
        AssertionError: If aetheric_frame does not match the spell metadata.
    """
    root_spell = _make_root_spell(aetheric_frame="frame-2")
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.aetheric_frame == "frame-2"
    finally:
        context.cleanup()


def test_conduit_metadata_preserves_none_values() -> None:
    """
    Verify conduit metadata preserves None values.

    Contract:
        - conduit_id, conduit_name, and aetheric_frame retain None values.

    Raises:
        AssertionError: If None metadata is replaced or altered.
    """
    root_spell = _make_root_spell(
        conduit_id=None,
        conduit_name=None,
        aetheric_frame=None,
    )
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.conduit_id is None
        assert context.conduit_name is None
        assert context.aetheric_frame is None
    finally:
        context.cleanup()


def test_overrides_default_none() -> None:
    """
    Verify overrides defaults to None when not provided.

    Contract:
        - overrides is None when no overrides are supplied.

    Raises:
        AssertionError: If overrides is not None by default.
    """
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.overrides is None
    finally:
        context.cleanup()


def test_overrides_default_none_for_each_context() -> None:
    """
    Verify default overrides are None per context.

    Contract:
        - Each MeldContext starts with overrides set to None.

    Raises:
        AssertionError: If overrides defaults are not None.
    """
    root_spell = _make_root_spell(creations=object())
    first = MeldContext(root_spell=root_spell)
    second = MeldContext(root_spell=root_spell)
    try:
        assert first.overrides is None
        assert second.overrides is None
    finally:
        first.cleanup()
        second.cleanup()


def test_overrides_copied_from_input_mapping() -> None:
    """
    Verify overrides are copied from the input mapping.

    Contract:
        - overrides equals the input mapping contents.
        - overrides is a separate object.

    Raises:
        AssertionError: If overrides are not copied.
    """
    overrides: Mapping[str, Any] = {"x": 1}
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides=overrides)
    try:
        assert context.overrides == overrides
        assert context.overrides is not overrides
    finally:
        context.cleanup()


def test_overrides_not_mutated_when_input_mapping_changes() -> None:
    """
    Verify overrides are insulated from input mapping changes.

    Contract:
        - Updates to the input mapping do not alter context overrides.

    Raises:
        AssertionError: If context overrides track external mutations.
    """
    overrides = {"x": 1}
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides=overrides)
    try:
        overrides["x"] = 2
        assert context.overrides["x"] == 1
    finally:
        context.cleanup()


def test_overrides_mutation_does_not_affect_original_mapping() -> None:
    """
    Verify context override mutations do not affect the input mapping.

    Contract:
        - Mutating context overrides leaves the original mapping untouched.

    Raises:
        AssertionError: If external overrides are mutated.
    """
    overrides = {"x": 1}
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides=overrides)
    try:
        context.overrides["x"] = 2
        assert overrides["x"] == 1
    finally:
        context.cleanup()


def test_overrides_property_mutations_persist() -> None:
    """
    Verify mutations made through overrides persist.

    Contract:
        - updates through overrides are reflected on subsequent access.

    Raises:
        AssertionError: If override mutations are not persisted.
    """
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides={})
    try:
        context.overrides["x"] = 1
        assert context.overrides["x"] == 1
    finally:
        context.cleanup()


def test_metadata_snapshot_is_immutable() -> None:
    """
    Verify conduit metadata is captured at initialization time.

    Contract:
        - Subsequent root spell metadata changes do not alter context metadata.

    Raises:
        AssertionError: If context metadata tracks root spell mutations.
    """
    root_spell = _make_root_spell(
        conduit_id="conduit-9",
        conduit_name="alpha",
        aetheric_frame="frame-1",
    )
    context = MeldContext(root_spell=root_spell)
    try:
        root_spell._owner_conduit_id = "conduit-10"
        root_spell._owner_conduit_name = "beta"
        root_spell.aetheric_frame = "frame-2"
        assert context.conduit_id == "conduit-9"
        assert context.conduit_name == "alpha"
        assert context.aetheric_frame == "frame-1"
    finally:
        context.cleanup()


def test_creations_snapshot_is_immutable() -> None:
    """
    Verify creations reference is captured at initialization time.

    Contract:
        - Subsequent changes to root spell creations do not alter context.creations.

    Raises:
        AssertionError: If context.creations tracks root spell mutations.
    """
    creations = object()
    root_spell = _make_root_spell(creations=creations)
    context = MeldContext(root_spell=root_spell)
    try:
        root_spell._owner_creations = object()
        assert context.creations is creations
    finally:
        context.cleanup()


def test_cleanup_clears_internal_overrides_only() -> None:
    """
    Verify cleanup clears internal overrides without mutating the input mapping.

    Contract:
        - context overrides are cleared on cleanup.
        - external override mapping remains unchanged.

    Raises:
        AssertionError: If cleanup mutates the original mapping.
    """
    overrides = {"x": 1}
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides=overrides)
    context.cleanup()
    assert overrides == {"x": 1}
    assert context.overrides is None


def test_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called multiple times safely.

    Contract:
        - Subsequent cleanup calls do not raise.
        - Context remains cleaned after repeated calls.

    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell)
    context.cleanup()
    context.cleanup()
    assert context.cleaned is True
