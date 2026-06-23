"""tests/integration/melder/conduit/test_conduit_integration_scope_ordering_matrix.py

Validation: Not run (authored on a Python 3.10 sandbox where melder does not
import; this suite targets the 3.14t free-threaded build).

BUILD-LANE truth table for the scope-ordering / captive-dependency invariant.

Scope lifetime ranks (broad -> narrow), per ScopeOrderingStrategy:
    unique(0) < unique_per_conduit_cluster(1) < unique_per_conduit_lineage(2)
    < unique_per_conduit(3) < unique_per_spell_space(4) < many(5)

Rule under test: a spell may depend on an EQUAL-or-BROADER scope, but NOT on a
strictly NARROWER one. A broad-lived holder depending on a narrower-lived
instance is a CAPTIVE DEPENDENCY: the narrower instance is torn down (conduit
close, lineage end, spellspace exit) before its holder, leaving a dangling
reference. `many` is exempt on both sides -- it owns nothing and is never shared.

These tests assert the violation is a HARD conjure failure
(`SpellbookValidationError`). On the CURRENT runtime, conjure-time system
validation is advisory: ScopeOrderingStrategy emits the ERROR diagnostic, the
validation system computes `is_valid=False`, but conjure throws the verdict away
(SpellSystemValidationSystem.validate returns a state, never raises; the conduit
path only records per-conduit validity, best-effort). So every REJECTION case is
EXPECTED TO FAIL until the build-lane gate is promoted to fatal. That red signal
IS the deliverable -- it pins exactly which edges leak through the gate.

The ALLOWED cases (equal-or-broader, or `many` on either side) must conjure
cleanly today AND after the fix; they are the guard against an over-broad gate
that would start rejecting legal graphs once conjure honors `is_valid`.

This module asserts only the BUILD verdict (does conjure raise?). Runtime store
alignment -- whether a legal edge resolves the CORRECT shared instance -- lives
in the sibling file test_conduit_integration_scope_resolution_alignment.py.
"""
from __future__ import annotations

from typing import List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from melder.utilities.custom_exceptions.spellbook_validation_error import (
    SpellbookValidationError,
)
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)

_UNIQUE = Existence.unique
_CLUSTER = Existence.unique_per_conduit_cluster
_LINEAGE = Existence.unique_per_conduit_lineage
_UPC = Existence.unique_per_conduit
_SPELLSPACE = Existence.unique_per_spell_space
_MANY = Existence.many


@pytest.fixture(autouse=True)
def reset_singletons_for_scope_matrix() -> None:
    """Reset Nexus + Aether around each test for singleton isolation."""

    def _reset() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


class _Leaf:
    """Dependency leaf; re-bound at each requested ``dep`` existence."""

    def __init__(self) -> None:
        """Construct one leaf."""
        pass


class _Parent:
    """Holder that depends on ``_Leaf``; re-bound at each requested ``parent`` existence."""

    def __init__(self, dep: _Leaf) -> None:
        """Store the injected leaf so DI must resolve the edge."""
        self.dep = dep


def _book(tag: str) -> Spellbook:
    """Build one dynamic spellbook whose config frame matches its aetheric frame."""
    frame = f"intg-scope-{tag}"
    configuration = SpellbookConfiguration(frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def _ids(pairs: List[Tuple[Existence, Existence]]) -> List[str]:
    """Render readable parametrize ids: ``parent->dep``."""
    return [f"{parent.name}->{dep.name}" for parent, dep in pairs]


# -- Illegal edges: a broader holder depending on a strictly narrower scope. ---
# Each row is (parent_existence, dependency_existence); parent is broader-lived.
_REJECTED: List[Tuple[Existence, Existence]] = [
    (_UNIQUE, _CLUSTER),
    (_UNIQUE, _LINEAGE),
    (_UNIQUE, _UPC),
    (_UNIQUE, _SPELLSPACE),
    (_CLUSTER, _LINEAGE),
    (_CLUSTER, _UPC),
    (_CLUSTER, _SPELLSPACE),
    (_LINEAGE, _UPC),
    (_LINEAGE, _SPELLSPACE),
    (_UPC, _SPELLSPACE),
]

# -- Legal edges: depend on an equal-or-broader scope, or `many` on either side.
_ALLOWED: List[Tuple[Existence, Existence]] = [
    (_UNIQUE, _UNIQUE),
    (_CLUSTER, _UNIQUE),
    (_CLUSTER, _CLUSTER),
    (_LINEAGE, _UNIQUE),
    (_LINEAGE, _CLUSTER),
    (_LINEAGE, _LINEAGE),
    (_UPC, _UNIQUE),
    (_UPC, _LINEAGE),
    (_UPC, _UPC),
    (_SPELLSPACE, _UNIQUE),
    (_SPELLSPACE, _LINEAGE),
    (_SPELLSPACE, _UPC),
    (_SPELLSPACE, _SPELLSPACE),
    # `many` is exempt on both sides:
    (_UNIQUE, _MANY),
    (_SPELLSPACE, _MANY),
    (_MANY, _UNIQUE),
    (_MANY, _SPELLSPACE),
]


@pytest.mark.parametrize("parent,dep", _REJECTED, ids=_ids(_REJECTED))
def test_broad_holder_on_narrower_dependency_is_rejected_at_conjure(
    parent: Existence, dep: Existence
) -> None:
    """A holder depending on a strictly narrower scope must fail conjure.

    EXPECTED TO FAIL on current runtime: conjure does not yet escalate the
    scope_ordering_violation ERROR to a raise. Passing means the build-lane gate
    is enforced.
    """
    book = _book(f"rej-{parent.name}-{dep.name}")
    book.bind(spell=_Leaf, existence=dep, permissions="create")
    book.bind(spell=_Parent, existence=parent, permissions="create")
    try:
        with pytest.raises(SpellbookValidationError):
            book.conjure(dynamic=True, name="root")
    finally:
        book.cleanup()


@pytest.mark.parametrize("parent,dep", _ALLOWED, ids=_ids(_ALLOWED))
def test_equal_or_broader_dependency_conjures_cleanly(
    parent: Existence, dep: Existence
) -> None:
    """A holder depending on an equal-or-broader scope (or `many`) must conjure.

    Guards against an over-broad gate: once conjure honors `is_valid`, these
    legal graphs must keep building.
    """
    book = _book(f"ok-{parent.name}-{dep.name}")
    book.bind(spell=_Leaf, existence=dep, permissions="create")
    book.bind(spell=_Parent, existence=parent, permissions="create")
    root = None
    try:
        root = book.conjure(dynamic=True, name="root")
        assert root is not None, "legal scope edge must produce a root conduit"
    finally:
        if root is not None:
            root.permanent_cleanup()
        book.cleanup()


def test_self_edge_unique_on_unique_is_legal() -> None:
    """Sanity floor: equal scope (unique depends on unique) is never a violation."""
    book = _book("self-unique")
    book.bind(spell=_Leaf, existence=_UNIQUE, permissions="create")
    book.bind(spell=_Parent, existence=_UNIQUE, permissions="create")
    root = None
    try:
        root = book.conjure(dynamic=True, name="root")
        assert root is not None
    finally:
        if root is not None:
            root.permanent_cleanup()
        book.cleanup()


def test_many_holder_on_spellspace_dependency_is_legal() -> None:
    """`many` may depend on the narrowest real scope -- it is never captive."""
    book = _book("many-on-ss")
    book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    book.bind(spell=_Parent, existence=_MANY, permissions="create")
    root = None
    try:
        root = book.conjure(dynamic=True, name="root")
        assert root is not None
    finally:
        if root is not None:
            root.permanent_cleanup()
        book.cleanup()
