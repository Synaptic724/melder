"""User module for the spell-id stability probe: one object per candidate shape."""
import functools
from dataclasses import dataclass

from melder.aether.conduit.meld.contracts.spell_contract import SpellContract


class Engine:
    """Plain provider class."""


def make_engine(size: int = 3) -> Engine:
    """Plain factory function."""
    return Engine()


def make_with_object_default(marker: object = object()) -> Engine:
    """Factory whose default is an object without a custom repr."""
    return Engine()


def make_with_contract_default(dep: Engine = SpellContract(spellframe="EngineFrame", binding_name="main")) -> Engine:
    """Factory whose default is a SpellContract."""
    return Engine()


def _decorate(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


@_decorate
def decorated_factory(size: int = 1) -> Engine:
    """Factory wrapped with functools.wraps."""
    return Engine()


make_lambda = lambda: Engine()


class Workshop:
    """Owner of method-shaped factories."""

    def build(self) -> Engine:
        """Bound-method factory."""
        return Engine()

    @staticmethod
    def build_static() -> Engine:
        """Static-method factory."""
        return Engine()

    @classmethod
    def build_class(cls) -> Engine:
        """Class-method factory."""
        return Engine()


class EngineWithMarker:
    """Class whose constructor default is an object without a custom repr."""

    def __init__(self, marker: object = object()) -> None:
        self.marker = marker


class CallableFactory:
    """Instance with __call__ (routed to the callable profile)."""

    def __call__(self) -> Engine:
        return Engine()


class Settings:
    """Existing object with the default repr."""


class NamedSettings:
    """Existing object with a custom repr."""

    def __repr__(self) -> str:
        return "NamedSettings(prod)"


@dataclass
class ValueSettings:
    """Existing dataclass object (field-based repr)."""
    level: int = 2


WORKSHOP = Workshop()
CANDIDATES = {
    "function": make_engine,
    "function_object_default": make_with_object_default,
    "function_contract_default": make_with_contract_default,
    "decorated_function": decorated_factory,
    "lambda": make_lambda,
    "bound_method": WORKSHOP.build,
    "static_method": Workshop.build_static,
    "class_method": Workshop.build_class,
    "partial": functools.partial(make_engine, size=4),
    "callable_instance": CallableFactory(),
    "instance_default_repr": Settings(),
    "instance_custom_repr": NamedSettings(),
    "instance_dataclass": ValueSettings(),
    "class": Engine,
    "class_object_default": EngineWithMarker,
}
