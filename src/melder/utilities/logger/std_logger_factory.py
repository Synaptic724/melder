import logging
import threading
from typing import Dict, Iterable, Optional

# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
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
    * **Universal Level:** Maintains a single, global log level for all managed loggers. You can set it
      numerically via `set_global_level(int)` or symbolically via `set_global_level_by_name(str)`. Symbolic
      names must be keys in `SafeLogger._LEVELS` (e.g., "debug", "info", ...).
    * **Handler Management:** Handlers added via `add_handler` are applied to all existing and future loggers.
    * **Propagation:** The propagate flag is applied to all existing and future loggers.
    * **Root Sync (optional):** If enabled, updates the stdlib root logger’s level when global level changes.
    * **Thread-Safe:** All configuration changes and logger retrieval operations are thread-safe using an `RLock`.

    Notes:
    * Level configuration is handled by the factory, not by the individual `SafeLogger` instances, but the
      factory drives changes through `SafeLogger.set_level(...)` / `.set_level_by_name(...)` so internal
      thresholds stay consistent.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = (
        *Cleanable.__slots__,
        "_lock",
        "_global_level",
        "_global_level_name",
        "_propagate",
        "_handlers",
        "_sync_root_with_global_level",
        "_loggers",
    )

    def __init__(
            self,
            default_level: int = logging.INFO,
            *,
            default_level_name: Optional[str] = None,
            propagate: bool = True,
            handlers: Optional[Iterable[logging.Handler]] = None,
            sync_root_with_global_level: bool = False,
    ) -> None:
        """
        Initializes the logger factory with default configuration settings.

        Args:
            default_level (int): Initial universal log level for all created loggers (e.g., `logging.INFO`).
            default_level_name (Optional[str]): Symbolic level name to initialize with (e.g., "info").
                If both `default_level_name` and `default_level` are provided, the name wins.
            propagate (bool): Whether created loggers should propagate records to ancestor loggers.
            handlers (Optional[Iterable[logging.Handler]]): Optional iterable of handlers to attach to all loggers
                created by this factory.
            sync_root_with_global_level (bool): If True, calls to `set_global_level` / `set_global_level_by_name`
                will also set the level of the stdlib root logger for global consistency.
        """
        super().__init__()
        self._lock = threading.RLock()
        self._handlers: list[logging.Handler] = list(handlers) if handlers else []
        self._sync_root_with_global_level = bool(sync_root_with_global_level)
        self._loggers: Dict[str, SafeLogger] = {}

        # Resolve initial level
        if default_level_name is not None:
            name = default_level_name.lower()
            if name not in SafeLogger._LEVELS:
                raise ValueError(f"Invalid log level name '{default_level_name}'. Expected one of: {list(SafeLogger._LEVELS)}")
            self._global_level_name = name
            self._global_level = SafeLogger._LEVELS[name]
        else:
            self._global_level = int(default_level)
            reverse = {v: k for k, v in SafeLogger._LEVELS.items()}
            self._global_level_name = reverse.get(self._global_level, "notset")

        self._propagate = bool(propagate)

        if self._sync_root_with_global_level:
            logging.getLogger().setLevel(self._global_level)

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
                    logger = safelogger._logger
                    if logger is not None:
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
            self._loggers = None
            self._handlers = None

    # ----------------------------
    # Public API
    # ----------------------------

    def __call__(self, obj) -> SafeLogger:
        """
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
        Creates or retrieves a `SafeLogger` using explicit class name and identifier strings,
        bypassing the need for an object instance.

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
        Sets the universal numeric log level for all existing and future loggers managed by this factory.

        Args:
            level (int): The new universal log level (e.g., `logging.DEBUG`).
        """
        self.check_cleaned()
        with self._lock:
            self._global_level = int(level)
            reverse = {v: k for k, v in SafeLogger._LEVELS.items()}
            self._global_level_name = reverse.get(self._global_level, "notset")

            for safe_logger in self._loggers.values():
                safe_logger.set_level(self._global_level)

            if self._sync_root_with_global_level:
                logging.getLogger().setLevel(self._global_level)

    def set_global_level_by_name(self, level_name: str) -> None:
        """
        Sets the universal symbolic log level for all existing and future loggers.

        Args:
            level_name (str): A level name present in `SafeLogger._LEVELS` (e.g., "debug", "info", ...).

        Raises:
            ValueError: If `level_name` is not a recognized level name.
        """
        self.check_cleaned()
        normalized = level_name.lower()
        if normalized not in SafeLogger._LEVELS:
            raise ValueError(f"Invalid log level name '{level_name}'. Expected one of: {list(SafeLogger._LEVELS)}")

        with self._lock:
            self._global_level_name = normalized
            self._global_level = SafeLogger._LEVELS[normalized]

            for safe_logger in self._loggers.values():
                safe_logger.set_level_by_name(normalized)

            if self._sync_root_with_global_level:
                logging.getLogger().setLevel(self._global_level)

    def get_global_level(self) -> int:
        """
        Returns the current universal numeric log level set for all managed loggers.

        Returns:
            int: The current global log level.
        """
        self.check_cleaned()
        with self._lock:
            return self._global_level

    def get_global_level_name(self) -> str:
        """
        Returns the current universal symbolic log level set for all managed loggers.

        Returns:
            str: The current global log level name.
        """
        self.check_cleaned()
        with self._lock:
            return self._global_level_name

    def set_propagate(self, propagate: bool) -> None:
        """
        Controls whether all existing and future loggers should propagate log records to their ancestor loggers.

        Args:
            propagate (bool): True to enable propagation, False to disable.
        """
        self.check_cleaned()
        with self._lock:
            self._propagate = bool(propagate)
            for safe_logger in self._loggers.values():
                if safe_logger._logger is not None:
                    safe_logger._logger.propagate = self._propagate

    def add_handler(self, handler: logging.Handler) -> None:
        """
        Adds a standard library `logging.Handler` to all existing loggers and registers it
        as a default for all future loggers.

        Args:
            handler (logging.Handler): The handler instance to add.
        """
        self.check_cleaned()
        if handler is None:
            return
        with self._lock:
            self._handlers.append(handler)
            for safe_logger in self._loggers.values():
                base = safe_logger._logger
                if base is not None and handler not in base.handlers:
                    base.addHandler(handler)

    def remove_handler(self, handler: logging.Handler) -> None:
        """
        Removes a standard library `logging.Handler` from all existing loggers and
        removes it from the list of future defaults.

        Args:
            handler (logging.Handler): The handler instance to remove.
        """
        self.check_cleaned()
        if handler is None:
            return
        with self._lock:
            self._handlers = [h for h in self._handlers if h is not handler]
            for safe_logger in self._loggers.values():
                base = safe_logger._logger
                if base is not None:
                    try:
                        base.removeHandler(handler)
                    except Exception:
                        pass

    def set_formatter(self, formatter: logging.Formatter) -> None:
        """
        Applies a `logging.Formatter` to all handlers currently attached to loggers managed by this factory.

        Args:
            formatter (logging.Formatter): The formatter instance to apply.
        """
        self.check_cleaned()
        if formatter is None:
            return
        with self._lock:
            for safe_logger in self._loggers.values():
                base = safe_logger._logger
                if base is None:
                    continue
                for h in base.handlers:
                    try:
                        h.setFormatter(formatter)
                    except Exception:
                        pass

    def get_logger_by_name(self, name: str) -> Optional[SafeLogger]:
        """
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
        Returns a snapshot list of the names of all loggers currently managed by this factory.

        Returns:
            list[str]: A list of all managed logger names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._loggers.keys())

    def clear_registry(self) -> None:
        """
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
        Retrieves an existing `SafeLogger` from the registry or creates a new one,
        applying the factory’s current global settings (level, propagate, handlers).

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

            for h in self._handlers:
                if h not in base_logger.handlers:
                    base_logger.addHandler(h)

            safe = SafeLogger(base_logger)
            # ensure the SafeLogger mirrors our chosen level representation
            safe.set_level(self._global_level)
            self._loggers[name] = safe
            return safe
