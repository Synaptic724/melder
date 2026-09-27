"""Investigation-only regressions for inherited cleanup; production source stays unchanged."""

from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.spellbook.test_ordered_disposal_binding import configured_book


class CleanupOwner:
    """Own a simple call log so real teardown has an observable, deterministic result."""

    def __init__(self) -> None:
        """Create the per-instance log without external resources or shared mutable state."""
        self.calls: list[str] = []

    def cleanup(self) -> None:
        """Record one cleanup invocation; no resource release or concurrency is involved."""
        self.calls.append("cleanup")


class InheritedCleanup(CleanupOwner):
    """Use the base cleanup unchanged, with no subclass-local method implementation."""


class UnrelatedMixin:
    """Supply a second base without defining or shadowing the cleanup method."""


class MixinCleanup(UnrelatedMixin, CleanupOwner):
    """Inherit cleanup through the second branch of the normal method resolution order."""


class ShadowedCleanup(CleanupOwner):
    """Disable the base callable with a subclass-local non-callable shadow."""

    cleanup = None


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Reset the real runtime around each case using the existing suite's ownership pattern."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Spellbook._aether
    try:
        yield
    finally:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        Spellbook._aether = Aether()
        Conduit._aether = Spellbook._aether


@pytest.mark.parametrize("target", [CleanupOwner, InheritedCleanup])
@pytest.mark.parametrize("source", ["explicit", "configured"])
def test_binding_retains_available_cleanup(target: type[CleanupOwner], source: str) -> None:
    """Both candidate sources must retain the callable available on the registered class."""
    book_names = ["cleanup"] if source == "configured" else []
    spell_names = ["cleanup"] if source == "explicit" else []
    with configured_book(book_names) as book:
        spell_id = book.bind(spell=target, existence="many", disposal_method_names=spell_names)
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == ["cleanup"]
        assert spell.has_disposal_methods is True


@pytest.mark.parametrize("target", [CleanupOwner, InheritedCleanup])
@pytest.mark.parametrize("existence", ["many", "unique"])
def test_runtime_calls_available_cleanup(target: type[CleanupOwner], existence: str) -> None:
    """Real bind/conjure/meld/cleanup must invoke the declared inherited or direct cleanup."""
    with configured_book([]) as book:
        spell_id = book.bind(spell=target, existence=existence, disposal_method_names=["cleanup"])
        conduit = book.conjure()
        instance = conduit.meld(spell_id=spell_id)
        conduit.permanent_cleanup()
        assert instance.calls == ["cleanup"]


def test_multiple_inheritance_retains_available_cleanup() -> None:
    """Cleanup supplied by a second base must be eligible without a duplicate implementation."""
    with configured_book([]) as book:
        spell_id = book.bind(spell=MixinCleanup, existence="many", disposal_method_names=["cleanup"])
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == ["cleanup"]


def test_non_callable_shadow_stays_excluded() -> None:
    """A future MRO-aware fix must stop at a non-callable shadow instead of reviving a base method."""
    with configured_book([]) as book:
        spell_id = book.bind(spell=ShadowedCleanup, existence="many", disposal_method_names=["cleanup"])
        spell = book.find_spell_by_id(spell_id)
        assert spell is not None
        assert spell.disposal_method_names == []
        assert spell.has_disposal_methods is False
