import logging
from typing import Any, Callable, Optional, Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IAetherConfiguration(ICleanable, Protocol):
    """
    Mutable-to-frozen configuration surface for Aether root policy.

    Purpose:
        Hold process-wide Aether policy inputs before the root applies them to
        hosted subsystems. The first owned policy slice is logger activation
        control for `AetherUtilitySystem`.

    Contract:
        - Mutable until frozen.
        - Activation is explicit and implies successful validation/freeze.
        - Automatic channel logger activation is disabled by default.
        - Explicit logger attachment remains outside this config surface.
    """

    @property
    def id(self) -> str:
        """
        Return the stable configuration id.

        Returns:
            str: Stable configuration identifier.
        """
        ...

    @property
    def frozen(self) -> bool:
        """
        Return whether the configuration is frozen.

        Returns:
            bool: True when mutation is closed.
        """
        ...

    @property
    def activated(self) -> bool:
        """
        Return whether the configuration has been activated.

        Returns:
            bool: True when validated, frozen, and marked ready for Aether.
        """
        ...

    @property
    def channel_logger_activation_enabled(self) -> bool:
        """
        Return whether automatic channel logger activation is enabled.

        Returns:
            bool: True when `resolve_channel_logger(...)` may auto-attach.
        """
        ...

    @property
    def channel_logger_resolver(self) -> Optional[Callable[..., Any]]:
        """
        Return the configured channel logger resolver, if any.

        Returns:
            Optional[Callable[..., Any]]: Configured resolver.
        """
        ...

    @property
    def default_logger(self) -> Optional[logging.Logger]:
        """
        Return the configured stdlib fallback logger, if any.

        Returns:
            Optional[logging.Logger]: Configured default logger.
        """
        ...

    def cleanup(self) -> None:
        """
        Idempotently clear configuration state.

        Returns:
            None.
        """
        ...

    def with_defaults(self) -> "IAetherConfiguration":
        """
        Apply the default Aether logger policy.

        Returns:
            IAetherConfiguration: This configuration instance.
        """
        ...

    def with_channel_logger_activation_enabled(
            self,
            enabled: bool,
    ) -> "IAetherConfiguration":
        """
        Set whether automatic channel logger resolution is enabled.

        Args:
            enabled:
                True when `resolve_channel_logger(...)` may auto-attach a
                logger for callers that opt into that path.

        Returns:
            IAetherConfiguration: This configuration instance.
        """
        ...

    def with_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> "IAetherConfiguration":
        """
        Set the channel logger resolver used by the utility system.

        Args:
            resolver:
                Resolver callable or None.

        Returns:
            IAetherConfiguration: This configuration instance.
        """
        ...

    def with_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> "IAetherConfiguration":
        """
        Set the stdlib fallback logger used by the utility system.

        Args:
            logger:
                Fallback stdlib logger or None.

        Returns:
            IAetherConfiguration: This configuration instance.
        """
        ...

    def set_channel_logger_activation_enabled(self, enabled: bool) -> None:
        """
        Set the automatic channel logger activation flag.

        Args:
            enabled:
                Desired activation state.

        Returns:
            None.
        """
        ...

    def set_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> None:
        """
        Set the channel logger resolver.

        Args:
            resolver:
                Resolver callable or None.

        Returns:
            None.
        """
        ...

    def set_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> None:
        """
        Set the stdlib fallback logger.

        Args:
            logger:
                Fallback logger or None.

        Returns:
            None.
        """
        ...

    def validate(self) -> bool:
        """
        Validate the logger policy values.

        Returns:
            bool: True when the configuration is valid.
        """
        ...

    def freeze(self) -> None:
        """
        Validate and freeze the configuration.

        Returns:
            None.
        """
        ...

    def finalize(self) -> "IAetherConfiguration":
        """
        Validate and freeze the configuration, then return it.

        Returns:
            IAetherConfiguration: This configuration instance.
        """
        ...

    def activate(self) -> "IAetherConfiguration":
        """
        Validate, freeze, and mark the configuration active.

        Returns:
            IAetherConfiguration: This activated configuration instance.
        """
        ...
