import logging
import threading
from typing import Dict, Iterable, Optional

# Melder Imports
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.general_base.cleanable import Cleanable


class StdLoggerFactory(Cleanable):
    """
    Stdlib-backed logger factory that returns a SafeLogger for a given object.

    This factory manages a registry of loggers and controls their configuration (level, propagation, handlers)
    globally across the application.

    **Naming Convention:**
        Loggers are named using the format: `<ClassName>[<IDENT>]`

    **Identity Rules:**
        Creation requires a target object that MUST expose an `_id` attribute (must be stringifiable).

    **Behavior:**
    * **Central Registry:** Stores all created `SafeLogger` instances (keyed by logger name).
    * **Universal Level:** Maintains a single, global log level for all managed loggers.
    * **Handler Management:** Handlers added via `add_handler` are applied to all existing and future loggers.
    * **Thread-Safe:** All configuration changes and logger retrieval operations are thread-safe using an `RLock`.

    Notes:
    * Level configuration is handled by the factory, not by the individual `SafeLogger` instances.
    """

    def __init__(
            self,
            default_level: int = logging.INFO,
            propagate: bool = True,
            handlers: Optional[Iterable[logging.Handler]] = None,
            sync_root_with_global_level: bool = False,
    ) -> None:
        """
        Initializes the logger factory with default configuration settings.

        Args:
            default_level (int): Initial universal log level for all created loggers (e.g., `logging.INFO`).
            propagate (bool): Whether created loggers should propagate records to ancestor loggers.
            handlers (Optional[Iterable[logging.Handler]]): Optional iterable of handlers to attach to all loggers created by this factory.
            sync_root_with_global_level (bool): If True, calls to `set_global_level` will also set the level of the standard library's root logger for global consistency.
        """
        super().__init__()
        self._lock = threading.RLock()
        self._global_level: int = int(default_level)
        self._propagate: bool = bool(propagate)
        self._handlers: list[logging.Handler] = list(handlers) if handlers else []
        self._sync_root_with_global_level: bool = bool(sync_root_with_global_level)

        # Registry of SafeLogger by name
        self._loggers: Dict[str, SafeLogger] = {}

    def cleanup(self) -> None:
        """
        Idempotent teardown of the logger factory.

        Order:
          1) Detach factory-managed handlers from every managed logger.
          2) Attempt to cleanup SafeLogger instances (if they expose cleanup()).
          3) Flush/close factory-managed handlers.
          4) Clear registries and null heavy references.

        Notes:
          - Does NOT modify the stdlib root logger or third-party loggers.
          - Safe to call multiple times.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            # 1) Detach our handlers from every logger we manage
            if self._loggers:
                for safelogger in list(self._loggers.values()):
                    logger = safelogger._logger  # SafeLogger should expose the underlying stdlib logger
                    # Remove factory-managed handlers (avoid double-logs / handler leaks)
                    for h in list(self._handlers):
                        try:
                            logger.removeHandler(h)
                        except Exception:
                            pass

                    # 2) Best-effort cleanup for SafeLogger (optional API)
                    if hasattr(safelogger, "cleanup"):
                        try:
                            safelogger.cleanup()
                        except Exception:
                            pass

            # 3) Flush/close our handlers (we own them if users passed them to the factory)
            for h in list(self._handlers):
                try:
                    h.flush()
                except Exception:
                    pass
                try:
                    h.close()
                except Exception:
                    pass

            # 4) Clear registries and null heavy refs
            self._loggers.clear()
            self._handlers.clear()

            # Replace with fresh containers to drop references deterministically
            self._loggers = None
            self._handlers = None



    # ----------------------------
    # Public API
    # ----------------------------

    def __call__(self, obj) -> SafeLogger:
        """
        Public API

        Creates or retrieves a `SafeLogger` for the given object based on the factory's naming convention.

        Args:
            obj (Any): The object instance to create the logger for. It **must** expose a stringifiable `_id` attribute.

        Returns:
            SafeLogger: The requested or newly created logger instance.

        Raises:
            AttributeError: If the input object does not have a readable `_id` attribute.
        """
        try:
            ident = str(obj._id)
        except AttributeError as e:
            raise AttributeError(
                f"Object of type {obj.__class__.__name__} must have an '_id' attribute for logging."
            ) from e

        name = f"{obj.__class__.__name__}[{ident}]"
        return self._get_or_create(name)

    def make_with_id(self, class_name: str, ident: str) -> SafeLogger:
        """
        Public API

        Creates or retrieves a `SafeLogger` using explicit class name and identifier strings, bypassing the need for an object instance.

        Args:
            class_name (str): The class name portion of the logger name.
            ident (str): The identifier portion (e.g., UUID or unique name).

        Returns:
            SafeLogger: The requested or newly created logger instance.
        """
        self.check_cleaned()
        name = f"{class_name}[{ident}]"
        return self._get_or_create(name)

    def set_global_level(self, level: int) -> None:
        """
        Public API

        Sets the universal log level for all existing and future loggers managed by this factory.

        If `sync_root_with_global_level` was set to True during initialization, this also updates the standard library's root logger.

        Args:
            level (int): The new universal log level (e.g., `logging.DEBUG`).
        """
        self.check_cleaned()
        with self._lock:
            self._global_level = int(level)
            for safe_logger in self._loggers.values():
                logger = safe_logger._logger  # SafeLogger should expose underlying logger via .logger
                logger.setLevel(self._global_level)
            if self._sync_root_with_global_level:
                logging.getLogger().setLevel(self._global_level)

    def get_global_level(self) -> int:
        """
        Public API

        Returns the current universal log level set for all managed loggers.

        Returns:
            int: The current global log level.
        """
        self.check_cleaned()
        with self._lock:
            return self._global_level

    def set_propagate(self, propagate: bool) -> None:
        """
        Public API

        Controls whether all existing and future loggers should propagate log records to their ancestor loggers.

        Args:
            propagate (bool): True to enable propagation, False to disable.
        """
        self.check_cleaned()
        with self._lock:
            self._propagate = bool(propagate)
            for safe_logger in self._loggers.values():
                safe_logger._logger.propagate = self._propagate

    def add_handler(self, handler: logging.Handler) -> None:
        """
        Public API

        Adds a standard library `logging.Handler` to all existing loggers and registers it as a default for all future loggers.

        Args:
            handler (logging.Handler): The handler instance to add.
        """
        self.check_cleaned()
        if handler is None:
            return
        with self._lock:
            self._handlers.append(handler)
            for safe_logger in self._loggers.values():
                # Avoid duplicate handler instances on the same logger
                if handler not in safe_logger._logger.handlers:
                    safe_logger._logger.addHandler(handler)

    def remove_handler(self, handler: logging.Handler) -> None:
        """
        Public API

        Removes a standard library `logging.Handler` from all existing loggers and removes it from the list of future defaults.

        Args:
            handler (logging.Handler): The handler instance to remove.
        """
        self.check_cleaned()
        if handler is None:
            return
        with self._lock:
            # Update future defaults
            self._handlers = [h for h in self._handlers if h is not handler]
            # Update existing
            for safe_logger in self._loggers.values():
                try:
                    safe_logger._logger.removeHandler(handler)
                except Exception:
                    # We avoid being noisy in teardown paths
                    pass

    def set_formatter(self, formatter: logging.Formatter) -> None:
        """
        Public API

        Applies a `logging.Formatter` to all handlers currently attached to loggers managed by this factory.

        Args:
            formatter (logging.Formatter): The formatter instance to apply.
        """
        self.check_cleaned()
        if formatter is None:
            return
        with self._lock:
            for safe_logger in self._loggers.values():
                for h in safe_logger._logger.handlers:
                    try:
                        h.setFormatter(formatter)
                    except Exception:
                        # Ignore handler-specific formatter errors
                        pass

    def get_logger_by_name(self, name: str) -> Optional[SafeLogger]:
        """
        Public API

        Retrieves a previously created `SafeLogger` instance by its full logger name.

        Args:
            name (str): The exact name of the logger to retrieve (e.g., `ClassName[IDENT]`).

        Returns:
            Optional[SafeLogger]: The managed logger instance, or None if not found in the registry.
        """
        self.check_cleaned()
        with self._lock:
            return self._loggers.get(name)

    def all_logger_names(self) -> list[str]:
        """
        Public API

        Returns a snapshot list of the names of all loggers currently managed by this factory.

        Returns:
            list[str]: A list of all managed logger names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._loggers.keys())

    def clear_registry(self) -> None:
        """
        Public API

        Clears the factory's internal registry of managed logger instances.

        This does **not** disable or remove the underlying loggers from the standard library's global logger tree;
        it only stops this factory from tracking them. Useful for tests or memory cleanup.
        """
        self.check_cleaned()
        with self._lock:
            self._loggers.clear()

    # ----------------------------
    # Internal helpers
    # ----------------------------

    def _get_or_create(self, name: str) -> SafeLogger:
        """
        Internal

        Retrieves an existing `SafeLogger` from the registry or creates a new one, applying all global settings.

        Args:
            name (str): The full logger name.

        Returns:
            SafeLogger: The managed logger instance.
        """
        self.check_cleaned()
        with self._lock:
            existing = self._loggers.get(name)
            if existing is not None:
                return existing

            base_logger = logging.getLogger(name)
            base_logger.setLevel(self._global_level)
            base_logger.propagate = self._propagate

            # Attach any default handlers requested for all loggers
            for h in self._handlers:
                if h not in base_logger.handlers:
                    base_logger.addHandler(h)

            safe = SafeLogger(base_logger)
            self._loggers[name] = safe
            return safe