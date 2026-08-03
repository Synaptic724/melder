"""tests/integration/melder/conduit/test_conduit_integration_lineage_isolation.py

Validation: Not run.

Integration tests through the real meld front door for `unique_per_conduit_lineage`:
    - cross-root ISOLATION: many independent roots each own a DISTINCT lineage
      instance (no cross-leak);
    - DEPENDENCY routing: a parent that DEPENDS on a lineage spell, melded on a
      lesser, resolves the ROOT's lineage instance -- the creation-store routing
      path that regressed. Covered for a `many` parent and a `unique_per_conduit`
      parent, and across multiple roots.

Intra-lineage sharing / store wiring lives in the component test
(tests/component/melder/aether/conduit/test_conduit_component_lineage.py).
"""

from __future__ import annotations

from typing import Any, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus

_LINEAGE = Existence.unique_per_conduit_lineage
_MANY = Existence.many
_UPC = Existence.unique_per_conduit


@pytest.fixture(autouse=True)
def reset_singletons_for_integration_lineage() -> None:
    """Reset Nexus + Aether around each integration lineage test for isolation."""

    def _reset() -> None:
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
        aether = Aether()
        Spellbook._aether = aether
        Conduit._aether = aether

    _reset()
    yield
    _reset()


class _LineageThing:
    def __init__(self) -> None:
        pass


class _LineageLeaf:
    def __init__(self) -> None:
        pass


class _ManyParentWithLineageDep:
    def __init__(self, dep: _LineageLeaf) -> None:
        self.dep = dep


class _UpcParentWithLineageDep:
    def __init__(self, dep: _LineageLeaf) -> None:
        self.dep = dep


def _lineage_book(tag: str) -> Spellbook:
    book = Spellbook(aetheric_frame=f"intg-lin-{tag}")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return book


def test_dependency_many_parent_resolves_root_lineage_instance() -> None:
    """A `many` parent on a lesser must receive the ROOT lineage instance as dep."""
    book = _lineage_book("dep-many")
    leaf_id = book.bind(spell=_LineageLeaf, existence=_LINEAGE, permissions="create")
    parent_id = book.bind(spell=_ManyParentWithLineageDep, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_parent = root.meld(spell=parent_id)
        root_leaf = root.meld(spell=leaf_id)
        assert root_parent.dep is root_leaf
        lesser = root.create_lesser_conduit()
        try:
            lesser_parent = lesser.meld(spell=parent_id)
        finally:
            lesser.cleanup()
        assert lesser_parent is not root_parent, "many parents are per-conduit"
        assert lesser_parent.dep is root_leaf, (
            "a lesser's parent must resolve the ROOT lineage instance as its dependency"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_dependency_upc_parent_resolves_root_lineage_instance() -> None:
    """Same as above but the parent is unique_per_conduit instead of many."""
    book = _lineage_book("dep-upc")
    leaf_id = book.bind(spell=_LineageLeaf, existence=_LINEAGE, permissions="create")
    parent_id = book.bind(spell=_UpcParentWithLineageDep, existence=_UPC, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        lesser = root.create_lesser_conduit()
        try:
            lesser_parent = lesser.meld(spell=parent_id)
        finally:
            lesser.cleanup()
        assert lesser_parent.dep is root_leaf, (
            "unique_per_conduit parent must still resolve the ROOT lineage dependency"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()



# ---------------------------------------------------------------------------
# DELETED 2026-08-02 - EPIC-2026-08-02-process-wide-spell-id-uniqueness
#
# Deleted:
#   test_many_roots_each_own_a_distinct_lineage_instance
#   test_dependency_isolated_across_roots
#
# These bound the SAME class once per root/cluster, each on its OWN FRAME, and
# relied on collisions being frame-scoped to get away with it - the fixtures
# said so themselves ("the same class is reused safely, since collisions are
# frame-scoped"). Process-wide uniqueness retired that rule, so the setup is no
# longer expressible.
#
# They are deleted rather than repaired because they were TAUTOLOGIES. Putting
# each root on its own frame gives it its own book, its own conduit and its own
# instance no matter what the scope does - so "the instances are distinct"
# passed by construction and would have kept passing with unique_per_conduit_lineage
# resolution entirely removed. There is no coverage here to preserve.
#
# REAL coverage needs several scopes sharing ONE binding inside ONE frame. That
# shape IS reachable and always was - `_form_cluster` already builds it: one
# book binds, further Spellbooks on the SAME frame conjure WITHOUT binding, and
# clusters are created on the CONDUIT CLOUD, not the frame. Two clusters off one
# binding is `create_cluster("a")` + `create_cluster("b")` on the same cloud.
# Only that shape actually exercises unique_per_conduit_lineage; the deleted
# tests never did.
# ---------------------------------------------------------------------------
