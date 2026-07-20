from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState
from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_spellbook_conjure_rejects_invalid_policy_string() -> None:
    """
    Purpose:
        Validate conjure rejects invalid policy strings.
    Contract:
        - Invalid policy strings raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid policy strings do not raise.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    with pytest.raises(ValueError, match="Invalid value"):
        spellbook.conjure(policy="not-a-policy", dynamic=False, name="root")


def test_spellbook_conjure_rejects_dynamic_policy_when_non_dynamic() -> None:
    """
    Purpose:
        Validate conjure rejects dynamic-only policies in non-dynamic mode.
    Contract:
        - Non-dynamic conjure on an automatic world rejects non-default policies
          (settle-then-inherit: the world's automatic posture is the effective mode).
    Returns:
        None.
    Raises:
        AssertionError: If dynamic policies are accepted in non-dynamic mode.
    """
    configuration = SpellbookConfiguration()
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    with pytest.raises(RuntimeError, match="Dynamic-only policies"):
        spellbook.conjure(policy="whitelist_all", dynamic=False, name="root")


def test_spellbook_conjure_dynamic_flag_cannot_override_settled_automatic_world() -> None:
    """
    Purpose:
        Validate the dynamic flag is ignored on a SETTLED automatic world
        (settle-then-inherit law, owner ruling 2026-07-20). On a FRESH world
        conjure(dynamic=True) SETTLES the world dynamic instead - the old
        refusal is the settlement case now.
    Contract:
        - On a frozen automatic posture, conjure(dynamic=True) INHERITS
          automatic; a dynamic-only policy therefore still raises the
          policy refusal.
    Returns:
        None.
    Raises:
        AssertionError: If the flag overrides a settled automatic world.
    """
    frame = Aether()._ensure_frame("default")
    frame.bind_frame_configuration(AethericFrameConfiguration(
        origin_spellbook_id=None, system_state=SystemState.automatic,
        ai_native_enabled=False, rift_enabled=False,
    ))
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    with pytest.raises(RuntimeError, match="Dynamic-only policies"):
        spellbook.conjure(policy="whitelist_all", dynamic=True, name="root")


def test_spellbook_bind_rejects_invalid_permissions() -> None:
    """
    Purpose:
        Validate bind rejects invalid permissions.
    Contract:
        - Invalid permissions raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid permissions are accepted.
    """
    spellbook = Spellbook()
    with pytest.raises(ValueError, match="Invalid value"):
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="nope",
        )


def test_spellbook_bind_rejects_invalid_existence() -> None:
    """
    Purpose:
        Validate bind rejects invalid existence values.
    Contract:
        - Invalid existence values raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid existence values are accepted.
    """
    spellbook = Spellbook()
    with pytest.raises(ValueError, match="Invalid value"):
        spellbook.bind(
            spell=BasicService,
            existence="not-real",
            permissions="create",
        )


def test_spellbook_bind_rejects_non_callable_hooks() -> None:
    """
    Purpose:
        Validate bind rejects non-callable hooks.
    Contract:
        - Non-callable hooks raise TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If non-callable hooks are accepted.
    """
    spellbook = Spellbook()
    with pytest.raises(TypeError, match="pre_hooks"):
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            pre_hooks=[42],
        )
