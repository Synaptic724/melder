import logging
from typing import Optional, Iterable, Dict, Any, Union
# Melder imports
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IChannelLogger
from melder.utilities.helpers.id_builder import IDBuilder


class SafeLogger(Cleanable):
    """
    A unified, low-overhead logger adapter that transparently handles both
    IChannelLogger-compatible objects and standard Python loggers.

    - Detects channel loggers by isinstance(logger, IChannelLogger).
    - Passes through `_manual_stack` and `_method_name` for ChannelLoggers.
    - Standard loggers drop channel-only kwargs and ignore masking.
    - No getattr on our own classes.
    """
    __slots__ = Cleanable.__slots__ + ["_logger", "_is_channel", "_id", "_level", "_level_name"]
    _LEVELS: Dict[str, int] = {
        "notset": logging.NOTSET,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    def __init__(self, logger: logging.Logger | IChannelLogger | None, level_name: str = "INFO"):
        super().__init__()
        self._id = IDBuilder.create_id()
        from melder.utilities.interfaces.interfaces import IChannelLogger as _IChannelLogger
        if logger is not None and not isinstance(logger, (logging.Logger, _IChannelLogger)):
            raise TypeError(
                f"SafeLogger expects a logging.Logger or IChannelLogger instance or None, "
                f"got {type(logger).__name__} instead."
            )
        self._logger = logger
        self._is_channel = isinstance(logger, _IChannelLogger)
        normalized = level_name.lower()
        if normalized not in self._LEVELS:
            raise ValueError(f"Invalid log level name '{level_name}'. Expected one of: {list(self._LEVELS)}")
        self._level_name = normalized
        self._level = self._LEVELS[normalized]
        if logger is not None:
            logger.setLevel(self._level)

    def cleanup(self):
        # Allow external polymorphic cleanup; std loggers won't have it.
        if self._logger is not None and hasattr(self._logger, "cleanup"):
            try:
                self._logger.cleanup()
            except Exception:
                pass
        self._logger = None

    def set_level_by_name(self, level_name: str):
        """
        Set the log level by symbolic name (debug, info, warning, error, critical).
        """
        normalized = level_name.lower()
        if normalized not in self._LEVELS:
            raise ValueError(f"Invalid log level name '{level_name}'. Expected one of: {list(self._LEVELS)}")
        self._level_name = normalized
        self._level = self._LEVELS[normalized]
        if self._logger is not None:
            self._logger.setLevel(self._level)

    def set_level(self, level: int):
        """
        Direct numeric setter (kept for parity).
        """
        if level not in self._LEVELS.values():
            raise ValueError(f"Invalid numeric log level: {level}")
        self._level = level
        if self._logger is not None:
            self._logger.setLevel(level)

    # ---- Internal unified emitter -------------------------------------------------

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
        Internal: route to ChannelLogger with or without masking, or to std logger.
        - Std logger path ignores masking entirely (as requested).
        """
        if self._logger is None:
            return
        if level < self._level:
            return

        if self._is_channel:
            # Channel path
            if mask:
                # Use the real masking API; enforce your manual stack metadata.
                self._logger.mask_log(
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

            # Non-masked channel path mirrors your existing behavior.
            if level == logging.DEBUG:
                self._logger.debug(msg, _manual_stack=True, _method_name=method_name)
                return
            if level == logging.INFO:
                self._logger.info(msg, _manual_stack=True, _method_name=method_name)
                return
            if level == logging.WARNING:
                self._logger.warning(msg, _manual_stack=True, _method_name=method_name)
                return
            if level == logging.ERROR:
                self._logger.error(
                    msg,
                    exc_info=exc_info if exc_info is not None else False,
                    _manual_stack=True,
                    _method_name=method_name,
                )
                return
            if level >= logging.CRITICAL:
                self._logger.critical(msg, _manual_stack=True, _method_name=method_name)
                return

            # Fallback for uncommon numeric levels
            self._logger._log(level, msg, _manual_stack=True, _method_name=method_name)  # type: ignore[attr-defined]
            return

        # Std logger path (masking is intentionally ignored)
        if level == logging.DEBUG:
            self._logger.debug(msg)
            return
        if level == logging.INFO:
            self._logger.info(msg)
            return
        if level == logging.WARNING:
            self._logger.warning(msg)
            return
        if level == logging.ERROR:
            if exc_info:
                # Match your current semantics: exception() when exc_info truthy.
                self._logger.exception(msg)
            else:
                self._logger.error(msg)
            return
        if level >= logging.CRITICAL:
            self._logger.critical(msg)
            return

        self._logger.log(level, msg)

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
        self._emit(
            logging.WARNING, msg, method_name,
            mask=mask,
            owner=owner, owner_id=owner_id, owner_display=owner_display,
            groups=groups, system_groups=system_groups, properties=properties,
        )

    warn = warning  # alias

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
    ):
        """Convenience alias for .error(..., exc_info=True)."""
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
        self._emit(
            logging.CRITICAL, msg, method_name,
            mask=mask,
            owner=owner, owner_id=owner_id, owner_display=owner_display,
            groups=groups, system_groups=system_groups, properties=properties,
        )

    fatal = critical
