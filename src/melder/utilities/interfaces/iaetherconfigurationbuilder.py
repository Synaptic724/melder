import logging
from typing import Any, Callable, Optional, Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iaetherconfiguration import IAetherConfiguration


@runtime_checkable
class IAetherConfigurationBuilder(ICleanable, Protocol):
    """
    One-shot builder for Aether root configuration assembly.

    Purpose:
        Mirror the repo's mutable-then-finalize configuration style while
        making ownership explicit for the wrapped `IAetherConfiguration`.

    Contract:
        - Owns exactly one mutable Aether configuration until build/finalize/
          activate transfers that ownership.
        - Builder mutators return the same builder for fluent chaining.
        - `build()` transfers the mutable configuration without freezing it.
        - `finalize()` transfers the frozen configuration.
        - `activate()` transfers the activated configuration.
    """

    def cleanup(self) -> None:
        """
        Idempotently clean the builder and any still-owned configuration.

        Returns:
            None.
        """
        ...

    def with_defaults(self) -> "IAetherConfigurationBuilder":
        """
        Apply the default Aether logger policy.

        Returns:
            IAetherConfigurationBuilder: This builder.
        """
        ...

    def with_channel_logger_activation_enabled(
            self,
            enabled: bool,
    ) -> "IAetherConfigurationBuilder":
        """
        Set the automatic channel logger activation flag.

        Args:
            enabled:
                Desired activation state.

        Returns:
            IAetherConfigurationBuilder: This builder.
        """
        ...

    def with_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> "IAetherConfigurationBuilder":
        """
        Set the channel logger resolver.

        Args:
            resolver:
                Resolver callable or None.

        Returns:
            IAetherConfigurationBuilder: This builder.
        """
        ...

    def with_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> "IAetherConfigurationBuilder":
        """
        Set the stdlib fallback logger.

        Args:
            logger:
                Fallback logger or None.

        Returns:
            IAetherConfigurationBuilder: This builder.
        """
        ...

    def build(self) -> IAetherConfiguration:
        """
        Transfer the wrapped mutable configuration to the caller.

        Returns:
            IAetherConfiguration: Wrapped configuration instance.
        """
        ...

    def finalize(self) -> IAetherConfiguration:
        """
        Finalize and transfer the wrapped configuration to the caller.

        Returns:
            IAetherConfiguration: Frozen configuration instance.
        """
        ...

    def activate(self) -> IAetherConfiguration:
        """
        Activate and transfer the wrapped configuration to the caller.

        Returns:
            IAetherConfiguration: Activated configuration instance.
        """
        ...
