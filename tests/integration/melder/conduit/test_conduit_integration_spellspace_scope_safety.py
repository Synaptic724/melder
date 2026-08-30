"""tests/integration/melder/conduit/test_conduit_integration_spellspace_scope_safety.py

Validation: Not run (authored on a Python 3.10 sandbox where melder does not
import; this suite targets the 3.14t free-threaded build).

PROVE-IT suite for `unique_per_spell_space`. Source analysis says spellspace is
NOT part of the lineage/cluster caller-store defect: its leaf door reads
`caller_creations` (creation_runtime_door_compiler.py:571), and `enter_spellspace`
installs the active-scope store AS the conduit's own creations, so a dependency
melded inside the scope inherits the scope store the same way `unique_per_conduit`
inherits the per-conduit store. This file tries to FALSIFY that on every front
that exposed the lineage bug:

    within-scope COUNT, the DEPENDENCY path, TRANSITIVE depth, multi-holder DEDUP,
    the LESSER case, lesser/root ISOLATION, re-entry CLEARING, and CONCURRENCY.

Every test is written to PASS. If any fails, spellspace shares the scope-store
defect and must be fixed in the same lane-1 pass as lineage and cluster.
"""
from __future__ import annotations

import threading
from typing import Any, List

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)

_SPELLSPACE = Existence.unique_per_spell_space
_MANY = Existence.many


@pytest.fixture(autouse=True)
def reset_singletons_for_spellspace_safety() -> None:
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
    """Spellspace-scoped leaf."""

    def __init__(self) -> None:
        """Construct one leaf."""
        pass


class _Holder:
    """`many` holder depending on a spellspace ``_Leaf`` (legal broader edge)."""

    def __init__(self, dep: _Leaf) -> None:
        """Store the injected leaf."""
        self.dep = dep


class _HolderB:
    """A SECOND `many` holder on the same spellspace ``_Leaf`` (dedup probe)."""

    def __init__(self, dep: _Leaf) -> None:
        """Store the injected leaf."""
        self.dep = dep


class _Mid:
    """Mid layer for the transitive chain: depends on the spellspace ``_Leaf``."""

    def __init__(self, leaf: _Leaf) -> None:
        """Store the injected leaf."""
        self.leaf = leaf


class _Top:
    """Top layer for the transitive chain: depends on ``_Mid`` (two hops to leaf)."""

    def __init__(self, mid: _Mid) -> None:
        """Store the injected mid."""
        self.mid = mid


def _book(tag: str) -> Spellbook:
    """Dynamic-frame spellbook (config frame matches aetheric frame)."""
    frame = f"intg-ss-{tag}"
    configuration = SpellbookConfiguration(frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=configuration)


# =====================================================================
# Direct-meld baselines.
# =====================================================================
def test_spellspace_same_instance_within_one_scope() -> None:
    """Repeated direct melds inside one scope resolve the same instance."""
    book = _book("same-in-scope")
    sid = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as space:
            assert space.meld(spell_id=sid) is space.meld(spell_id=sid)
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_spellspace_distinct_across_two_scopes() -> None:
    """Two separate scopes on the same conduit resolve different instances."""
    book = _book("distinct-scopes")
    sid = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as s1:
            first = s1.meld(spell_id=sid)
        with root.enter_spellspace() as s2:
            second = s2.meld(spell_id=sid)
        assert first is not second
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# COUNT: exactly one instance per scope, shared by direct + dependency melds.
# =====================================================================
def test_spellspace_exactly_one_instance_within_scope() -> None:
    """Within one scope, the direct leaf and N holder dependencies are ONE object."""
    n_holders = 5
    book = _book("count")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    seen: List[Any] = []
    try:
        with root.enter_spellspace() as space:
            seen.append(space.meld(spell_id=leaf_id))
            for _ in range(n_holders):
                seen.append(space.meld(spell_id=holder_id).dep)
        assert len({id(x) for x in seen}) == 1, (
            f"one spellspace instance per scope; saw {len({id(x) for x in seen})}"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# DEPENDENCY path: a many holder's spellspace dep == the direct meld.
# =====================================================================
def test_spellspace_dependency_into_many_holder_resolves_scope_instance() -> None:
    """A `many` holder's spellspace dependency is the active scope's instance."""
    book = _book("many-dep")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as space:
            direct = space.meld(spell_id=leaf_id)
            holder = space.meld(spell_id=holder_id)
            assert holder.dep is direct
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# TRANSITIVE: two-hop dependency still lands in the scope store.
# =====================================================================
def test_spellspace_transitive_dependency_resolves_scope_instance() -> None:
    """Top -> Mid -> spellspace Leaf, melded in a scope, reaches the scope instance."""
    book = _book("transitive")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    book.bind(spell=_Mid, existence=_MANY, permissions="create")
    top_id = book.bind(spell=_Top, existence=_MANY, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as space:
            direct = space.meld(spell_id=leaf_id)
            top = space.meld(spell_id=top_id)
            assert top.mid.leaf is direct
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# DEDUP: two distinct holders in one scope share the one instance.
# =====================================================================
def test_spellspace_two_holders_share_one_scope_instance() -> None:
    """Two different holders in one scope receive the same spellspace instance."""
    book = _book("dedup")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    holder_a = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    holder_b = book.bind(spell=_HolderB, existence=_MANY, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as space:
            direct = space.meld(spell_id=leaf_id)
            a = space.meld(spell_id=holder_a)
            b = space.meld(spell_id=holder_b)
            assert a.dep is b.dep
            assert a.dep is direct
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# THE LESSER CASE: the exact shape that broke lineage. A holder melded in a
# LESSER's scope must resolve the LESSER scope's instance, not leak elsewhere.
# =====================================================================
def test_spellspace_dependency_on_lesser_resolves_lesser_scope_instance() -> None:
    """A many holder melded inside a LESSER's scope gets that scope's instance."""
    book = _book("lesser-dep")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        lesser = root.create_lesser_conduit()
        try:
            with lesser.enter_spellspace() as space:
                direct = space.meld(spell_id=leaf_id)
                holder = space.meld(spell_id=holder_id)
                assert holder.dep is direct, (
                    "a lesser's scope dependency must be that scope's instance"
                )
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_spellspace_lesser_scope_isolated_from_root_scope() -> None:
    """A lesser's active scope owns a different instance than the root's scope."""
    book = _book("lesser-iso")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as root_space:
            root_inst = root_space.meld(spell_id=leaf_id)
            lesser = root.create_lesser_conduit()
            try:
                with lesser.enter_spellspace() as lesser_space:
                    lesser_inst = lesser_space.meld(spell_id=leaf_id)
                    assert lesser_inst is not root_inst, (
                        "each conduit's scope owns its own spellspace instance"
                    )
            finally:
                lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# CLEARING: re-entering a scope yields a fresh instance (no carry-over).
# =====================================================================
def test_spellspace_reentry_yields_fresh_instance() -> None:
    """Exiting and re-entering a scope produces a new instance (scope cleared)."""
    book = _book("reentry")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as s1:
            first = s1.meld(spell_id=holder_id).dep
        with root.enter_spellspace() as s2:
            second = s2.meld(spell_id=holder_id).dep
        assert first is not second, "a re-entered scope must not reuse the old instance"
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# CONCURRENCY: independent scopes across threads stay isolated (no cross-leak,
# no shared scope store) -- the 3.14t no-GIL threadsafety front.
# =====================================================================
def test_spellspace_concurrent_scopes_are_isolated() -> None:
    """N threads, each its own lesser + scope, resolve N distinct instances."""
    n_threads = 8
    book = _book("concurrent")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    results: List[Any] = []
    lock = threading.Lock()
    barrier = threading.Barrier(n_threads)

    def _worker() -> None:
        lesser = root.create_lesser_conduit()
        try:
            barrier.wait()
            with lesser.enter_spellspace() as space:
                inst = space.meld(spell_id=leaf_id)
            with lock:
                results.append(inst)
        finally:
            lesser.cleanup()

    try:
        threads = [threading.Thread(target=_worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == n_threads
        assert len({id(x) for x in results}) == n_threads, (
            "each concurrent scope must own a distinct instance (no shared store)"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()
