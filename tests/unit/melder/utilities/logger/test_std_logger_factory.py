import logging
from unittest import mock

import pytest

from melder.utilities.logger.std_logger_factory import StdLoggerFactory
from melder.utilities.logger.safe_logger import SafeLogger


def test_std_logger_factory_returns_safe_logger_and_sets_name():
    obj = type("Obj", (), {"_id": "123"})()
    factory = StdLoggerFactory()
    logger = factory(obj)
    assert isinstance(logger, SafeLogger)
    assert any("Obj[123]" in name for name in factory.all_logger_names())
    # __call__ should return same logger if called again
    logger_again = factory(obj)
    assert logger_again is logger


def test_std_logger_factory_call_requires_id():
    factory = StdLoggerFactory()
    class NoId:
        pass
    with pytest.raises(AttributeError):
        factory(NoId())


def test_std_logger_factory_rejects_invalid_level():
    factory = StdLoggerFactory()
    with pytest.raises(ValueError):
        factory.set_global_level_by_name("nope")


def test_std_logger_factory_global_level_propagation_and_handlers():
    handler = logging.NullHandler()
    factory = StdLoggerFactory(propagate=False, handlers=[handler])
    obj = type("Obj", (), {"_id": "id1"})()
    logger = factory(obj)
    raw_logger = logger._logger
    assert handler in raw_logger.handlers
    assert raw_logger.propagate is False

    factory.set_global_level_by_name("error")
    assert factory.get_global_level_name() == "error"
    factory.set_global_level(logging.INFO)
    assert factory.get_global_level() == logging.INFO

    # new logger should pick up updated settings
    obj2 = type("Obj2", (), {"_id": "id2"})()
    logger2 = factory(obj2)
    assert logger2._logger.level == logging.INFO
    # sync root path
    factory_sync = StdLoggerFactory(sync_root_with_global_level=True)
    factory_sync.set_global_level(logging.ERROR)
    assert logging.getLogger().level == logging.ERROR


def test_std_logger_factory_remove_handler_and_set_formatter():
    factory = StdLoggerFactory()
    obj = type("Obj", (), {"_id": "id"})()
    logger = factory(obj)
    handler = logging.NullHandler()
    factory.add_handler(handler)
    assert handler in logger._logger.handlers
    factory.remove_handler(handler)
    assert handler not in logger._logger.handlers
    # add/remove None are no-ops
    factory.add_handler(None)
    factory.remove_handler(None)

    formatter = logging.Formatter("%(message)s")
    factory.set_formatter(formatter)
    for h in logger._logger.handlers:
        assert h.formatter == formatter
    # set_formatter should be no-op on None
    factory.set_formatter(None)


def test_std_logger_factory_clear_registry_and_cleanup():
    factory = StdLoggerFactory()
    obj = type("Obj", (), {"_id": "id"})()
    logger = factory(obj)
    name = list(factory.all_logger_names())[0]
    assert factory.get_logger_by_name(name) is logger
    factory.clear_registry()
    assert factory.get_logger_by_name(name) is None
    factory.cleanup()
    with pytest.raises(RuntimeError):
        factory(obj)
    with pytest.raises(RuntimeError):
        factory.get_logger_by_name(name)
    # cleanup is idempotent
    factory.cleanup()


def test_std_logger_factory_make_with_id_and_missing_handler_removal():
    factory = StdLoggerFactory()
    logger = factory.make_with_id("Cls", "ident")
    assert isinstance(logger, SafeLogger)
    # Removing a handler not present is a no-op
    factory.remove_handler(logging.NullHandler())


def test_std_logger_factory_getters_and_missing_logger():
    factory = StdLoggerFactory(default_level=logging.WARNING, propagate=False)
    assert factory.get_global_level() == logging.WARNING
    assert factory.get_global_level_name() == "warning"
    # missing logger returns None
    assert factory.get_logger_by_name("missing") is None
    assert factory.all_logger_names() == []


def test_std_logger_factory_set_propagate_applies_to_existing():
    factory = StdLoggerFactory(propagate=True)
    obj = type("Obj", (), {"_id": "id"})()
    logger = factory(obj)
    raw = logger._logger
    assert raw.propagate is True
    factory.set_propagate(False)
    assert raw.propagate is False


def test_std_logger_factory_set_formatter_applies_to_new_loggers():
    fmt = logging.Formatter("%(message)s")
    factory = StdLoggerFactory()
    obj1 = type("Obj", (), {"_id": "id1"})()
    logger1 = factory(obj1)
    factory.set_formatter(fmt)
    for h in logger1._logger.handlers:
        assert h.formatter == fmt
    obj2 = type("Obj", (), {"_id": "id2"})()
    logger2 = factory(obj2)
    for h in logger2._logger.handlers:
        assert h.formatter == fmt
    # None formatter is no-op
    factory.set_formatter(None)


def test_std_logger_factory_make_with_id_returns_existing():
    factory = StdLoggerFactory()
    first = factory.make_with_id("Cls", "ident")
    second = factory.make_with_id("Cls", "ident")
    assert first is second


def test_std_logger_factory_set_global_level_by_name_invalid_and_sync_root():
    factory = StdLoggerFactory(sync_root_with_global_level=True)
    with pytest.raises(ValueError):
        factory.set_global_level_by_name("invalid")
    factory.set_global_level_by_name("debug")
    assert factory.get_global_level_name() == "debug"
    assert logging.getLogger().level == logging.DEBUG


def test_std_logger_factory_get_logger_by_name_after_clear_and_recreate():
    factory = StdLoggerFactory()
    obj = type("Obj", (), {"_id": "idx"})()
    logger = factory(obj)
    name = factory.all_logger_names()[0]
    factory.clear_registry()
    assert factory.get_logger_by_name(name) is None
    # recreating should register again
    logger2 = factory(obj)
    assert logger2 is not None
    assert name in factory.all_logger_names()
