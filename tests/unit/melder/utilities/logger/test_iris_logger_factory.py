import logging
import pytest

from melder.utilities.logger.iris_logger_factory import IrisLoggerFactory
from melder.utilities.logger.safe_logger import SafeLogger


def test_iris_logger_factory_returns_safe_logger_when_available(monkeypatch):
    raw = logging.getLogger("iris_test")

    def _resolver(registrant, groups=None, system_groups=None, props=None, channels=None):
        return raw

    factory = IrisLoggerFactory(_resolver, default_level_name="debug")
    logger = factory("registrant", groups=["g"])
    assert isinstance(logger, SafeLogger)


def test_iris_logger_factory_handles_missing_dependency(monkeypatch):
    def _resolver(*args, **kwargs):
        raise ImportError("missing iris deps")

    factory = IrisLoggerFactory(_resolver)
    logger = factory("registrant")
    assert isinstance(logger, SafeLogger)


def test_iris_logger_factory_default_levels_and_overrides():
    raw = logging.getLogger("iris_levels")

    def _resolver(**kwargs):
        return raw

    factory = IrisLoggerFactory(_resolver, default_level=logging.WARNING)
    logger = factory("registrant")
    assert raw.level == logging.WARNING

    logger = factory("registrant", level_name="error")
    assert raw.level == logging.ERROR

    factory.set_default_level_by_name("info")
    logger = factory("registrant")
    assert raw.level == logging.INFO

    with pytest.raises(ValueError):
        factory.set_default_level_by_name("invalid")
