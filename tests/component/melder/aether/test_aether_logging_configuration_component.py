import logging

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_for_component_logger_tests() -> None:
    """
    Reset Aether-owned singleton state around each logger component test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_configuration(aether_frame: str) -> SpellbookConfiguration:
    """
    Create one spellbook configuration for logger component tests.

    Args:
        aether_frame:
            Target Aether frame name.

    Returns:
        SpellbookConfiguration:
            Initialized configuration object.
    """
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    return configuration


def test_component_spellbook_automatic_logger_stays_null_when_activation_is_disabled() -> None:
    """
    Verify Aether-owned logger policy keeps Spellbook silent by default.

    Contract:
        - Aether builder-created config can be activated through the root.
        - Automatic channel logger activation remains off.
        - Spellbook logger initialization resolves to the null SafeLogger path.

    Returns:
        None.
    """
    aether = Aether()
    configuration = (
        aether.create_configuration_builder()
        .with_defaults()
        .activate()
    )
    aether.activate(configuration)

    spellbook = Spellbook(
        aetheric_frame="component-logger-disabled",
        configuration=_make_configuration("component-logger-disabled"),
    )
    try:
        assert spellbook._logger._logger is None
    finally:
        spellbook.cleanup()


def test_component_spellbook_automatic_logger_uses_configured_default_logger_when_enabled() -> None:
    """
    Verify enabled Aether logger policy reaches Spellbook through InitHelpers.

    Contract:
        - Aether builder-created config can enable automatic logger activation.
        - The configured default stdlib logger becomes the Spellbook logger
          when no explicit logger is supplied.

    Returns:
        None.
    """
    aether = Aether()
    default_logger = logging.getLogger("component-spellbook-default-logger")
    configuration = (
        aether.create_configuration_builder()
        .with_channel_logger_activation_enabled(True)
        .with_default_logger(default_logger)
        .activate()
    )
    aether.activate(configuration)

    spellbook = Spellbook(
        aetheric_frame="component-logger-enabled",
        configuration=_make_configuration("component-logger-enabled"),
    )
    try:
        assert spellbook._logger._logger is default_logger
    finally:
        spellbook.cleanup()
