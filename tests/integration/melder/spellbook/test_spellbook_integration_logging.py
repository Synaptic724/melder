from __future__ import annotations

import logging

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook


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
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_spellbook_uses_registered_channel_logger_provider() -> None:
    """
    Purpose:
        Validate Spellbook and Aether use the registered channel logger provider.
    Contract:
        - The provider resolver is invoked for both Aether and Spellbook.
        - Aether and Spellbook both end up with non-null underlying loggers.
    Returns:
        None.
    Raises:
        AssertionError: If the provider path is not used.
    """
    created_for: list[object] = []

    def resolver(*, registrant: object, groups=None, system_groups=None, props=None, channels=None) -> logging.Logger:
        """
        Purpose:
            Provide a stable stdlib logger for the requested registrant.
        Contract:
            - Records each registrant for verification.
            - Returns a stdlib logger instance.
        Args:
            registrant: Object requesting a logger.
        Returns:
            logging.Logger: The logger instance.
        """
        created_for.append(registrant)
        return logging.getLogger(f"spellbook-integration.{registrant.__class__.__name__}")

    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem().register_channel_logger_resolver(resolver)
    aether = Aether()
    aether_configuration = (
        aether.create_configuration_builder()
        .with_channel_logger_activation_enabled(True)
        .with_channel_logger_resolver(resolver)
        .build()
        .activate()
    )
    aether.activate(aether_configuration)
    aether.enable_logging()
    Spellbook._aether = aether
    Conduit._aether = aether

    configuration = SpellbookConfiguration(aether_frame="log-frame")
    spellbook = Spellbook(aetheric_frame="log-frame", configuration=configuration)

    assert any(isinstance(obj, Aether) for obj in created_for)
    assert any(isinstance(obj, Spellbook) for obj in created_for)
    assert Spellbook._aether._logger is not None
    assert Spellbook._aether._logger._logger is not None
    assert spellbook._logger is not None
    assert spellbook._logger._logger is not None
