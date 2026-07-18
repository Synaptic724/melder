import logging
from typing import Optional, Iterable, Dict, Any, Union, ClassVar, List



# Melder imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.ichannellogger import IChannelLogger
from melder.utilities.helpers.id_builder import IDBuilder



class SafeLogger(Cleanable):
    """
    Unified logger adapter over channel loggers and stdlib loggers.

    `SafeLogger` gives the rest of the runtime one stable logging surface while
    hiding the differences between `IChannelLogger` implementations and plain
    `logging.Logger` instances.

    Contract:
    - Accepts either an `IChannelLogger`, a stdlib `logging.Logger`, or `None`.
    - Preserves channel-specific stack metadata when the wrapped logger is a
      channel logger.
    - Ignores channel-only masking semantics on stdlib logger paths.
    - Falls back to a no-op surface when no logger is configured.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_logger", "_id", "_level", "_level_name", "_is_channel"]
    _LEVELS: ClassVar[Dict[str, int]] = {
        "notset": logging.NOTSET,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    def __init__(self, logger: logging.Logger | IChannelLogger | None, level_name: str = "INFO"):
        """
        Initialize the logger adapter around one concrete logger or null target.

        Contract:
        - Accepts either an `IChannelLogger`, stdlib `logging.Logger`, or
          `None`.
        - Normalizes the configured level name immediately.
        - Pushes the resolved level onto the wrapped logger when a concrete
          logger is present.
        """
        super().__init__()
        self._id = IDBuilder.create_id()
        if logger is not None and not isinstance(logger, (logging.Logger, IChannelLogger)):
            raise TypeError(
                f"SafeLogger expects a logging.Logger or IChannelLogger instance or None, "
                f"got {type(logger).__name__} instead."
            )
        self._logger: Optional[Union[logging.Logger, IChannelLogger]] = logger
        self._is_channel = isinstance(logger, IChannelLogger)
        normalized = level_name.lower()
        if normalized not in self._LEVELS:
            raise ValueError(f"Invalid log level name '{level_name}'. Expected one of: {list(self._LEVELS)}")
        self._level_name = normalized
        self._level = self._LEVELS[normalized]
        if logger is not None:
            logger.setLevel(self._level)

    def cleanup(self) -> None:
        """
        Idempotently release the wrapped logger reference.

        Contract:
        - Safe to call multiple times; only the first call performs teardown.
        - If the wrapped logger exposes `cleanup()`, this method attempts to
          call it once on teardown.
        - Always clears the local logger reference afterward.
        - Marks this adapter cleaned per the `Cleanable` contract: `cleaned`
          reads True and `check_cleaned()` refuses use-after-clean, while the
          emit surface stays a safe no-op through the null-logger path.
        - Does not assume stdlib loggers own a cleanup lifecycle.
        """
        if self._cleaned:
            return
        # Allow external polymorphic cleanup; std loggers won't have it.
        if self._logger is not None and hasattr(self._logger, "cleanup"):
            try:
                self._logger.cleanup()
            except Exception:
                pass
        self._logger = None
        # BUG-147 (2026-07-17 audit): terminal cleanup must flip the Cleanable
        # lifecycle flag so owners and diagnostics can distinguish a cleaned
        # adapter from an active silent one.
        self._cleaned = True

    @property
    def is_attached(self) -> bool:
        """
        Return whether a concrete logger sink is currently attached.

        Purpose:
            Give hot-path callers one cheap pre-flight check so they can skip
            building log messages and keyword payloads entirely when this
            adapter is a null surface.

        Contract:
            - True when a concrete `IChannelLogger` or stdlib `logging.Logger`
              is wrapped.
            - False for the null-logger surface, including after `cleanup()`
              has released the wrapped reference.
            - Does not consider the active level threshold; callers that gate
              on this still rely on `_emit(...)` level filtering for
              attached-but-quiet sinks.

        Returns:
            bool: True when log calls can reach a concrete sink.
        """
        return self._logger is not None

    def set_level_by_name(self, level_name: str) -> None:
        """
        Set the active log level by symbolic name.

        Contract:
        - Normalizes the supplied level name to lowercase.
        - Updates the wrapped logger immediately when one exists.
        - Rejects unsupported symbolic names instead of silently coercing them.
        """
        normalized = level_name.lower()
        if normalized not in self._LEVELS:
            raise ValueError(f"Invalid log level name '{level_name}'. Expected one of: {list(self._LEVELS)}")
        self._level_name = normalized
        self._level = self._LEVELS[normalized]
        if self._logger is not None:
            self._logger.setLevel(self._level)

    def set_level(self, level: int) -> None:
        """
        Set the active log level by its numeric logging value.

        Contract:
        - Rejects values that are not one of the known stdlib logging levels.
        - Updates the wrapped logger immediately when one exists.
        - Keeps `_level_name` as the last symbolic value set; numeric updates
          only adjust the active threshold.
        """
        if level not in self._LEVELS.values():
            raise ValueError(f"Invalid numeric log level: {level}")
        self._level = level
        if self._logger is not None:
            self._logger.setLevel(level)

    # ---- Internal unified emitter -------------------------------------------------

    def _emit_channel(
            self,
            logger: Any,
            *,
            level: int,
            msg: str,
            method_name: str,
            exc_info: Union[None, bool, BaseException] = None,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one log record through the channel-style logger surface.

        Contract:
        - Preserves the existing `_is_channel`-driven behavior so channel-like
          test doubles continue to work even when they do not implement the
          full public `IChannelLogger` protocol.
        - Keeps `_manual_stack` and `_method_name` on the channel path only.
        - Uses the masking API when `mask=True`.
        """
        if mask:
            logger.mask_log(
                level,
                msg,
                owner=owner,
                owner_id=owner_id,
                owner_display=owner_display,
                groups=groups,
                system_groups=system_groups,
                properties=properties,
                exc_info=exc_info,
                _manual_stack=True,
                _method_name=method_name,
            )
            return

        if level == logging.DEBUG:
            logger.debug(msg, _manual_stack=True, _method_name=method_name)
            return
        if level == logging.INFO:
            logger.info(msg, _manual_stack=True, _method_name=method_name)
            return
        if level == logging.WARNING:
            logger.warning(msg, _manual_stack=True, _method_name=method_name)
            return
        if level == logging.ERROR:
            logger.error(
                msg,
                exc_info=exc_info if exc_info is not None else False,
                _manual_stack=True,
                _method_name=method_name,
            )
            return
        if level >= logging.CRITICAL:
            logger.critical(msg, _manual_stack=True, _method_name=method_name)
            return

        logger._log(level, msg, _manual_stack=True, _method_name=method_name)

    def _emit(
            self,
            level: int,
            msg: str,
            method_name: str,
            *,
            exc_info: Union[None, bool, BaseException] = None,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> None:
        """
        Internal unified emit path for both channel and stdlib loggers.

        Contract:
        - Returns immediately when no logger is configured or the message level
          is below the current threshold.
        - Preserves channel-specific metadata when using `IChannelLogger`.
        - Ignores masking on stdlib logger paths by design.
        - Forwards explicit exception objects on the stdlib error path;
          boolean `True` uses the active exception context.
        """
        logger = self._logger
        if logger is None:
            return
        if level < self._level:
            return

        if self._is_channel or isinstance(logger, IChannelLogger):
            self._emit_channel(
                logger,
                level=level,
                msg=msg,
                method_name=method_name,
                exc_info=exc_info,
                mask=mask,
                owner=owner,
                owner_id=owner_id,
                owner_display=owner_display,
                groups=groups,
                system_groups=system_groups,
                properties=properties,
            )
            return

        # Std logger path (masking is intentionally ignored)
        if not isinstance(logger, logging.Logger):
            raise TypeError("SafeLogger requires a stdlib logger in the non-channel branch.")
        if level == logging.DEBUG:
            logger.debug(msg)
            return
        if level == logging.INFO:
            logger.info(msg)
            return
        if level == logging.WARNING:
            logger.warning(msg)
            return
        if level == logging.ERROR:
            if isinstance(exc_info, BaseException):
                # BUG-148 (2026-07-17 audit): forward the explicit exception
                # object so the record carries the caller-supplied type,
                # value, and traceback even outside an active handler.
                logger.error(msg, exc_info=exc_info)
            elif exc_info:
                # Boolean True: use the active exception context.
                logger.exception(msg)
            else:
                logger.error(msg)
            return
        if level >= logging.CRITICAL:
            logger.critical(msg)
            return

        logger.log(level, msg)

    # ---- Public API (now with optional masking on every call) ---------------------

    def debug(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one debug-level log event.

        Contract:
        - Delegates to `_emit(...)` with `logging.DEBUG`.
        - Supports optional masking and channel metadata when the wrapped
          logger is a channel logger.
        """
        self._emit(
            logging.DEBUG, msg, method_name,
            mask=mask,
            owner=owner, owner_id=owner_id, owner_display=owner_display,
            groups=groups, system_groups=system_groups, properties=properties,
        )

    def info(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one info-level log event.

        Contract:
        - Delegates to `_emit(...)` with `logging.INFO`.
        - Supports optional masking and channel metadata when the wrapped
          logger is a channel logger.
        """
        self._emit(
            logging.INFO, msg, method_name,
            mask=mask,
            owner=owner, owner_id=owner_id, owner_display=owner_display,
            groups=groups, system_groups=system_groups, properties=properties,
        )

    def warning(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one warning-level log event.

        Contract:
        - Delegates to `_emit(...)` with `logging.WARNING`.
        - Supports optional masking and channel metadata when the wrapped
          logger is a channel logger.
        """
        self._emit(
            logging.WARNING, msg, method_name,
            mask=mask,
            owner=owner, owner_id=owner_id, owner_display=owner_display,
            groups=groups, system_groups=system_groups, properties=properties,
        )

    def warn(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object | None = None,
            owner_id: str | None = None,
            owner_display: str | None = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Compatibility alias for `warning()`.

        Contract:
            - Preserves the historical `warn` surface without relying on a
              class-body alias assignment.
            - Delegates all behavior and metadata handling to `warning()`.
        """
        self.warning(
            msg,
            method_name,
            mask=mask,
            owner=owner,
            owner_id=owner_id,
            owner_display=owner_display,
            groups=groups,
            system_groups=system_groups,
            properties=properties,
        )

    def error(
            self,
            msg: str,
            method_name: str,
            *,
            exc_info: Union[None, bool, BaseException] = True,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one error-level log event.

        Contract:
        - Delegates to `_emit(...)` with `logging.ERROR`.
        - Passes through `exc_info` so channel and stdlib paths can preserve
          error context.
        """
        self._emit(
            logging.ERROR, msg, method_name,
            exc_info=exc_info,
            mask=mask,
            owner=owner, owner_id=owner_id, owner_display=owner_display,
            groups=groups, system_groups=system_groups, properties=properties,
        )

    def exception(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Convenience wrapper for emitting an error with exception context.

        Contract:
        - Delegates to `_emit(...)` with `logging.ERROR` and `exc_info=True`.
        """
        self._emit(
            logging.ERROR, msg, method_name,
            exc_info=True,
            mask=mask,
            owner=owner, owner_id=owner_id, owner_display=owner_display,
            groups=groups, system_groups=system_groups, properties=properties,
        )

    def critical(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object = None,
            owner_id: Optional[str] = None,
            owner_display: Optional[str] = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit one critical-level log event.

        Contract:
        - Delegates to `_emit(...)` with `logging.CRITICAL`.
        - Supports optional masking and channel metadata when the wrapped
          logger is a channel logger.
        """
        self._emit(
            logging.CRITICAL, msg, method_name,
            mask=mask,
            owner=owner, owner_id=owner_id, owner_display=owner_display,
            groups=groups, system_groups=system_groups, properties=properties,
        )

    def fatal(
            self,
            msg: str,
            method_name: str,
            *,
            mask: bool = False,
            owner: object | None = None,
            owner_id: str | None = None,
            owner_display: str | None = None,
            groups: Optional[Iterable[str]] = None,
            system_groups: Optional[Iterable[str]] = None,
            properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Compatibility alias for `critical()`.

        Contract:
            - Preserves the historical `fatal` surface without relying on a
              class-body alias assignment.
            - Delegates all behavior and metadata handling to `critical()`.
        """
        self.critical(
            msg,
            method_name,
            mask=mask,
            owner=owner,
            owner_id=owner_id,
            owner_display=owner_display,
            groups=groups,
            system_groups=system_groups,
            properties=properties,
        )
