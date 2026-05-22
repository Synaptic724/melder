import logging
from typing import Any, Dict, Iterable, Optional, Union
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.interfaces.ichannellogger import IChannelLogger
from melder.aether.aether_utility_system import AetherUtilitySystem




class InitHelpers:
    """
    Centralized startup-time helper wrappers for logger resolution.

    `InitHelpers` exists so runtime constructors can ask for safe logger
    wrappers without directly reaching into deeper utility-system ownership or
    spreading bootstrapping logic across many classes.

    Contract:
    - Provides thin static wrappers only.
    - Delegates actual logger policy and fallback behavior to
      `AetherUtilitySystem`.
    - Does not hold runtime state of its own.
    """

    __slots__ = ()

    @staticmethod
    def resolve_safe_logger(logger: IChannelLogger | logging.Logger | None) -> SafeLogger:
        """
        Resolve a plain logger-like object into a `SafeLogger`.

        Contract:
        - Delegates directly to `AetherUtilitySystem.resolve_safe_logger(...)`.
        - Accepts either an `IChannelLogger`, a stdlib `logging.Logger`, or
          `None`.
        - Returns a null-safe wrapper when no logger is supplied.

        Args:
            logger:
                Logger-like object to wrap. May be None.

        Returns:
            SafeLogger:
                Ready-to-use safe logger wrapper.
        """
        return AetherUtilitySystem().resolve_safe_logger(logger)

    @staticmethod
    def resolve_channel_logger(
            registrant: object,
            *,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            props: Optional[Dict[str, Any]] = None,
            channels: Optional[Union[str, Iterable[str]]] = None,
    ) -> SafeLogger:
        """
        Resolve a channel-style logger through the hosted utility system.

        Contract:
        - Delegates directly to `AetherUtilitySystem.resolve_channel_logger(...)`.
        - Does not own channel registration, fallback policy, or caching.

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
            SafeLogger:
                Channel-backed logger when configured, otherwise the hosted
                fallback/null-safe wrapper.
        """
        return AetherUtilitySystem().resolve_channel_logger(
            registrant,
            groups=groups,
            system_groups=system_groups,
            props=props,
            channels=channels,
        )
