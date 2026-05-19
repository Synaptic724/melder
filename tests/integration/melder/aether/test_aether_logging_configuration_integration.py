import logging

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_logger_integration() -> None:
    """
    Reset Aether-owned singleton state around each logger integration test.

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
    Create one spellbook configuration for logger integration tests.

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


def test_integration_aether_logging_configuration_reaches_aether_spellbook_and_conduit() -> None:
    """
    Verify one Aether config drives the full runtime logger path.

    Contract:
        - Aether can create the fluent config builder itself.
        - Activated logger policy enables automatic channel logger resolution.
        - `Aether.enable_logging()` uses the same automatic path.
        - Spellbook and its conjured Conduit resolve their loggers through the
          configured resolver when no explicit logger is supplied.

    Returns:
        None.
    """
    aether = Aether()
    seen_registrant_types = []

    def resolver(**kwargs: object) -> logging.Logger:
        registrant = kwargs["registrant"]
        seen_registrant_types.append(type(registrant).__name__)
        return logging.getLogger(
            f"integration-auto-{type(registrant).__name__.lower()}"
        )

    configuration = (
        aether.create_configuration_builder()
        .with_channel_logger_activation_enabled(True)
        .with_channel_logger_resolver(resolver)
        .activate()
    )
    aether.activate(configuration)
    aether.enable_logging()

    spellbook = Spellbook(
        aetheric_frame="integration-logger-enabled",
        configuration=_make_configuration("integration-logger-enabled"),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")

    try:
        assert aether.logger is logging.getLogger("integration-auto-aether")
        assert spellbook._logger._logger is logging.getLogger(
            "integration-auto-spellbook"
        )
        assert conduit._logger._logger is logging.getLogger(
            "integration-auto-conduit"
        )
        assert seen_registrant_types == ["Aether", "Spellbook", "Conduit"]
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_integration_aether_logging_configuration_keeps_automatic_logger_path_disabled() -> None:
    """
    Verify registered logger providers stay dormant until Aether enables them.

    Contract:
        - Aether can carry a resolver/default logger in config while automatic
          activation remains disabled.
        - `Aether.enable_logging()` now fails fast for the automatic path in
          that disabled state instead of silently no-oping.
        - Spellbook and Conduit stay on the null logger path.

    Returns:
        None.
    """
    aether = Aether()
    configuration = (
        aether.create_configuration_builder()
        .with_channel_logger_resolver(
            lambda **_: logging.getLogger("integration-disabled-resolver")
        )
        .with_default_logger(logging.getLogger("integration-disabled-default"))
        .activate()
    )
    aether.activate(configuration)

    with pytest.raises(RuntimeError, match="disabled in AetherConfiguration"):
        aether.enable_logging()

    spellbook = Spellbook(
        aetheric_frame="integration-logger-disabled",
        configuration=_make_configuration("integration-logger-disabled"),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")

    try:
        assert aether.logger is None
        assert spellbook._logger._logger is None
        assert conduit._logger._logger is None
    finally:
        conduit.cleanup()
        spellbook.cleanup()
