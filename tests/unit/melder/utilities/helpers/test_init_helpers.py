import logging
import pytest

from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.interfaces import IChannelLogger


def test_resolve_safe_logger_accepts_none():
    logger = InitHelpers.resolve_safe_logger(None)
    assert isinstance(logger, SafeLogger)


def test_resolve_safe_logger_wraps_std_logger():
    raw = logging.getLogger("test_init_helpers")
    logger = InitHelpers.resolve_safe_logger(raw)
    assert isinstance(logger, SafeLogger)


def test_resolve_safe_logger_rejects_invalid_type():
    with pytest.raises(TypeError):
        InitHelpers.resolve_safe_logger(object())  # type: ignore[arg-type]


class _ChannelLoggerStub(IChannelLogger):
    def cleanup(self):
        pass

    def debug(self, *args, **kwargs): ...
    def info(self, *args, **kwargs): ...
    def warn(self, *args, **kwargs): ...
    def warning(self, *args, **kwargs): ...
    def error(self, *args, **kwargs): ...
    def critical(self, *args, **kwargs): ...
    def setLevel(self, level): ...
    @property
    def level(self): return None


def test_resolve_safe_logger_wraps_channel_logger():
    channel = _ChannelLoggerStub()
    logger = InitHelpers.resolve_safe_logger(channel)
    assert isinstance(logger, SafeLogger)
