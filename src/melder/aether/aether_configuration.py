import logging
from pathlib import Path
import threading
from typing import Any, Callable, ClassVar, Dict, Optional, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class AetherConfiguration(Cleanable):
    """
    Mutable-to-frozen configuration surface for Aether root policy.

    Purpose:
        Hold process-wide Aether policy inputs before the root applies them to
        hosted subsystems. The current owned policy slices are logger
        activation control for `AetherUtilitySystem` and the root-level
        system-caching posture used by later cache-aware runtime layers.

    Contract:
        - mutable until frozen
        - activation is explicit and implies successful validation/freeze
        - automatic channel logger activation is disabled by default
        - system caching is enabled by default
        - the default cache root is the package-relative `__melder_cache__`
          directory under the installed `melder` package root
        - explicit logger attachment remains outside this config surface
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frozen",
        "_activated",
        "_properties",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty Aether configuration with the default logger policy.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frozen: bool = False
        self._activated: bool = False
        self._properties: Dict[str, object] = {
            "system_caching_enabled": True,
            "system_cache_root_path": self._build_default_system_cache_root_path(),
            "channel_logger_activation_enabled": False,
            "channel_logger_resolver": None,
            "default_logger": None,
        }

    @staticmethod
    def _build_default_system_cache_root_path() -> Path:
        """
        Build the default package-relative cache root path.

        Returns:
            Path:
                Relative cache-root fragment that later runtime consumers
                resolve under the installed `melder` package root.
        """
        return Path("__melder_cache__")

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
            bool: True when the mutation is closed.
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
        value = self._properties["channel_logger_activation_enabled"]
        if not isinstance(value, bool):
            raise TypeError(
                "channel_logger_activation_enabled must remain a bool."
            )
        return value

    @property
    def system_caching_enabled(self) -> bool:
        """
        Return whether root-level system caching is enabled.

        Returns:
            bool:
                True when later runtime layers may treat system caching as
                globally enabled by policy.
        """
        self.check_cleaned()
        value = self._properties["system_caching_enabled"]
        if not isinstance(value, bool):
            raise TypeError("system_caching_enabled must remain a bool.")
        return value

    @property
    def system_cache_root_path(self) -> Path:
        """
        Return the configured root directory for cache artifacts.

        Returns:
            Path:
                Package-relative cache root path for all Melder cache data.
        """
        self.check_cleaned()
        value = self._properties["system_cache_root_path"]
        if not isinstance(value, Path):
            raise TypeError("system_cache_root_path must remain a Path.")
        return value

    def resolve_system_cache_root_path(self) -> Path:
        """
        Resolve the configured cache-root fragment against the melder package root.

        Returns:
            Path:
                Absolute cache root path under the installed `melder` package
                directory.
        """
        self.check_cleaned()
        return Path(__file__).resolve().parent.parent / self.system_cache_root_path

    @property
    def channel_logger_resolver(self) -> Optional[Callable[..., Any]]:
        """
        Return the configured channel logger resolver, if any.

        Returns:
            Optional[Callable[..., Any]]: Configured resolver.
        """
        self.check_cleaned()
        value = self._properties["channel_logger_resolver"]
        if value is not None and not callable(value):
            raise TypeError(
                "channel_logger_resolver must remain callable or None."
            )
        return value

    @property
    def default_logger(self) -> Optional[logging.Logger]:
        """
        Return the configured stdlib fallback logger, if any.

        Returns:
            Optional[logging.Logger]: Configured default logger.
        """
        self.check_cleaned()
        value = self._properties["default_logger"]
        if value is not None and not isinstance(value, logging.Logger):
            raise TypeError("default_logger must remain logging.Logger or None.")
        return value

    def with_defaults(self) -> "AetherConfiguration":
        """
        Apply the default Aether logger policy.

        Returns:
            AetherConfiguration: This configuration instance.
        """
        self.set_system_caching_enabled(True)
        self.set_system_cache_root_path(
            self._build_default_system_cache_root_path()
        )
        self.set_channel_logger_activation_enabled(False)
        self.set_channel_logger_resolver(None)
        self.set_default_logger(None)
        return self

    def with_system_caching_enabled(
            self,
            enabled: bool,
    ) -> "AetherConfiguration":
        """
        Set whether root-level system caching is enabled.

        Args:
            enabled:
                True when the runtime should treat system caching as enabled by
                default.

        Returns:
            AetherConfiguration:
                This configuration instance.
        """
        self.set_system_caching_enabled(enabled)
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

    def with_system_cache_root_path(
            self,
            root_path: Union[str, Path],
    ) -> "AetherConfiguration":
        """
        Set the root directory used for all Melder cache data.

        Args:
            root_path:
                Relative cache-root override anchored under the installed
                `melder` package root.

        Returns:
            AetherConfiguration:
                This configuration instance.
        """
        self.set_system_cache_root_path(root_path)
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

    def set_system_caching_enabled(self, enabled: bool) -> None:
        """
        Set the root-level system-caching policy flag.

        Args:
            enabled:
                Desired system-caching state.

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
            self._properties["system_caching_enabled"] = enabled

    def set_system_cache_root_path(
            self,
            root_path: Union[str, Path],
    ) -> None:
        """
        Set the root directory used for all Melder cache data.

        Args:
            root_path:
                Relative cache-root override anchored under the installed
                `melder` package root.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the configuration is frozen.
            TypeError:
                If `root_path` is not path-like or is absolute.
        """
        self.check_cleaned()
        if self._frozen:
            raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
        if not isinstance(root_path, (str, Path)):
            raise TypeError("root_path must be a str or Path.")
        normalized_root_path = Path(root_path)
        if normalized_root_path.is_absolute():
            raise ValueError("root_path must remain relative to the melder package root.")
        with self._lock:
            if self._frozen:
                raise RuntimeError("Cannot modify AetherConfiguration after freeze().")
            self._properties["system_cache_root_path"] = normalized_root_path

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
        if not isinstance(self._properties["system_caching_enabled"], bool):
            raise ValueError("system_caching_enabled must be a bool.")
        if not isinstance(self._properties["system_cache_root_path"], Path):
            raise ValueError("system_cache_root_path must be a Path.")
        if self._properties["system_cache_root_path"].is_absolute():
            raise ValueError(
                "system_cache_root_path must remain relative to the melder package root."
            )
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
