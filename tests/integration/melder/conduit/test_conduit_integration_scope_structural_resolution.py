"""tests/integration/melder/conduit/test_conduit_integration_scope_structural_resolution.py

Validation: Not run (authored on a Python 3.10 sandbox where melder does not
import; this suite targets the 3.14t free-threaded build).

STRUCTURAL probes for the dependency-path store-routing defect
(`root_creations = caller_creations` in the codegen doors). The sibling
alignment file catches the bug only where it is VISIBLE -- on a lesser, where the
caller store differs from the lineage-root store. That leaves the actual cause
under-probed, because:

  * On the ROOT, caller IS the root store, so a lineage/cluster dependency
    resolves correctly BY COINCIDENCE. A test that only melds on the root passes
    for the wrong reason (see test_..._on_root_is_masked below).
  * Object-identity-vs-a-known-good asserts "is it root_leaf?" but does not prove
    the structural invariant "the whole lineage owns exactly ONE instance" or
    "the direct path and the dependency path AGREE."
  * Cluster-as-a-dependency was never exercised.

These tests attack the cause from seven angles: root/lesser DIVERGENCE,
instance-COUNT, direct-vs-dependency PATH AGREEMENT, TRANSITIVE depth, multi-
holder DEDUP, LIFETIME across sibling cleanup, and the CLUSTER dependency path
through a lesser member. The lineage/cluster ones are expected to FAIL on the
current runtime; the root-masking one is expected to PASS (that is the point --
it demonstrates why root-only coverage gives false comfort).
"""
from __future__ import annotations

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

_LINEAGE = Existence.unique_per_conduit_lineage
_CLUSTER = Existence.unique_per_conduit_cluster
_SPELLSPACE = Existence.unique_per_spell_space
_MANY = Existence.many


@pytest.fixture(autouse=True)
def reset_singletons_for_structural() -> None:
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
    """Scoped leaf (bound lineage or cluster per test)."""

    def __init__(self) -> None:
        """Construct one leaf."""
        pass


class _Holder:
    """`many` holder depending on ``_Leaf``."""

    def __init__(self, dep: _Leaf) -> None:
        """Store the injected leaf."""
        self.dep = dep


class _HolderB:
    """A SECOND distinct `many` holder on the same ``_Leaf`` (dedup probe)."""

    def __init__(self, dep: _Leaf) -> None:
        """Store the injected leaf."""
        self.dep = dep


class _Mid:
    """Mid layer for the transitive chain: depends on ``_Leaf``."""

    def __init__(self, leaf: _Leaf) -> None:
        """Store the injected leaf."""
        self.leaf = leaf


class _Top:
    """Top layer for the transitive chain: depends on ``_Mid`` (two hops to leaf)."""

    def __init__(self, mid: _Mid) -> None:
        """Store the injected mid."""
        self.mid = mid


def _static_book(tag: str) -> Spellbook:
    """Automatic-frame spellbook (proven lineage pattern), dynamic=False path."""
    book = Spellbook(aetheric_frame=f"intg-struct-{tag}")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return book


def _cluster_config() -> SpellbookConfiguration:
    """Default-frame dynamic config for cluster member books (proven pattern)."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _dynamic_book(tag: str) -> Spellbook:
    """Dynamic-frame spellbook for the spellspace path (frame name matches config)."""
    frame = f"intg-struct-dyn-{tag}"
    configuration = SpellbookConfiguration(frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=configuration)


# =====================================================================
# 0. The MASKING control: the same broken path on the ROOT passes.
# =====================================================================
def test_lineage_dependency_on_root_is_masked_and_passes() -> None:
    """CONTROL: a holder melded on the ROOT resolves the lineage dep correctly --
    NOT because routing is right, but because the caller store IS the root store.

    This is expected to PASS today. Its job is to document why root-only coverage
    is false comfort: the defect is invisible exactly where caller == root.
    """
    book = _static_book("mask-root")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        root_holder = root.meld(spell=holder_id)
        assert root_holder.dep is root_leaf, (
            "on the root the dependency path coincidentally matches the direct path"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# 1. DIVERGENCE: the dependency's identity must NOT depend on who melds it.
# =====================================================================
def test_lineage_dependency_identity_is_invariant_to_melding_conduit() -> None:
    """The SAME holder melded on the root and on a lesser must inject the SAME
    lineage instance. If they diverge, the dependency is being stored per-caller.

    This asserts the structural inconsistency directly, without presuming which
    instance is 'correct'. Expected to FAIL on current runtime.
    """
    book = _static_book("diverge")
    book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_holder = root.meld(spell=holder_id)
        lesser = root.create_lesser_conduit()
        try:
            lesser_holder = lesser.meld(spell=holder_id)
        finally:
            lesser.cleanup()
        assert root_holder.dep is lesser_holder.dep, (
            "a lineage dependency must be identical regardless of the melding conduit"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# 2. COUNT: the whole lineage must own EXACTLY ONE instance.
# =====================================================================
def test_lineage_dependency_yields_exactly_one_instance_across_lineage() -> None:
    """Across the root and N lessers, the dependency must resolve to ONE object.

    A count-based invariant (not pairwise identity): the bug yields one instance
    per caller store, so the set size blows up to N+1. Expected to FAIL.
    """
    n_lessers = 5
    book = _static_book("count")
    book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    seen: List[Any] = []
    try:
        seen.append(root.meld(spell=holder_id).dep)
        for _ in range(n_lessers):
            lesser = root.create_lesser_conduit()
            try:
                seen.append(lesser.meld(spell=holder_id).dep)
            finally:
                lesser.cleanup()
        assert len({id(x) for x in seen}) == 1, (
            f"the lineage must own exactly one instance; saw {len({id(x) for x in seen})}"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# 3. PATH AGREEMENT: direct meld and dependency meld must resolve the same thing.
# =====================================================================
def test_lineage_direct_and_dependency_paths_agree_on_lesser() -> None:
    """On a lesser, the DIRECT meld of the leaf and the DEPENDENCY-injected leaf
    must be the same object. This isolates the defect to the dependency path:
    the direct path is already correct; the dependency path is not.

    Expected: the direct assert passes, the path-agreement assert FAILS.
    """
    book = _static_book("agree")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        lesser = root.create_lesser_conduit()
        try:
            lesser_direct = lesser.meld(spell=leaf_id)
            lesser_dep = lesser.meld(spell=holder_id).dep
        finally:
            lesser.cleanup()
        assert lesser_direct is root_leaf, "direct lineage meld on a lesser is correct"
        assert lesser_dep is lesser_direct, (
            "the dependency path must resolve the same instance as the direct path"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# 4. TRANSITIVE: the defect must not survive deeper in the dependency chain.
# =====================================================================
def test_lineage_transitive_dependency_through_lesser_resolves_root() -> None:
    """A two-hop chain (Top -> Mid -> lineage Leaf) melded on a lesser must reach
    the ROOT lineage instance at the bottom. Tests the fix holds through the whole
    resolution chain, not just the first hop. Expected to FAIL.
    """
    book = _static_book("transitive")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    book.bind(spell=_Mid, existence=_MANY, permissions="create")
    top_id = book.bind(spell=_Top, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        lesser = root.create_lesser_conduit()
        try:
            lesser_top = lesser.meld(spell=top_id)
        finally:
            lesser.cleanup()
        assert lesser_top.mid.leaf is root_leaf, (
            "a transitive lineage dependency must still resolve the ROOT instance"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# 5. DEDUP: two different holders on a lesser must share the one instance.
# =====================================================================
def test_lineage_two_distinct_holders_on_lesser_share_one_instance() -> None:
    """Two different holders melded on the same lesser must receive the SAME
    lineage instance (and it must equal the root's). Tests dedup within the
    lineage store via the dependency path. Expected to FAIL.
    """
    book = _static_book("dedup")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    holder_a = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    holder_b = book.bind(spell=_HolderB, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        lesser = root.create_lesser_conduit()
        try:
            a = lesser.meld(spell=holder_a)
            b = lesser.meld(spell=holder_b)
        finally:
            lesser.cleanup()
        assert a.dep is b.dep, "both holders must share one lineage instance"
        assert a.dep is root_leaf, "and it must be the shared ROOT instance"
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# 6. LIFETIME: the lineage instance must be the durable root one, not a
#    per-lesser transient that dies with its caller.
# =====================================================================
def test_lineage_dependency_is_durable_across_sibling_lesser_churn() -> None:
    """A lineage dependency resolved on lesser A, then on lesser B after A is gone,
    must be the same durable ROOT instance. Per-caller storage would hand each
    lesser its own short-lived instance (the captive-dependency hazard). FAIL.
    """
    book = _static_book("lifetime")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        lesser_a = root.create_lesser_conduit()
        try:
            dep_a = lesser_a.meld(spell=holder_id).dep
        finally:
            lesser_a.cleanup()
        lesser_b = root.create_lesser_conduit()
        try:
            dep_b = lesser_b.meld(spell=holder_id).dep
        finally:
            lesser_b.cleanup()
        assert dep_a is root_leaf and dep_b is root_leaf, (
            "both lessers must resolve the durable ROOT lineage instance"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# 7. CLUSTER dependency path -- REMOVED 2026-08-02.
#    The test here bound the SAME class in two Spellbooks on one frame so a
#    member conduit could meld a holder depending on a cluster spell. Owner
#    ruling: a spell_id is unique per frame, so that setup is not a legal world
#    and the test was probing a scenario the system must refuse. Removed rather
#    than repaired: `_Holder.__init__(self, dep: _Leaf)` is a hard constructor
#    dependency resolved at conjure, while cluster shares arrive afterwards, so
#    there is no ordering that makes a member's own holder resolvable without
#    the duplicate bind. Re-expressing it needs SpellContract (late-bound
#    cross-conduit socket), not a second bind. See the conjure integrity sweep
#    `Spellbook._spell_id_integrity_checker`.
# =====================================================================


# =====================================================================
# 8. SPELLSPACE dependency path -- closing the blast-radius question.
#    spellspace's leaf door reads caller_creations (door_compiler.py:571-583),
#    same shape as upc. The discriminating legal edge is a `many` holder
#    depending on a spellspace leaf, melded INSIDE a scope: its dep must be that
#    scope's instance (== a direct meld in the same scope). PASS => spellspace is
#    correctly scope-threaded and NOT part of the caller-store defect; FAIL =>
#    spellspace is a third casualty alongside lineage and cluster.
# =====================================================================
def test_spellspace_dependency_into_many_holder_resolves_scope_instance() -> None:
    """A `many` holder depending on a spellspace leaf, melded inside a scope, must
    receive that scope's spellspace instance (== the direct meld in the scope)."""
    book = _dynamic_book("ss-many-dep")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    holder_id = book.bind(spell=_Holder, existence=_MANY, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as space:
            direct = space.meld(spell=leaf_id)
            holder = space.meld(spell=holder_id)
            assert holder.dep is direct, (
                "a many holder's spellspace dependency must be the active scope instance"
            )
    finally:
        root.permanent_cleanup()
        book.cleanup()
