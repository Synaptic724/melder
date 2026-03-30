import logging
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.interfaces.interfaces import IChannelLogger
from melder.aether.aether_utility_system import AetherUtilitySystem


class InitHelpers:
    """
    Centralized initializer utilities for Aether and related components.

    Provides static helpers for resolving safe wrappers or facilities
    during startup, before full DI/registry bootstraps are active.
    """

    __slots__ = ()

    @staticmethod
    def resolve_safe_logger(logger: IChannelLogger | logging.Logger | None) -> SafeLogger:
        """
        Returns a SafeLogger instance for any given logger-like object.

        - If `logger` is None, returns a SafeLogger in null mode.
        - If it's a CommandOps ChannelLogger, preserves its behavior.
        - If it's a standard Python logger, wraps it safely.
        - Never raises; always returns a usable SafeLogger.

        Args:
            logger: Logger-like object to wrap. May be None.

        Returns:
            SafeLogger: The resolved, ready-to-use SafeLogger instance.
        """
        return AetherUtilitySystem().resolve_safe_logger(logger)

    @staticmethod
    def resolve_channel_logger(
            registrant: object,
            *,
            groups=None,
            system_groups=None,
            props=None,
            channels=None,
    ) -> SafeLogger:
        """
        Resolve a channel-style logger through the hosted utility system.

        Args:
            registrant:
                Object requesting the logger.
            groups:
                Optional group tokens.
            system_groups:
                Optional system-group tokens.
            props:
                Optional flat property map.
            channels:
                Optional channel or channel list.

        Returns:
            SafeLogger: Iris-backed logger when configured, otherwise a null
            `SafeLogger`.
        """
        return AetherUtilitySystem().resolve_channel_logger(
            registrant,
            groups=groups,
            system_groups=system_groups,
            props=props,
            channels=channels,
        )
