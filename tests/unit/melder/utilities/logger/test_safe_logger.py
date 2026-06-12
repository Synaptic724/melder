import logging
from unittest import mock

import pytest

from melder.utilities.logger.safe_logger import SafeLogger
from melder.utilities.interfaces.ichannellogger import IChannelLogger


class _ChannelMock:
    """
    Minimal duck-type for IChannelLogger to hit the channel path.
    """

    def __init__(self):
        self.calls = []

    def mask_log(self, level, msg, **kwargs):
        self.calls.append(("mask_log", level, msg, kwargs))

    def debug(self, msg, **kwargs):
        self.calls.append(("debug", msg, kwargs))

    def info(self, msg, **kwargs):
        self.calls.append(("info", msg, kwargs))

    def warning(self, msg, **kwargs):
        self.calls.append(("warning", msg, kwargs))

    def error(self, msg, exc_info=None, **kwargs):
        self.calls.append(("error", msg, exc_info, kwargs))

    def critical(self, msg, **kwargs):
        self.calls.append(("critical", msg, kwargs))

    def _log(self, level, msg, **kwargs):
        self.calls.append(("_log", level, msg, kwargs))


class _ChannelLoggerStub:
    """Implements the expected channel logger methods."""

    def __init__(self):
        self.calls = []
        self.level = logging.NOTSET

    def mask_log(self, level, msg, **kwargs):
        self.calls.append(("mask_log", level, msg, kwargs))

    def debug(self, msg, **kwargs):
        self.calls.append(("debug", msg, kwargs))

    def info(self, msg, **kwargs):
        self.calls.append(("info", msg, kwargs))

    def warning(self, msg, **kwargs):
        self.calls.append(("warning", msg, kwargs))

    def error(self, msg, exc_info=None, **kwargs):
        self.calls.append(("error", msg, exc_info, kwargs))

    def critical(self, msg, **kwargs):
        self.calls.append(("critical", msg, kwargs))

    def _log(self, level, msg, **kwargs):
        self.calls.append(("_log", level, msg, kwargs))

    def cleanup(self):
        self.calls.append(("cleanup",))


def test_safe_logger_init_validates_level_and_type():
    raw = logging.getLogger("safe_init")
    logger = SafeLogger(raw, level_name="INFO")
    assert logger is not None
    with pytest.raises(TypeError):
        SafeLogger(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        SafeLogger(raw, level_name="NOPE")


def test_safe_logger_null_logger_is_noop_and_cleanup():
    logger = SafeLogger(None)
    logger.debug("noop", method_name="test")
    logger.error("noop", method_name="test")
    logger.cleanup()
    assert logger._logger is None


def test_safe_logger_std_logger_paths_and_thresholds():
    raw = mock.create_autospec(logging.Logger, instance=True)
    raw.level = logging.INFO
    logger = SafeLogger(raw, level_name="WARNING")
    # Below threshold dropped
    logger.info("drop", method_name="test")
    raw.info.assert_not_called()
    # At/above thresholds emit
    logger.warning("warn", method_name="test")
    raw.warning.assert_called_once_with("warn")
    logger.error("err", method_name="test", exc_info=False)
    raw.error.assert_called_once_with("err")
    logger.critical("crit", method_name="test")
    raw.critical.assert_called_once_with("crit")
    # exception path when exc_info is True
    logger.error("err_exc", method_name="test", exc_info=True)
    raw.exception.assert_called_once_with("err_exc")

    # convenience exception() wrapper
    raw.reset_mock()
    logger.exception("via_exception", method_name="test")
    raw.exception.assert_called_once_with("via_exception")

    # warn/fatal aliases on std path
    logger.warn("warn_alias", method_name="test")
    raw.warning.assert_called_with("warn_alias")
    logger.fatal("fatal_alias", method_name="test")
    raw.critical.assert_called_with("fatal_alias")

def test_safe_logger_set_level_by_name_and_numeric():
    raw = logging.getLogger("safe_levels")
    logger = SafeLogger(raw, level_name="INFO")
    logger.set_level_by_name("debug")
    assert raw.level == logging.DEBUG
    with pytest.raises(ValueError):
        logger.set_level_by_name("notalevel")
    with pytest.raises(ValueError):
        logger.set_level(999)


def test_safe_logger_channel_path_with_mask():
    channel = _ChannelLoggerStub()
    channel_mock = mock.create_autospec(IChannelLogger, instance=True)
    channel_mock.setLevel = mock.Mock()
    logger = SafeLogger(channel_mock, level_name="debug")
    # swap underlying to our stub to inspect calls
    logger._logger = channel
    logger._is_channel = True
    assert logger._is_channel is True

    logger.debug("dmsg", method_name="m", mask=True)
    logger.info("imsg", method_name="m")
    logger.warning("wmsg", method_name="m")
    logger.error("emsg", method_name="m", exc_info=False)
    logger.critical("cmsg", method_name="m")
    logger.warn("alias_warn", method_name="m")
    logger.fatal("alias_fatal", method_name="m")

    kinds = [c[0] for c in channel.calls]
    assert "mask_log" in kinds  # debug with mask
    assert any(c[0] == "error" and c[1] == "emsg" and c[2] is False for c in channel.calls)


def test_safe_logger_channel_path_exc_info_and_fallback():
    channel = _ChannelLoggerStub()
    channel_mock = mock.create_autospec(IChannelLogger, instance=True)
    channel_mock.setLevel = mock.Mock()
    logger = SafeLogger(channel_mock, level_name="info")
    logger._logger = channel
    logger._is_channel = True
    logger.error("err", method_name="m", exc_info=True, mask=True)
    logger.error("err_obj", method_name="m", exc_info=ValueError("boom"))
    logger._level = 5  # uncommon numeric
    logger._emit(5, "low", "m")
    assert any(call[0] == "_log" for call in channel.calls)


def test_safe_logger_cleanup_calls_channel_cleanup():
    channel = _ChannelLoggerStub()
    channel_mock = mock.create_autospec(IChannelLogger, instance=True)
    channel_mock.setLevel = mock.Mock()
    logger = SafeLogger(channel_mock)
    logger._logger = channel
    logger._is_channel = True
    logger.cleanup()
    assert ("cleanup",) in channel.calls


def test_safe_logger_is_attached_reflects_wrapped_sink():
    """
    Purpose:
        Verify the hot-path attachment probe matches the wrapped sink state.
    Contract:
        - Null surface reports not attached.
        - Stdlib-backed and channel-backed surfaces report attached.
    """
    assert SafeLogger(None).is_attached is False

    std_logger = logging.getLogger("safe-logger-is-attached-std")
    assert SafeLogger(std_logger).is_attached is True

    channel_mock = mock.create_autospec(IChannelLogger, instance=True)
    channel_mock.setLevel = mock.Mock()
    assert SafeLogger(channel_mock).is_attached is True


def test_safe_logger_is_attached_false_after_cleanup():
    """
    Purpose:
        Verify cleanup downgrades the attachment probe to False.
    Contract:
        - After ``cleanup()`` releases the wrapped reference, callers gating
          on ``is_attached`` skip message construction entirely.
    """
    std_logger = logging.getLogger("safe-logger-is-attached-cleanup")
    safe_logger = SafeLogger(std_logger)
    assert safe_logger.is_attached is True
    safe_logger.cleanup()
    assert safe_logger.is_attached is False
