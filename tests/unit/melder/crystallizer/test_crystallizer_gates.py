"""
Unit contract tests for Crystallizer gate tripwires (activation-required
verbs, sink type guards) and the RecordedUnitState enum's public contract.
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.persistence.recorded_unit_state import RecordedUnitState


@pytest.fixture(autouse=True)
def reset_crystallizer_singleton():
    """
    Reset the world singletons and boot a hosting Aether around each test.

    Contract:
        - First-time Crystallizer initialization REQUIRES the hosting
          Aether (crystallizer.py:101); Aether() constructs the hosted
          crystallizer, so the later Crystallizer() call returns it.

    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    Aether()
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()


def _activated_crystallizer():
    """
    Build one activated crystallizer with default knobs.

    Returns:
        Crystallizer: The activated singleton.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def test_create_spell_crystal_requires_activation():
    """
    Purpose:
        Verify crystal minting is activation-gated.
    Contract:
        create_spell_crystal on an inactive crystallizer raises
        RuntimeError (custody cannot be minted outside the recorded lane).
    Returns:
        None.
    Raises:
        AssertionError: If minting works while inactive.
    """
    crystallizer = Crystallizer()
    with pytest.raises(RuntimeError):
        crystallizer.create_spell_crystal(object())


def test_get_spell_crystal_requires_activation():
    """
    Purpose:
        Verify the custody lookup is activation-gated.
    Contract:
        get_spell_crystal on an inactive crystallizer raises RuntimeError
        before any record access.
    Returns:
        None.
    Raises:
        AssertionError: If lookup works while inactive.
    """
    crystallizer = Crystallizer()
    with pytest.raises(RuntimeError):
        crystallizer.get_spell_crystal("sha-a")


def test_activated_emit_rejects_unsupported_twin_types():
    """
    Purpose:
        Verify the sink forwards the profile's type guard.
    Contract:
        emit(object()) on an ACTIVATED crystallizer raises TypeError
        (the record never accepts unknown shapes silently).
    Returns:
        None.
    Raises:
        AssertionError: If an unsupported twin is swallowed.
    """
    crystallizer = _activated_crystallizer()
    with pytest.raises(TypeError, match="unsupported twin"):
        crystallizer.emit(object())


def test_describe_profile_routes_by_explicit_name():
    """
    Purpose:
        Verify named describe routing (not just the active profile).
    Contract:
        describe_profile("default") reports default even while a named
        profile is active; unknown names raise KeyError.
    Returns:
        None.
    Raises:
        AssertionError: If named routing drifts.
    """
    crystallizer = _activated_crystallizer()
    crystallizer.create_profile("kit-a")
    assert crystallizer.describe_profile("default")["profile_name"] == "default"
    assert crystallizer.describe_profile()["profile_name"] == "kit-a"
    with pytest.raises(KeyError):
        crystallizer.describe_profile("ghost")


def test_recorded_unit_state_enum_contract():
    """
    Purpose:
        Verify the state-switch enum's public shape.
    Contract:
        Exactly three members (enabled/disabled/cleaned); each member's
        value equals its name (describe consumers read stable strings).
    Returns:
        None.
    Raises:
        AssertionError: If the enum shape drifts.
    """
    assert {member.name for member in RecordedUnitState} == {
        "enabled", "disabled", "cleaned",
    }
    for member in RecordedUnitState:
        assert member.value == member.name
