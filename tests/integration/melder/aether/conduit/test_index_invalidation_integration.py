"""
Integration tests -- invalidation / dependent rechecking (area B).

Formalizes `test_cleanup_dependency_breaks_dependents_experiment`. Cleaning up a shared
dependency's spell gates its dependents on the SpellSystemStates plane and re-resolves them.
Since 2026-09-26 (owner decision) the removed provider leaves an unresolved input rather
than a resolution failure:
    - a dependent object built before the cleanup keeps being served with the dependency
      object it already holds (Melder stops tracking that dependency, it does not close it);
    - building a dependent after the cleanup needs the value supplied by the meld, or a new
      provider; otherwise UnresolvedInputError is raised.

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
from melder.utilities.custom_exceptions.unresolved_input_error import UnresolvedInputError

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
        return conduit.meld(spell_id=spell_id) is not None
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


def test_cleanup_dependency_keeps_stored_dependent_with_its_dependency():
    book = _make_spellbook()
    conduit = book.conjure(dynamic=True, name="root")
    try:
        dep1, dep2, root, other = _bound_graph(book)
        built = conduit.meld(spell_id=root)
        held = built.dep1
        conduit.cleanup_spell(spell=_spell(book, dep1))
        # The stored dependent was built before the cleanup: it is served unchanged,
        # still holding the dependency object it was constructed with.
        again = conduit.meld(spell_id=root)
        assert again is built
        assert again.dep1 is held
    finally:
        conduit.cleanup()


def test_cleanup_shared_dependency_leaves_unbuilt_dependent_needing_the_input():
    book = _make_spellbook()
    conduit = book.conjure(dynamic=True, name="root")
    try:
        dep1, dep2, root, other = _bound_graph(book)
        conduit.cleanup_spell(spell=_spell(book, dep1))
        # _OtherRoot was never built: constructing it now needs dep1 from the meld.
        with pytest.raises(UnresolvedInputError) as caught:
            conduit.meld(spell_id=other)
        assert caught.value.unresolved_params == ("dep1",)
        supplied = _Dep1()
        assert conduit.meld(spell_id=other, override={"dep1": supplied}).dep1 is supplied
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
