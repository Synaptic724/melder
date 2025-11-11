import logging
from melder.utilities.general_base.cleanable import Cleanable

class SafeLogger(Cleanable):
    """
    A unified, low-overhead logger adapter that transparently handles both
    IChannelLogger-compatible objects and standard Python loggers.

    - Detects channel loggers by isinstance(logger, IChannelLogger).
    - Passes through `_manual_stack` and `_method_name` for ChannelLoggers.
    - Standard loggers drop those extra kwargs.
    - No getattr, no reflection, zero overhead when logger is None.
    """
    __slots__ = Cleanable.__slots__ + ["_logger", "_is_channel"]

    def __init__(self, logger: 'logging.Logger | IChannelLogger | None'):
        super().__init__()
        from melder.utilities.interfaces.interfaces import IChannelLogger
        if logger is not None and not isinstance(logger, (logging.Logger, IChannelLogger)):
            raise TypeError(
                f"SafeLogger expects a logging.Logger or IChannelLogger instance or None, "
                f"got {type(logger).__name__} instead."
            )
        self._logger = logger
        self._is_channel = isinstance(logger, IChannelLogger)

    def cleanup(self):
        if hasattr(self._logger, "cleanup"):
            self._logger.cleanup()
        self._logger = None

    def debug(self, msg: str, method_name: str):
        if self._logger is None:
            return
        if self._is_channel:
            self._logger.debug(msg, _manual_stack=True, _method_name=method_name)
        else:
            self._logger.debug(msg)

    def info(self, msg: str, method_name: str):
        if self._logger is None:
            return
        if self._is_channel:
            self._logger.info(msg, _manual_stack=True, _method_name=method_name)
        else:
            self._logger.info(msg)

    def warning(self, msg: str, method_name: str):
        if self._logger is None:
            return
        if self._is_channel:
            self._logger.warning(msg, _manual_stack=True, _method_name=method_name)
        else:
            self._logger.warning(msg)

    def error(self, msg: str, method_name: str, *, exc_info: bool = True):
        if self._logger is None:
            return
        if self._is_channel:
            self._logger.error(msg, exc_info=exc_info, _manual_stack=True, _method_name=method_name)
        else:
            if exc_info:
                self._logger.exception(msg)
            else:
                self._logger.error(msg)

    def exception(self, msg: str, method_name: str):
        """Convenience alias for .error(msg, method_name, exc_info=True)."""
        self.error(msg, method_name, exc_info=True)
