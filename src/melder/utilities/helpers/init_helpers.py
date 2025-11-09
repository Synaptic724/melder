import logging
from melder.utilities.helpers.safe_logger import SafeLogger
from melder.utilities.interfaces.interfaces import IChannelLogger


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
        return SafeLogger(logger)
