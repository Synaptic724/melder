import logging
import threading
from typing import Any, Callable, Dict, Iterable, Optional, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IChannelLogger
from melder.utilities.logger.safe_logger import SafeLogger


class AetherUtilitySystem(Cleanable):
    """
    Internal

    Process-wide utility host for Aether-owned helper systems.

    Purpose:
        Provide one stable runtime-owned location for shared utility providers,
        starting with logger acquisition. This avoids constructor logger spam,
        keeps the default logger path system-wide, and allows late
        registration of an Iris-backed resolver after Melder has already
        booted.

    Contract:
        - Singleton.
        - Starts unconfigured and returns a null `SafeLogger` by default.
        - Supports late registration of one channel-logger resolver.
        - Resolves channel loggers directly through the registered resolver.
        - Explicit logger objects may still be resolved bottom-up via
          `resolve_safe_logger(...)`.

    Lifecycle:
        Created eagerly by `Aether` at boot. Cleanup clears the registered
        resolver and resets singleton state for tests.
    """

    __melder_internal__ = _mrg.sentinel
    _instance = None
    _singleton_lock = threading.RLock()
    _initialized = False
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_channel_logger_resolver",
        "_default_logger",
    ]

    def __new__(cls, *args, **kwargs):
        """
        Ensure the utility system behaves as a singleton.

        Returns:
            AetherUtilitySystem: The one process-wide utility system instance.
        """
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = super(AetherUtilitySystem, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Internal

        Initialize the utility-system singleton.

        Returns:
            None.
        """
        if not AetherUtilitySystem._initialized:
            super().__init__()
            self._lock: threading.RLock = threading.RLock()
            self._channel_logger_resolver: Optional[Callable[..., Any]] = None
            self._default_logger: Optional[logging.Logger] = None
            AetherUtilitySystem._initialized = True

    @classmethod
    def _reset_singleton_for_tests(cls) -> None:
        """
        Reset the utility-system singleton for test isolation.

        Returns:
            None.
        """
        with cls._singleton_lock:
            instance = cls._instance
            if instance is None:
                cls._initialized = False
                return
            try:
                instance.cleanup()
            finally:
                cls._instance = None
                cls._initialized = False

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the utility system.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._channel_logger_resolver = None
            self._default_logger = None
        self._lock = None
        with AetherUtilitySystem._singleton_lock:
            AetherUtilitySystem._instance = None
            AetherUtilitySystem._initialized = False

    def has_channel_logger_resolver(self) -> bool:
        """
        Purpose:
            Return whether a channel-logger resolver has been registered.

        Returns:
            bool: True when configured.
        """
        self.check_cleaned()
        return self._channel_logger_resolver is not None

    def register_channel_logger_resolver(
            self,
            resolver: Callable[..., Any],
    ) -> None:
        """
        Internal

        Register the callable used to request Iris-backed channel loggers.

        Args:
            resolver:
                Callable accepting the channel-logger resolver signature.

        Returns:
            None.
        """
        self.check_cleaned()
        if not callable(resolver):
            raise TypeError("resolver must be callable.")
        with self._lock:
            self._channel_logger_resolver = resolver

    def has_default_logger(self) -> bool:
        """
        Purpose:
            Return whether a plain stdlib logger fallback has been registered.

        Returns:
            bool: True when configured.
        """
        self.check_cleaned()
        return self._default_logger is not None

    def register_default_logger(self, logger: logging.Logger) -> None:
        """
        Internal

        Register one process-wide default stdlib logger for message-only
        fallback behavior when no channel resolver is available.

        Args:
            logger:
                Standard library logger instance to use as the provider
                fallback.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(logger, logging.Logger):
            raise TypeError("logger must be a logging.Logger.")
        with self._lock:
            self._default_logger = logger

    def clear_default_logger(self) -> None:
        """
        Internal

        Remove the currently registered default stdlib logger fallback.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._default_logger = None

    def clear_channel_logger_resolver(self) -> None:
        """
        Internal

        Remove the currently registered channel-logger resolver.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._channel_logger_resolver = None

    def resolve_safe_logger(
            self,
            logger: Union[IChannelLogger, logging.Logger, None],
    ) -> SafeLogger:
        """
        Resolve a plain logger-like object into a `SafeLogger`.

        Args:
            logger:
                Explicit logger-like override or None.

        Returns:
            SafeLogger: Wrapped logger or null logger.
        """
        self.check_cleaned()
        if logger is None:
            return SafeLogger(None)
        if not isinstance(logger, (IChannelLogger, logging.Logger)):
            raise TypeError(
                "Expected logger to be an IChannelLogger, logging.Logger, or None."
            )
        return SafeLogger(logger)

    def resolve_channel_logger(
            self,
            registrant: object,
            *,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            props: Optional[Dict[str, Any]] = None,
            channels: Optional[Union[str, Iterable[str]]] = None,
    ) -> SafeLogger:
        """
        Resolve a channel-style logger for one registrant.

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
            SafeLogger: Iris-backed logger when configured; otherwise a null
            `SafeLogger`.
        """
        self.check_cleaned()
        with self._lock:
            resolver = self._channel_logger_resolver
            default_logger = self._default_logger
        if resolver is None:
            if default_logger is not None:
                return SafeLogger(default_logger)
            return SafeLogger(None)
        try:
            return SafeLogger(resolver(
                groups=groups,
                system_groups=system_groups,
                props=props,
                channels=channels,
                registrant=registrant,
            ))
        except Exception:
            if default_logger is not None:
                return SafeLogger(default_logger)
            return SafeLogger(None)
