import logging
from concurrent.futures import ThreadPoolExecutor
import threading

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


def test_aether_utility_system_singleton_under_concurrent_construction() -> None:
    """Parallel constructor calls should still resolve to one shared utility-system instance."""
    worker_count = 16
    start_barrier = threading.Barrier(worker_count)

    def build_instance_id() -> int:
        start_barrier.wait()
        return id(AetherUtilitySystem())

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(build_instance_id) for _ in range(worker_count)]
        instance_ids = [future.result() for future in futures]

    assert len(set(instance_ids)) == 1
    assert AetherUtilitySystem._instance is not None


def test_has_channel_logger_resolver_false_by_default() -> None:
    """Resolver presence should default to false."""
    assert AetherUtilitySystem().has_channel_logger_resolver() is False


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


def test_resolve_safe_logger_returns_null_logger_for_none() -> None:
    """resolve_safe_logger should return a null SafeLogger for None."""
    logger = AetherUtilitySystem().resolve_safe_logger(None)

    assert isinstance(logger, SafeLogger)
    assert logger._logger is None


def test_resolve_safe_logger_wraps_stdlib_logger() -> None:
    """resolve_safe_logger should wrap a concrete stdlib logger unchanged."""
    raw = logging.getLogger("utility-safe-wrap")

    logger = AetherUtilitySystem().resolve_safe_logger(raw)

    assert isinstance(logger, SafeLogger)
    assert logger._logger is raw


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


def test_register_channel_logger_resolver_rejects_non_callable() -> None:
    """register_channel_logger_resolver should reject non-callable inputs."""
    with pytest.raises(TypeError, match="callable"):
        AetherUtilitySystem().register_channel_logger_resolver("invalid")


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


def test_register_default_logger_is_used_when_channel_resolver_is_missing() -> None:
    """
    Verify a registered plain stdlib logger becomes the provider fallback when
    no channel resolver exists.

    Returns:
        None.
    """
    raw = logging.getLogger("default-fallback")
    system = AetherUtilitySystem()
    system.register_default_logger(raw)

    logger = system.resolve_channel_logger(object(), channels="system")

    assert isinstance(logger, SafeLogger)
    assert logger._logger is raw


def test_has_default_logger_tracks_registration_and_clear() -> None:
    """Default logger presence should reflect registration and clearing."""
    system = AetherUtilitySystem()
    logger = logging.getLogger("presence-check")

    assert system.has_default_logger() is False
    system.register_default_logger(logger)
    assert system.has_default_logger() is True
    system.clear_default_logger()
    assert system.has_default_logger() is False


def test_register_default_logger_rejects_non_logger() -> None:
    """register_default_logger should reject non-logging.Logger objects."""
    with pytest.raises(TypeError, match="logging.Logger"):
        AetherUtilitySystem().register_default_logger("invalid")


def test_default_logger_is_used_when_channel_resolver_raises() -> None:
    """
    Verify the default stdlib logger fallback is used when channel resolution
    fails.

    Returns:
        None.
    """
    raw = logging.getLogger("default-on-error")

    def resolver(**_: object) -> logging.Logger:
        """
        Raise to simulate channel resolver failure.

        Returns:
            logging.Logger: Never returns successfully.
        """
        raise RuntimeError("resolver failed")

    system = AetherUtilitySystem()
    system.register_default_logger(raw)
    system.register_channel_logger_resolver(resolver)

    logger = system.resolve_channel_logger(object(), channels="system")

    assert isinstance(logger, SafeLogger)
    assert logger._logger is raw


def test_clear_default_logger_restores_null_fallback_without_channel_resolver() -> None:
    """
    Verify clearing the default logger restores null fallback mode when no
    channel resolver exists.

    Returns:
        None.
    """
    system = AetherUtilitySystem()
    system.register_default_logger(logging.getLogger("temp-default"))
    system.clear_default_logger()

    logger = system.resolve_channel_logger(object(), channels="system")

    assert isinstance(logger, SafeLogger)
    assert logger._logger is None


def test_cleanup_is_idempotent() -> None:
    """cleanup should be safe to call repeatedly."""
    system = AetherUtilitySystem()

    system.cleanup()
    system.cleanup()

    assert system._cleaned is True


def test_cleanup_returns_early_when_cleaned_flips_inside_lock() -> None:
    """cleanup should return safely if another path marks the instance cleaned inside the lock."""
    system = AetherUtilitySystem()
    system._channel_logger_resolver = lambda **_: logging.getLogger("resolver")
    system._default_logger = logging.getLogger("default-before-race")
    original_lock = system._lock

    class _LockThatMarksCleaned:
        def __enter__(self_inner):
            system._cleaned = True
            return self_inner

        def __exit__(self_inner, exc_type, exc_value, traceback):
            return False

    try:
        system._lock = _LockThatMarksCleaned()
        system.cleanup()
    finally:
        system._lock = original_lock

    assert system._channel_logger_resolver is not None
    assert system._default_logger is not None


def test_resolve_safe_logger_rejects_invalid_type() -> None:
    """resolve_safe_logger should reject unsupported logger objects."""
    with pytest.raises(TypeError, match="IChannelLogger"):
        AetherUtilitySystem().resolve_safe_logger("invalid")


def test_resolve_channel_logger_returns_null_logger_when_resolver_raises_and_no_default_exists() -> None:
    """Resolver failures should fall back to a null logger when no default logger is registered."""
    def resolver(**_: object) -> logging.Logger:
        raise RuntimeError("resolver failed")

    system = AetherUtilitySystem()
    system.register_channel_logger_resolver(resolver)

    logger = system.resolve_channel_logger(object(), channels="system")

    assert isinstance(logger, SafeLogger)
    assert logger._logger is None
