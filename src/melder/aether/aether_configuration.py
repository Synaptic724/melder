import logging
import threading
from typing import Any, Callable, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces import IAetherConfiguration
from melder.utilities.helpers.id_builder import IDBuilder


class AetherConfiguration(Cleanable, IAetherConfiguration):
    """
    Mutable-to-frozen configuration surface for Aether root policy.

    Purpose:
        Hold process-wide Aether policy inputs before the root applies them to
        hosted subsystems. The first owned policy slice is logger activation
        control for `AetherUtilitySystem`.

    Contract:
        - mutable until frozen
        - activation is explicit and implies successful validation/freeze
        - automatic channel logger activation is disabled by default
        - explicit logger attachment remains outside this config surface
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_activated",
        "_properties",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty Aether configuration with default logger policy.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._activated: bool = False
        self._properties: Dict[str, object] = {
            "channel_logger_activation_enabled": False,
            "channel_logger_resolver": None,
            "default_logger": None,
        }

    def cleanup(self) -> None:
        """
        Idempotently clear configuration state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._frozen = True
            self._activated = False
            self._properties.clear()

            del self._properties
            del self._id

    @property
    def id(self) -> str:
        """
        Return the stable configuration id.

        Returns:
            str: Stable configuration id.
        """
        self.check_cleaned()
        return self._id

    @property
    def frozen(self) -> bool:
        """
        Return whether the configuration is frozen.

        Returns:
            bool: True when mutation is closed.
        """
        self.check_cleaned()
        return self._frozen

    @property
    def activated(self) -> bool:
        """
        Return whether the configuration has been activated.

        Returns:
            bool: True when validated, frozen, and marked ready for Aether.
        """
        self.check_cleaned()
        return self._activated

    @property
    def channel_logger_activation_enabled(self) -> bool:
        """
        Return whether automatic channel logger activation is enabled.

        Returns:
            bool: True when `resolve_channel_logger(...)` may auto-attach.
        """
        self.check_cleaned()
        return self._properties["channel_logger_activation_enabled"]

    @property
    def channel_logger_resolver(self) -> Optional[Callable[..., Any]]:
        """
        Return the configured channel logger resolver, if any.

        Returns:
            Optional[Callable[..., Any]]: Configured resolver.
        """
        self.check_cleaned()
        return self._properties["channel_logger_resolver"]

    @property
    def default_logger(self) -> Optional[logging.Logger]:
        """
        Return the configured stdlib fallback logger, if any.

        Returns:
            Optional[logging.Logger]: Configured default logger.
        """
        self.check_cleaned()
        return self._properties["default_logger"]

    def with_defaults(self) -> "AetherConfiguration":
        """
        Apply the default Aether logger policy.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_channel_logger_activation_enabled(False)
        self.set_channel_logger_resolver(None)
        self.set_default_logger(None)
        return self

    def with_channel_logger_activation_enabled(
            self,
            enabled: bool,
    ) -> "AetherConfiguration":
        """
        Set whether automatic channel logger resolution is enabled.

        Args:
            enabled:
                True when `resolve_channel_logger(...)` may auto-attach a
                logger for callers that opt into that path.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_channel_logger_activation_enabled(enabled)
        return self

    def with_channel_logger_resolver(
            self,
            resolver: Optional[Callable[..., Any]],
    ) -> "AetherConfiguration":
        """
        Set the channel logger resolver used by the utility system.

        Args:
            resolver:
                Resolver callable or None.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_channel_logger_resolver(resolver)
        return self

    def with_default_logger(
            self,
            logger: Optional[logging.Logger],
    ) -> "AetherConfiguration":
        """
        Set the stdlib fallback logger used by the utility system.

        Args:
            logger:
                Fallback stdlib logger or None.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_default_logger(logger)
        return self

    def set_channel_logger_activation_enabled(self, enabled: bool) -> None:
        """
        Set the automatic channel logger activation flag.

        Args:
            enabled:
                Desired activation state.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration is frozen.
            TypeError:
                If `enabled` is not a bool.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a bool.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
            self._properties["channel_logger_activation_enabled"] = enabled

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

        Raises:
            RuntimeError:
                If the configuration is frozen.
            TypeError:
                If `resolver` is neither callable nor None.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
        if resolver is not None and not callable(resolver):
            raise TypeError("resolver must be callable or None.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
            self._properties["channel_logger_resolver"] = resolver

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

        Raises:
            RuntimeError:
                If the configuration is frozen.
            TypeError:
                If `logger` is neither `logging.Logger` nor None.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
        if logger is not None and not isinstance(logger, logging.Logger):
            raise TypeError("logger must be logging.Logger or None.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
            self._properties["default_logger"] = logger

    def validate(self) -> bool:
        """
        Validate the logger policy values.

        Returns:
            bool: True when the configuration is valid.
        """
        self.check_cleaned()
        if not isinstance(self._properties["channel_logger_activation_enabled"], bool):
            raise ValueError("channel_logger_activation_enabled must be a bool.")
        if (
                self._properties["channel_logger_resolver"] is not None
                and not callable(self._properties["channel_logger_resolver"])
        ):
            raise ValueError("channel_logger_resolver must be callable or None.")
        if (
                self._properties["default_logger"] is not None
                and not isinstance(self._properties["default_logger"], logging.Logger)
        ):
            raise ValueError(
                "default_logger must be logging.Logger or None."
            )
        return True

    def freeze(self) -> None:
        """
        Validate and freeze the configuration.

        Returns:
            None.
        """
        self.check_cleaned()
        if self._frozen:
            return
        if not self.validate():
            raise ValueError("AetherConfiguration validation failed.")
        with self._lock:
            self._frozen = True

    def finalize(self) -> "AetherConfiguration":
        """
        Validate and freeze the configuration, then return it.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.freeze()
        return self

    def activate(self) -> "AetherConfiguration":
        """
        Validate, freeze, and mark the configuration active.

        Returns:
            AetherConfiguration: This activated configuration instance.
        """
        self.freeze()
        with self._lock:
            self._activated = True
        return self
