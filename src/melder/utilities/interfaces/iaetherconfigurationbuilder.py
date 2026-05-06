import logging
from typing import Any, Callable, Optional, Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iaetherconfiguration import IAetherConfiguration


@runtime_checkable
class IAetherConfigurationBuilder(ICleanable, Protocol):
    """
    Structural contract for the one-shot Aether configuration builder.
    """

    def with_defaults(self) -> "IAetherConfigurationBuilder":
        ...

    def with_channel_logger_activation_enabled(
            self,
            enabled: bool,
    ) -> "IAetherConfigurationBuilder":
        ...

    def with_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> "IAetherConfigurationBuilder":
        ...

    def with_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> "IAetherConfigurationBuilder":
        ...

    def build(self) -> IAetherConfiguration:
        ...

    def finalize(self) -> IAetherConfiguration:
        ...

    def activate(self) -> IAetherConfiguration:
        ...
