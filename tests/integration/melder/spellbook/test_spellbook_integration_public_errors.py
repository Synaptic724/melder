from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


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
        spellbook.conjure(policy="not-a-policy", automatic=True, name="root")


def test_spellbook_conjure_rejects_dynamic_policy_when_automatic_true() -> None:
    """
    Purpose:
        Validate conjure rejects dynamic-only policies in automatic mode.
    Contract:
        - automatic=True rejects non-default policies.
    Returns:
        None.
    Raises:
        AssertionError: If dynamic policies are accepted in automatic mode.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    with pytest.raises(RuntimeError, match="Dynamic-only policies"):
        spellbook.conjure(policy="whitelist_all", automatic=True, name="root")


def test_spellbook_conjure_rejects_dynamic_mode_in_automatic_system_state() -> None:
    """
    Purpose:
        Validate conjure rejects dynamic mode when system_state is automatic.
    Contract:
        - automatic=False raises when system_state is automatic.
    Returns:
        None.
    Raises:
        AssertionError: If dynamic mode is allowed in automatic system_state.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    with pytest.raises(RuntimeError, match="automatic system_state"):
        spellbook.conjure(policy="default", automatic=False, name="root")


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
