import logging
import threading
from typing import Any, Callable, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aether_configuration import AetherConfiguration
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces import IAetherConfigurationBuilder


class AetherConfigurationBuilder(Cleanable, IAetherConfigurationBuilder):
    """
    One-shot builder for Aether root configuration assembly.

    Purpose:
        Mirror the repo's mutable-then-finalize configuration style while
        making ownership explicit for the wrapped `AetherConfiguration`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_configuration",
    ]

    def __init__(self) -> None:
        """
        Initialize one builder with a fresh Aether configuration.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._configuration: AetherConfiguration = AetherConfiguration()

    def cleanup(self) -> None:
        """
        Idempotently cleanup the builder and any still-owned configuration.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._configuration is not None:
                self._configuration.cleanup()
            del self._configuration
            del self._id

    def with_defaults(self) -> "AetherConfigurationBuilder":
        """
        Apply the default Aether logger policy.

        Returns:
            AetherConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        self._configuration.with_defaults()
        return self

    def with_channel_logger_activation_enabled(
            self,
            enabled: bool,
    ) -> "AetherConfigurationBuilder":
        """
        Set the automatic channel logger activation flag.

        Returns:
            AetherConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        self._configuration.with_channel_logger_activation_enabled(enabled)
        return self

    def with_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> "AetherConfigurationBuilder":
        """
        Set the channel logger resolver.

        Returns:
            AetherConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        self._configuration.with_channel_logger_resolver(resolver)
        return self

    def with_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> "AetherConfigurationBuilder":
        """
        Set the stdlib fallback logger.

        Returns:
            AetherConfigurationBuilder: This builder.
        """
        self.check_cleaned()
        self._configuration.with_default_logger(logger)
        return self

    def build(self) -> AetherConfiguration:
        """
        Transfer the wrapped mutable configuration to the caller.

        Returns:
            AetherConfiguration: Wrapped configuration instance.
        """
        self.check_cleaned()
        return self._handoff_configuration()

    def finalize(self) -> AetherConfiguration:
        """
        Finalize and transfer the wrapped configuration to the caller.

        Returns:
            AetherConfiguration: Frozen configuration instance.
        """
        self.check_cleaned()
        self._configuration.finalize()
        return self._handoff_configuration()

    def activate(self) -> AetherConfiguration:
        """
        Activate and transfer the wrapped configuration to the caller.

        Returns:
            AetherConfiguration: Activated configuration instance.
        """
        self.check_cleaned()
        self._configuration.activate()
        return self._handoff_configuration()

    def _handoff_configuration(self) -> AetherConfiguration:
        """
        Transfer builder-owned configuration ownership to the caller.

        Returns:
            AetherConfiguration: The configuration previously owned by this builder.
        """
        with self._lock:
            if self._configuration is None:
                raise RuntimeError(
                    "AetherConfigurationBuilder no longer owns a configuration."
                )
            configuration = self._configuration
            self._configuration = None
            self.cleanup()
        return configuration
