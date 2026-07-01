"""
Integration tests -- invalidation / dependent rechecking (area B).

Formalizes the proven experiment `test_cleanup_dependency_breaks_dependents_experiment`:
cleaning up a shared dependency must BREAK its dependents. A spell that other spells
depend on is disposed; the dependents must go gated on the SpellSystemStates plane and
FAIL to resolve -- a dependent that still melds after its dependency was disposed is a
correctness violation.

Dependencies are expressed via constructor type-hints (the repo's DI convention).
Transactions are OUT OF SCOPE. Runtime: Python 3.14t; the 3.10 sandbox cannot run
these -> user runs on 3.14t.
"""

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class _Dep1:
    def __init__(self) -> None:
        pass


class _Dep2:
    def __init__(self) -> None:
        pass


class _Root:
    def __init__(self, dep1: _Dep1, dep2: _Dep2) -> None:
        self.dep1 = dep1
        self.dep2 = dep2


class _OtherRoot:
    def __init__(self, dep1: _Dep1) -> None:
        self.dep1 = dep1


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_invalidation() -> None:
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    config = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=config)


def _spell(book: Spellbook, spell_id: str) -> Any:
    """Live spell object for a current spell id (from the id pool)."""
    return book._spell_id_pool.get(spell_id)


def _validity(book: Spellbook, spell_id: str) -> str:
    state = _spell(book, spell_id).system_state
    return str(state.validity) if state is not None else ""


def _resolves(conduit: Conduit, spell_id: str) -> bool:
    """True iff meld returns a non-None instance without raising."""
    try:
        return conduit.meld(spell=spell_id) is not None
    except Exception:
        return False


def _bound_graph(book: Spellbook) -> tuple:
    """Bind two deps + two roots sharing dep1; return (dep1, dep2, root, other)."""
    with book.transaction("bind"):
        dep1 = book.bind(spell=_Dep1, existence=Existence.unique, permissions="create")
        dep2 = book.bind(spell=_Dep2, existence=Existence.unique, permissions="create")
        root = book.bind(spell=_Root, existence=Existence.unique, permissions="create")
        other = book.bind(spell=_OtherRoot, existence=Existence.unique, permissions="create")
    return dep1, dep2, root, other


def test_dependents_meld_before_cleanup():
    book = _make_spellbook()
    conduit = book.conjure(dynamic=True, name="root")
    try:
        dep1, dep2, root, other = _bound_graph(book)
        assert _resolves(conduit, root) is True
        assert _resolves(conduit, other) is True
    finally:
        conduit.cleanup()


def test_cleanup_dependency_gates_both_dependents():
    book = _make_spellbook()
    conduit = book.conjure(dynamic=True, name="root")
    try:
        dep1, dep2, root, other = _bound_graph(book)
        _resolves(conduit, root)
        _resolves(conduit, other)
        conduit.cleanup_spell(spell=_spell(book, dep1))
        assert "gated" in _validity(book, root).lower()
        assert "gated" in _validity(book, other).lower()
    finally:
        conduit.cleanup()


def test_cleanup_dependency_breaks_dependent_meld():
    book = _make_spellbook()
    conduit = book.conjure(dynamic=True, name="root")
    try:
        dep1, dep2, root, other = _bound_graph(book)
        _resolves(conduit, root)
        conduit.cleanup_spell(spell=_spell(book, dep1))
        # The shared dependency is gone -> the dependent can no longer resolve.
        assert _resolves(conduit, root) is False
    finally:
        conduit.cleanup()


def test_cleanup_shared_dependency_breaks_the_other_root_too():
    book = _make_spellbook()
    conduit = book.conjure(dynamic=True, name="root")
    try:
        dep1, dep2, root, other = _bound_graph(book)
        _resolves(conduit, other)
        conduit.cleanup_spell(spell=_spell(book, dep1))
        assert _resolves(conduit, other) is False
    finally:
        conduit.cleanup()


def test_cleanup_unrelated_dependency_does_not_break_other_root():
    book = _make_spellbook()
    conduit = book.conjure(dynamic=True, name="root")
    try:
        dep1, dep2, root, other = _bound_graph(book)
        _resolves(conduit, root)
        _resolves(conduit, other)
        # dep2 is only used by _Root; disposing it must not break _OtherRoot (uses dep1).
        conduit.cleanup_spell(spell=_spell(book, dep2))
        assert _resolves(conduit, other) is True
    finally:
        conduit.cleanup()
