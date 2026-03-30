import logging

import pytest

from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.utilities.logger.safe_logger import SafeLogger


@pytest.fixture(autouse=True)
def fresh_utility_system() -> None:
    """
    Reset the utility-system singleton around each test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    yield
    AetherUtilitySystem._reset_singleton_for_tests()


def test_aether_utility_system_is_singleton() -> None:
    """
    Verify `AetherUtilitySystem` enforces the singleton contract.

    Returns:
        None.
    """
    first = AetherUtilitySystem()
    second = AetherUtilitySystem()

    assert first is second


def test_resolve_channel_logger_falls_back_to_null_logger_when_unconfigured() -> None:
    """
    Verify the provider returns a null `SafeLogger` when no resolver is
    registered.

    Returns:
        None.
    """
    logger = AetherUtilitySystem().resolve_channel_logger(object(), channels="system")

    assert isinstance(logger, SafeLogger)
    assert logger._logger is None


def test_register_channel_logger_resolver_is_used() -> None:
    """
    Verify a registered resolver is called through the provider and wrapped in
    `SafeLogger`.

    Returns:
        None.
    """
    seen = {}

    def resolver(*, registrant, groups=None, system_groups=None, props=None, channels=None):
        seen["registrant"] = registrant
        seen["groups"] = list(groups or [])
        seen["system_groups"] = list(system_groups or [])
        seen["props"] = dict(props or {})
        seen["channels"] = channels
        return logging.getLogger("provider-test")

    system = AetherUtilitySystem()
    system.register_channel_logger_resolver(resolver)
    registrant = object()

    logger = system.resolve_channel_logger(
        registrant,
        groups=["rift"],
        system_groups=["melder"],
        props={"epoch": 7},
        channels="system",
    )

    assert isinstance(logger, SafeLogger)
    assert seen["registrant"] is registrant
    assert seen["groups"] == ["rift"]
    assert seen["system_groups"] == ["melder"]
    assert seen["props"] == {"epoch": 7}
    assert seen["channels"] == "system"


def test_clear_channel_logger_resolver_restores_null_fallback() -> None:
    """
    Verify clearing the resolver returns the provider to null-logger mode.

    Returns:
        None.
    """
    system = AetherUtilitySystem()
    system.register_channel_logger_resolver(lambda **_: logging.getLogger("temp"))
    system.clear_channel_logger_resolver()

    logger = system.resolve_channel_logger(object(), channels="system")

    assert isinstance(logger, SafeLogger)
    assert logger._logger is None
