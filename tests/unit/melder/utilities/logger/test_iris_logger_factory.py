import logging
from unittest import mock

import pytest

from melder.utilities.logger.iris_logger_factory import IrisLoggerFactory
from melder.utilities.logger.safe_logger import SafeLogger


class DummyConduit:
    pass


class DummySpellbook:
    pass


class DummyAether:
    pass


def test_iris_logger_factory_defaults_by_type_and_cleanup():
    raw = logging.getLogger("iris_defaults")

    captured = {}

    def _resolver(registrant, **kwargs):
        captured[type(registrant).__name__] = kwargs
        return raw

    # Test default_level path (notset) and default_level_name path
    factory = IrisLoggerFactory(_resolver, default_level=SafeLogger._LEVELS["notset"])
    # conduit defaults
    logger = factory(DummyConduit())
    assert isinstance(logger, SafeLogger)
    assert raw.level == logging.INFO  # SafeLogger defaults to INFO when no factory override applied
    # spellbook defaults
    factory(DummySpellbook())
    # aether defaults
    factory(DummyAether())

    # defaults applied when call args are None (uses generic when type not Protocol)
    assert captured["DummyConduit"]["groups"] == ["general"]
    assert captured["DummySpellbook"]["system_groups"] == []
    assert captured["DummyAether"]["channels"] == "system"

    factory.cleanup()


def test_iris_logger_factory_handles_missing_dependency(monkeypatch):
    def _resolver(*args, **kwargs):
        raise ImportError("missing iris deps")

    factory = IrisLoggerFactory(_resolver)
    # Factory doesn't catch; we expect ImportError to propagate
    with pytest.raises(ImportError):
        factory("registrant")


def test_iris_logger_factory_cleanup_calls_resolver_cleanup():
    class ResolverWithCleanup:
        def __init__(self):
            self.cleaned = False
        def __call__(self, **kwargs):
            return logging.getLogger("resolver_cleanup")
        def cleanup(self):
            self.cleaned = True
    resolver = ResolverWithCleanup()
    factory = IrisLoggerFactory(resolver)
    factory("registrant")
    factory.cleanup()
    assert resolver.cleaned is True


def test_iris_logger_factory_level_overrides_and_errors():
    raw = logging.getLogger("iris_levels")

    def _resolver(**kwargs):
        return raw

    factory = IrisLoggerFactory(_resolver, default_level=logging.INFO)
    # call with level override
    logger = factory("registrant", level_name="error")
    assert raw.level == logging.ERROR

    factory.set_default_level(logging.DEBUG)
    logger = factory("registrant")
    assert raw.level == logging.DEBUG

    with pytest.raises(ValueError):
        factory.set_default_level_by_name("invalid")


def test_iris_logger_factory_defaults_filled_only_when_none():
    raw = logging.getLogger("iris_defaults_fill")
    captured_kwargs = {}

    def _resolver(**kwargs):
        captured_kwargs.update(kwargs)
        return raw

    factory = IrisLoggerFactory(_resolver)
    factory(
        DummyConduit(),
        groups=["custom"],
        system_groups=["sys"],
        props={"p": 1},
        channels="chan",
        level=logging.CRITICAL,
    )
    assert captured_kwargs["groups"] == ["custom"]
    assert captured_kwargs["system_groups"] == ["sys"]
    assert captured_kwargs["props"] == {"p": 1}
    assert captured_kwargs["channels"] == "chan"
    assert raw.level == logging.CRITICAL
