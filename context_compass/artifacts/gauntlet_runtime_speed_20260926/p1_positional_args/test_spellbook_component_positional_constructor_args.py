"""
Component tests for positional constructor arguments in generalized no-overrides plans.

Purpose:
    The phase-11 generalized emitter passes a step's leading dependency values positionally when
    the target is plainly constructed (metaclass keeps `type.__call__`, `__new__` is
    `object.__new__`, `__init__` is a Python function), because on CPython 3.14 a positional class
    call takes the interpreter's specialized allocate-and-init path. These tests drive real
    bind -> conjure -> meld flows and pin what must not change: every dependency lands on the
    parameter it was resolved for, defaults and keyword-only parameters keep their meaning, and a
    class with a custom `__new__` still melds correctly. They also pin the one intended behavior change:
    positional-only dependency parameters now meld instead of raising.
"""

from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus


def _reset_runtime() -> None:
    """Reset the Nexus and Aether singletons and rebind the class-level Aether references."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def reset_runtime_for_positional_constructor_args() -> Iterator[None]:
    """
    Reset singleton runtime state around every test.

    Yields:
        None.
    """
    _reset_runtime()
    yield
    _reset_runtime()


class Alpha:
    """Singleton dependency."""


class Beta:
    """Second singleton dependency."""


class Pair:
    """Two dependencies in declaration order."""

    def __init__(self, alpha: Alpha, beta: Beta) -> None:
        """Store both dependencies."""
        self.alpha = alpha
        self.beta = beta


class Reversed:
    """Two dependencies declared in the opposite order."""

    def __init__(self, beta: Beta, alpha: Alpha) -> None:
        """Store both dependencies."""
        self.beta = beta
        self.alpha = alpha


class DefaultThenKeywordOnly:
    """A dependency, a plain defaulted value, then a keyword-only dependency."""

    def __init__(self, alpha: Alpha, count: int = 7, *, beta: Beta) -> None:
        """Store the arguments."""
        self.alpha = alpha
        self.count = count
        self.beta = beta


class PositionalOnly:
    """A positional-only dependency followed by a regular one."""

    def __init__(self, alpha: Alpha, /, beta: Beta) -> None:
        """Store both dependencies."""
        self.alpha = alpha
        self.beta = beta


class CustomNew:
    """Class with its own `__new__`; the emitter keeps its keyword call."""

    def __new__(cls, alpha: Alpha, beta: Beta) -> "CustomNew":
        """Allocate; `__new__` receives the same arguments as `__init__`."""
        instance = super().__new__(cls)
        instance.allocated_with = (alpha, beta)
        return instance

    def __init__(self, alpha: Alpha, beta: Beta) -> None:
        """Store both dependencies."""
        self.alpha = alpha
        self.beta = beta


class Outer:
    """Consumer whose first dependency is itself built positionally."""

    def __init__(self, pair: Pair, alpha: Alpha) -> None:
        """Store both dependencies."""
        self.pair = pair
        self.alpha = alpha


def _conjure() -> Conduit:
    """Bind every test class (singletons unique, consumers many) and conjure a root conduit."""
    spellbook = Spellbook(aetheric_frame="positional-constructor-args")
    spellbook.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    for singleton in (Alpha, Beta):
        spellbook.bind(spell=singleton, existence=Existence.unique)
    for consumer in (Pair, Reversed, DefaultThenKeywordOnly, PositionalOnly, CustomNew, Outer):
        spellbook.bind(spell=consumer, existence=Existence.many)
    return spellbook.conjure(name="positional-root", dynamic=False)


def test_positional_prefix_binds_each_dependency_to_its_parameter() -> None:
    """Both dependencies land on the parameter they were resolved for."""
    conduit = _conjure()
    pair = conduit.meld(Pair)
    assert pair.alpha is conduit.meld(Alpha)
    assert pair.beta is conduit.meld(Beta)


def test_reversed_declaration_order_binds_correctly() -> None:
    """Positional order follows the target's signature, not the dependency list."""
    conduit = _conjure()
    reversed_pair = conduit.meld(Reversed)
    assert reversed_pair.beta is conduit.meld(Beta)
    assert reversed_pair.alpha is conduit.meld(Alpha)


def test_default_and_keyword_only_parameters_keep_their_values() -> None:
    """The prefix stops at the defaulted value; the keyword-only dependency stays a keyword."""
    conduit = _conjure()
    consumer = conduit.meld(DefaultThenKeywordOnly)
    assert consumer.alpha is conduit.meld(Alpha)
    assert consumer.count == 7
    assert consumer.beta is conduit.meld(Beta)


def test_positional_only_dependencies_meld() -> None:
    """Positional-only dependency parameters meld (they raised TypeError under keyword calls)."""
    conduit = _conjure()
    consumer = conduit.meld(PositionalOnly)
    assert consumer.alpha is conduit.meld(Alpha)
    assert consumer.beta is conduit.meld(Beta)


def test_custom_new_class_still_melds_with_correct_bindings() -> None:
    """A custom `__new__` keeps the keyword call; both `__new__` and `__init__` get the right values."""
    conduit = _conjure()
    consumer = conduit.meld(CustomNew)
    alpha, beta = conduit.meld(Alpha), conduit.meld(Beta)
    assert consumer.allocated_with == (alpha, beta)
    assert consumer.alpha is alpha
    assert consumer.beta is beta


def test_nested_consumer_receives_positionally_built_dependency() -> None:
    """A dependency built by a positional call is itself passed on correctly."""
    conduit = _conjure()
    outer = conduit.meld(Outer)
    assert isinstance(outer.pair, Pair)
    assert outer.pair.alpha is conduit.meld(Alpha)
    assert outer.pair.beta is conduit.meld(Beta)
    assert outer.alpha is conduit.meld(Alpha)


def test_warm_melds_rebuild_many_with_the_same_bindings() -> None:
    """Cold and hot doors emit the same call: repeated melds build new, correctly bound objects."""
    conduit = _conjure()
    first = conduit.meld(Pair)
    second = conduit.meld(Pair)
    third = conduit.meld(Pair)
    assert first is not second and second is not third
    for pair in (first, second, third):
        assert pair.alpha is conduit.meld(Alpha)
        assert pair.beta is conduit.meld(Beta)
