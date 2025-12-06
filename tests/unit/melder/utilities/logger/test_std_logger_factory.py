import logging
import pytest

from melder.utilities.logger.std_logger_factory import StdLoggerFactory
from melder.utilities.logger.safe_logger import SafeLogger


def test_std_logger_factory_returns_safe_logger():
    logger = StdLoggerFactory.get_logger("test_std_logger_factory")
    assert isinstance(logger, SafeLogger)


def test_std_logger_factory_rejects_invalid_level():
    with pytest.raises(ValueError):
        StdLoggerFactory.get_logger("bad_level", level_name="nope")

    # Valid level_name should set the underlying level
    raw = logging.getLogger("std_factory_level")
    logger = StdLoggerFactory.get_logger("std_factory_level", level_name="DEBUG", logger=raw)
    assert raw.level == logging.DEBUG


def test_std_logger_factory_global_level_and_handlers():
    factory = StdLoggerFactory()
    handler = logging.NullHandler()
    factory.add_handler(handler)
    logger = factory("obj_with_id")
    # change global level by name and numeric
    factory.set_global_level_by_name("error")
    assert factory.get_global_level_name() == "error"
    factory.set_global_level(logging.INFO)
    assert factory.get_global_level() == logging.INFO
    # propagate flag
    factory.set_propagate(False)
    raw_logger = logger._logger
    assert raw_logger.propagate is False
    # handler was attached
    assert handler in raw_logger.handlers


def test_std_logger_factory_clear_registry_and_cleanup():
    factory = StdLoggerFactory()
    logger = factory("obj_with_id")
    name = list(factory.all_logger_names())[0]
    assert factory.get_logger_by_name(name) is logger
    factory.clear_registry()
    assert factory.get_logger_by_name(name) is None
    factory.cleanup()
    with pytest.raises(RuntimeError):
        factory("another")
