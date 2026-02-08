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
) -> SimpleNamespace:
    """
    Build a minimal spell stub with the attributes MeldContext expects.

    Contract:
        - Provides owner creations metadata.

    Args:
        creations (Any): The creations container to expose on the spell.

    Returns:
        SimpleNamespace: Spell-like object with the expected attributes.
    """
    return SimpleNamespace(
        _owner_creations=creations,
    )


def test_init_with_missing_root_spell_raises_attributeerror() -> None:
    """
    Verify missing root spell fails via raw contract violation.

    Contract:
        - root_spell None propagates attribute-access failure.

    Raises:
        AssertionError: If root_spell None does not raise.
    """
    with pytest.raises(AttributeError):
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


def test_owner_creations_property_returns_owner_creations() -> None:
    """
    Verify owner_creations returns the root spell's owner creations.

    Contract:
        - owner_creations returns root_spell._owner_creations.

    Raises:
        AssertionError: If owner_creations does not match spell owner creations.
    """
    creations = object()
    root_spell = _make_root_spell(creations=creations)
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.owner_creations is creations
    finally:
        context.cleanup()


def test_caller_creations_defaults_none_when_not_provided() -> None:
    """
    Verify caller_creations remains None when not provided.

    Contract:
        - caller_creations is None when omitted.

    Raises:
        AssertionError: If caller_creations is not None by default.
    """
    creations = object()
    root_spell = _make_root_spell(creations=creations)
    context = MeldContext(root_spell=root_spell)
    try:
        assert context.caller_creations is None
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


def test_overrides_referenced_from_input_mapping() -> None:
    """
    Verify overrides reference the input mapping.

    Contract:
        - overrides equals the input mapping contents.
        - overrides is the same object supplied to MeldContext.

    Raises:
        AssertionError: If overrides are not referenced.
    """
    overrides: Mapping[str, Any] = {"x": 1}
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides=overrides)
    try:
        assert context.overrides == overrides
        assert context.overrides is overrides
    finally:
        context.cleanup()


def test_overrides_track_input_mapping_changes() -> None:
    """
    Verify overrides reflect input mapping changes.

    Contract:
        - Updates to the input mapping alter context overrides.

    Raises:
        AssertionError: If context overrides do not track external mutations.
    """
    overrides = {"x": 1}
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides=overrides)
    try:
        overrides["x"] = 2
        assert context.overrides["x"] == 2
    finally:
        context.cleanup()


def test_overrides_mutation_affects_original_mapping() -> None:
    """
    Verify context override mutations affect the input mapping.

    Contract:
        - Mutating context overrides mutates the original mapping.

    Raises:
        AssertionError: If external overrides are not mutated.
    """
    overrides = {"x": 1}
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides=overrides)
    try:
        context.overrides["x"] = 2
        assert overrides["x"] == 2
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


def test_owner_creations_snapshot_is_immutable() -> None:
    """
    Verify owner_creations reference is captured at initialization time.

    Contract:
        - Subsequent changes to root spell creations do not alter
          context.owner_creations.

    Raises:
        AssertionError: If context.owner_creations tracks root spell mutations.
    """
    creations = object()
    root_spell = _make_root_spell(creations=creations)
    context = MeldContext(root_spell=root_spell)
    try:
        root_spell._owner_creations = object()
        assert context.owner_creations is creations
    finally:
        context.cleanup()


def test_cleanup_clears_referenced_overrides_mapping() -> None:
    """
    Verify cleanup clears referenced overrides mapping.

    Contract:
        - context overrides are cleared on cleanup.
        - referenced override mapping is cleared.

    Raises:
        AssertionError: If cleanup does not clear referenced overrides.
    """
    overrides = {"x": 1}
    root_spell = _make_root_spell(creations=object())
    context = MeldContext(root_spell=root_spell, overrides=overrides)
    context.cleanup()
    assert overrides == {}
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
