import logging
from typing import Any, Dict, Iterable, Optional, Union
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.interfaces.ichannellogger import IChannelLogger
from melder.aether.aether_utility_system import AetherUtilitySystem




class InitHelpers:
    """
    Centralized startup-time helper wrappers for logger resolution.

    Responsibilities:
        - Resolve a provider-backed CHANNEL logger for a runtime object.
        - Wrap an explicitly supplied logger into a `SafeLogger`.

    TWO RESOLUTION PATHS, AND WHICH TO USE:
        - `resolve_channel_logger(...)` is the PRIMARY path. It asks the hosted
          provider in `AetherUtilitySystem` for a channel logger. When automatic
          channel activation is disabled - the default - it returns a null
          `SafeLogger` rather than failing, so a runtime object always ends up
          with a usable logging surface.
        - `resolve_safe_logger(...)` is for the case where a caller ALREADY has
          a logger object and wants it wrapped for the runtime's uniform
          interface.

        Every runtime object goes through one of these rather than touching
        `logging` directly. That is what makes logger policy installable at the
        Aether root instead of being baked into each constructor.

    Owned State:
        None. Static namespace, not an object with a lifetime.

    Threading:
        Stateless. Resolution reads provider registrations owned by
        `AetherUtilitySystem`; the concurrency contract lives there, not here.

    Lifecycle / Cleanup:
        No instances, no cleanup contract. Deliberately not `Cleanable`. The
        `SafeLogger` objects it hands back ARE cleanable, and are owned by the
        object that requested one.

    Registration:
        MELDER KERNEL - guarded. Logging resolution is runtime plumbing called
        directly during construction.

    Subsystem Context:
        The construction-time face of the logging trio in `utilities/`:
        `AetherUtilitySystem` hosts the providers, `SafeLogger` is the adapter,
        and this is the thin resolution seam constructors call. Sits beside
        `IDBuilder`, `EnumHelpers`, and `SpellInputUtils` as one of the static
        helper namespaces.

    System Context:
        `Aether`, `Spellbook`, `Conduit`, `Nexus`, and `Rift` all obtain their
        loggers here during `_initialize_logging`-style boot steps. Because the
        provider path no-ops to a null logger by default, a Melder process is
        SILENT until logger policy is installed through
        `AetherConfiguration` - quiet-by-default is a deliberate posture for a
        library, not a missing feature.

    `InitHelpers` exists so runtime constructors can ask for safe logger
    wrappers without directly reaching into deeper utility-system ownership or
    spreading bootstrapping logic across many classes.

    Contract:
    - Provides thin static wrappers only.
    - Delegates actual logger policy and fallback behavior to
      `AetherUtilitySystem`.
    - Does not hold runtime state of its own.
    """

    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Static seam every runtime constructor uses to obtain a "
        "logger. resolve_channel_logger(...) asks the hosted provider (returns "
        "a null SafeLogger when channel logging is off - the default, so Melder "
        "is silent until policy is installed); resolve_safe_logger(...) wraps a "
        "logger you already have."
    )

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
