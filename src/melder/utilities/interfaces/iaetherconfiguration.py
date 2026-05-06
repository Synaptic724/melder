import logging
from typing import Any, Callable, Optional, Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ichannellogger import IChannelLogger


@runtime_checkable
class IAetherConfiguration(ICleanable, Protocol):
    """
    Structural contract for Aether root configuration.
    """

    @property
    def channel_logger_activation_enabled(self) -> bool:
        ...

    @property
    def channel_logger_resolver(self) -> Optional[Callable[..., Any]]:
        ...

    @property
    def default_logger(self) -> Optional[logging.Logger]:
        ...

    def with_defaults(self) -> "IAetherConfiguration":
        ...

    def with_channel_logger_activation_enabled(
            self,
            enabled: bool,
    ) -> "IAetherConfiguration":
        ...

    def with_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> "IAetherConfiguration":
        ...

    def with_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> "IAetherConfiguration":
        ...

    def freeze(self) -> None:
        ...

    def finalize(self) -> "IAetherConfiguration":
        ...

    def activate(self) -> "IAetherConfiguration":
        ...
