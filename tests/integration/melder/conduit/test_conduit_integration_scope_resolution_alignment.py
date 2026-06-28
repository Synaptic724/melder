"""tests/integration/melder/conduit/test_conduit_integration_scope_resolution_alignment.py

Validation: Not run (authored on a Python 3.10 sandbox where melder does not
import; this suite targets the 3.14t free-threaded build).

RUNTIME-LANE matrix for the scope-alignment invariant:

    declared existence  ==  the creation store it resolves from  ==  its lifetime

An instance must resolve from the store that matches its declared scope, whether
it is melded DIRECTLY or injected as a DEPENDENCY, and whether the caller is the
root conduit, a lesser, a nested lesser, or several threads at once. The known
defect is that the codegen doors thread only ``caller_creations`` and emit
``root_creations = caller_creations``, so a lineage/cluster instance reached as a
DEPENDENCY lands in the caller's (per-conduit) store instead of the lineage-root
/ cluster-leader store. Sharing then breaks on lessers while the direct meld and
the root-local path still look fine.

Expected split on the CURRENT runtime:
  - unique / unique_per_conduit / many resolution: PASS (their store is the
    caller or a frame singleton, which the doors already thread correctly).
  - lineage AS A DEPENDENCY on a lesser: FAIL -- resolves a lesser-local instance
    instead of the shared lineage-root instance. These are the bug-pinning reds.
  - cluster: PROBES of the elected-leader store-resolution path, which the
    existing suite does not exercise; they surface the real cluster API/behavior.

These tests assert object identity (``is``) because scope alignment is precisely
a question of WHICH instance you get, not whether you get one.
"""
from __future__ import annotations

import threading
from typing import Any, List, Tuple

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

_UNIQUE = Existence.unique
_CLUSTER = Existence.unique_per_conduit_cluster
_LINEAGE = Existence.unique_per_conduit_lineage
_UPC = Existence.unique_per_conduit
_SPELLSPACE = Existence.unique_per_spell_space
_MANY = Existence.many


@pytest.fixture(autouse=True)
def reset_singletons_for_alignment() -> None:
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
    """Dependency leaf; re-bound at each requested existence per test."""

    def __init__(self) -> None:
        """Construct one leaf."""
        pass


class _Parent:
    """Holder that depends on ``_Leaf`` so DI must resolve the edge by type."""

    def __init__(self, dep: _Leaf) -> None:
        """Store the injected leaf."""
        self.dep = dep


def _static_book(tag: str) -> Spellbook:
    """Automatic-frame spellbook (proven lineage-isolation pattern), dynamic=False path."""
    book = Spellbook(aetheric_frame=f"intg-align-{tag}")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return book


def _dynamic_config(frame: str) -> SpellbookConfiguration:
    """Dynamic config whose frame name matches the spellbook's aetheric frame."""
    configuration = SpellbookConfiguration(frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _dynamic_book(tag: str) -> Spellbook:
    """Dynamic-frame spellbook for spellspace/cluster paths."""
    frame = f"intg-align-dyn-{tag}"
    return Spellbook(aetheric_frame=frame, configuration=_dynamic_config(frame))


def _cluster_config() -> SpellbookConfiguration:
    """Default-frame dynamic config shared verbatim across cluster member books.

    Cluster membership requires the member conduits to live in the SAME frame, so
    both books take this one config object with NO explicit aetheric_frame (the
    proven pattern in test_conduit_integration_clusters_spellspace). Passing a
    named frame to the config without the matching aetheric_frame trips the
    "name does not match the aetheric frame" guard at construction.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


# =====================================================================
# unique -- frame singleton: one instance per frame, everywhere.
# =====================================================================
def test_unique_shared_across_root_and_lesser() -> None:
    """A `unique` spell resolves the same instance on the root and a lesser."""
    book = _static_book("u-share")
    sid = book.bind(spell=_Leaf, existence=_UNIQUE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_inst = root.meld(spell=sid)
        lesser = root.create_lesser_conduit()
        try:
            assert lesser.meld(spell=sid) is root_inst
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_unique_shared_across_nested_lesser() -> None:
    """A `unique` spell stays the same instance two lesser levels deep."""
    book = _static_book("u-nested")
    sid = book.bind(spell=_Leaf, existence=_UNIQUE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_inst = root.meld(spell=sid)
        lesser = root.create_lesser_conduit()
        try:
            nested = lesser.create_lesser_conduit()
            try:
                assert nested.meld(spell=sid) is root_inst
            finally:
                nested.cleanup()
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_unique_dependency_shared_across_lessers() -> None:
    """A `unique` dependency injected into per-conduit holders is the same object."""
    book = _static_book("u-dep")
    leaf_id = book.bind(spell=_Leaf, existence=_UNIQUE, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        root_parent = root.meld(spell=parent_id)
        assert root_parent.dep is root_leaf
        lesser = root.create_lesser_conduit()
        try:
            lesser_parent = lesser.meld(spell=parent_id)
        finally:
            lesser.cleanup()
        assert lesser_parent.dep is root_leaf, (
            "unique dependency must be the shared frame singleton on a lesser too"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# unique_per_conduit -- one instance per conduit.
# =====================================================================
def test_upc_stable_within_a_single_conduit() -> None:
    """`unique_per_conduit` returns the same instance for repeated melds on one conduit."""
    book = _static_book("upc-stable")
    sid = book.bind(spell=_Leaf, existence=_UPC, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        assert root.meld(spell=sid) is root.meld(spell=sid)
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_upc_distinct_between_root_and_lesser() -> None:
    """`unique_per_conduit` gives the root and a lesser DIFFERENT instances."""
    book = _static_book("upc-distinct")
    sid = book.bind(spell=_Leaf, existence=_UPC, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_inst = root.meld(spell=sid)
        lesser = root.create_lesser_conduit()
        try:
            assert lesser.meld(spell=sid) is not root_inst
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_upc_dependency_is_per_conduit() -> None:
    """A `unique_per_conduit` dependency differs between the root holder and a lesser holder."""
    book = _static_book("upc-dep")
    leaf_id = book.bind(spell=_Leaf, existence=_UPC, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_parent = root.meld(spell=parent_id)
        lesser = root.create_lesser_conduit()
        try:
            lesser_parent = lesser.meld(spell=parent_id)
        finally:
            lesser.cleanup()
        assert root_parent.dep is not lesser_parent.dep, (
            "per-conduit dependency must not leak across conduits"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_upc_shared_across_spellspaces_of_one_conduit() -> None:
    """`unique_per_conduit` is the conduit's single instance -- shared across the
    conduit's direct meld AND every spellspace entered on that conduit.

    A spellspace is a scope WITHIN its owner conduit, so a `unique_per_conduit`
    spell resolved from inside any spellspace must land in the owner conduit's
    store (``meld._conduit_creations``), never a per-spellspace store -- that is
    reserved for `unique_per_spell_space`.
    """
    book = _dynamic_book("upc-across-ss")
    sid = book.bind(spell=_Leaf, existence=_UPC, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        direct = root.meld(spell=sid)
        with root.enter_spellspace() as s1:
            in_s1 = s1.meld(spell=sid)
        with root.enter_spellspace() as s2:
            in_s2 = s2.meld(spell=sid)
        assert in_s1 is direct, (
            "a unique_per_conduit melded inside a spellspace must be the conduit's instance"
        )
        assert in_s2 is in_s1, (
            "unique_per_conduit is shared across every spellspace of the same conduit"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# unique_per_conduit_lineage -- one instance per lineage root.
# =====================================================================
def test_lineage_shared_across_root_and_lesser() -> None:
    """`unique_per_conduit_lineage` is shared between the root and its lesser."""
    book = _static_book("lin-share")
    sid = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_inst = root.meld(spell=sid)
        lesser = root.create_lesser_conduit()
        try:
            assert lesser.meld(spell=sid) is root_inst
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_lineage_shared_across_nested_lesser() -> None:
    """`unique_per_conduit_lineage` stays shared two lesser levels deep."""
    book = _static_book("lin-nested")
    sid = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_inst = root.meld(spell=sid)
        lesser = root.create_lesser_conduit()
        try:
            nested = lesser.create_lesser_conduit()
            try:
                assert nested.meld(spell=sid) is root_inst, (
                    "nested lesser must still share the lineage-root instance"
                )
            finally:
                nested.cleanup()
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_lineage_distinct_across_separate_roots() -> None:
    """Two independent roots each own a DISTINCT lineage instance (no cross-leak)."""
    n_roots = 4
    keepalive: List[Tuple[Spellbook, Any]] = []
    instances: List[Any] = []
    try:
        for i in range(n_roots):
            book = _static_book(f"lin-iso-{i}")
            sid = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
            root = book.conjure(name=f"root-{i}", dynamic=False)
            keepalive.append((book, root))
            instances.append(root.meld(spell=sid))
        assert len({id(x) for x in instances}) == n_roots
    finally:
        for book, root in keepalive:
            root.permanent_cleanup()
            book.cleanup()


def test_lineage_dependency_into_many_parent_resolves_root_instance() -> None:
    """BUG PIN: a `many` holder on a lesser must receive the ROOT lineage dep."""
    book = _static_book("lin-dep-many")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        lesser = root.create_lesser_conduit()
        try:
            lesser_parent = lesser.meld(spell=parent_id)
        finally:
            lesser.cleanup()
        assert lesser_parent.dep is root_leaf, (
            "lesser holder's lineage dependency must be the shared ROOT instance"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_lineage_dependency_into_upc_parent_resolves_root_instance() -> None:
    """BUG PIN: a `unique_per_conduit` holder on a lesser must receive the ROOT lineage dep."""
    book = _static_book("lin-dep-upc")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_UPC, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_leaf = root.meld(spell=leaf_id)
        lesser = root.create_lesser_conduit()
        try:
            lesser_parent = lesser.meld(spell=parent_id)
        finally:
            lesser.cleanup()
        assert lesser_parent.dep is root_leaf, (
            "per-conduit holder's lineage dependency must be the shared ROOT instance"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_lineage_legal_dependency_on_unique_resolves_shared() -> None:
    """A lineage holder may depend on a broader `unique` leaf and share it across the lineage."""
    book = _static_book("lin-on-unique")
    leaf_id = book.bind(spell=_Leaf, existence=_UNIQUE, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_unique = root.meld(spell=leaf_id)
        root_parent = root.meld(spell=parent_id)
        assert root_parent.dep is root_unique
        lesser = root.create_lesser_conduit()
        try:
            lesser_parent = lesser.meld(spell=parent_id)
        finally:
            lesser.cleanup()
        assert lesser_parent is root_parent, "lineage holder is shared across the lineage"
        assert lesser_parent.dep is root_unique, "and keeps the shared unique dependency"
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# many -- never shared, fresh every resolution.
# =====================================================================
def test_many_is_fresh_on_every_meld() -> None:
    """`many` produces a new instance on every meld."""
    book = _static_book("many-fresh")
    sid = book.bind(spell=_Leaf, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        assert root.meld(spell=sid) is not root.meld(spell=sid)
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_many_dependency_is_fresh_per_holder() -> None:
    """Each fresh `many` holder gets its own fresh `many` dependency."""
    book = _static_book("many-dep")
    book.bind(spell=_Leaf, existence=_MANY, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        p1 = root.meld(spell=parent_id)
        p2 = root.meld(spell=parent_id)
        assert p1 is not p2
        assert p1.dep is not p2.dep, "many dependency must not be reused across holders"
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# unique_per_spell_space -- one instance per active spellspace scope.
# =====================================================================
def test_spellspace_shared_within_one_scope() -> None:
    """Within one spellspace, repeated melds resolve the same instance."""
    book = _dynamic_book("ss-share")
    sid = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as space:
            assert space.meld(spell=sid) is space.meld(spell=sid)
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_spellspace_distinct_across_scopes() -> None:
    """Two separate spellspace scopes resolve DIFFERENT instances."""
    book = _dynamic_book("ss-distinct")
    sid = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as s1:
            first = s1.meld(spell=sid)
        with root.enter_spellspace() as s2:
            second = s2.meld(spell=sid)
        assert first is not second, "each spellspace scope owns its own instance"
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_spellspace_dependency_within_scope() -> None:
    """A spellspace holder resolves the same-scope spellspace dependency."""
    book = _dynamic_book("ss-dep")
    leaf_id = book.bind(spell=_Leaf, existence=_SPELLSPACE, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_SPELLSPACE, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        with root.enter_spellspace() as space:
            leaf = space.meld(spell=leaf_id)
            parent = space.meld(spell=parent_id)
            assert parent.dep is leaf
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_spellspace_holder_on_lesser_resolves_root_lineage_dependency() -> None:
    """PROBE/BUG PIN: a spellspace holder entered on a lesser must still get the
    ROOT lineage instance as its dependency, not a lesser-local one."""
    book = _dynamic_book("ss-lin-dep")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_SPELLSPACE, permissions="create")
    root = book.conjure(dynamic=True, name="root")
    try:
        root_leaf = root.meld(spell=leaf_id)
        lesser = root.create_lesser_conduit()
        try:
            with lesser.enter_spellspace() as space:
                parent = space.meld(spell=parent_id)
                assert parent.dep is root_leaf, (
                    "spellspace holder on a lesser must resolve the ROOT lineage dep"
                )
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


# =====================================================================
# unique_per_conduit_cluster -- elected-leader store (PROBES).
# These exercise the cluster store-resolution path the existing suite never
# melds through. Setup mirrors test_conduit_integration_clusters_spellspace.
# =====================================================================
def test_cluster_meld_without_elected_leader_raises() -> None:
    """INVARIANT (discovered in RUN 3): a cluster spell melded with members but NO
    elected leader hard-errors at the meld door -- the leader store is inert.

    (SpellbookValidationError subclasses RuntimeError, so both internal error
    paths -- resolved_store() and the resolution-validity gate -- are covered.)
    """
    owner_book = Spellbook(configuration=_cluster_config())
    spell_id = owner_book.bind(spell=_Leaf, existence=_CLUSTER, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    try:
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.refresh_cluster_shares_for_conduit(owner)
        with pytest.raises(RuntimeError):
            owner.meld(spell=spell_id)
    finally:
        owner.permanent_cleanup()


def test_cluster_meld_with_elected_leader_is_stable_in_leader_store() -> None:
    """A cluster spell resolves into the elected leader's store and is stable there."""
    owner_book = Spellbook(configuration=_cluster_config())
    spell_id = owner_book.bind(spell=_Leaf, existence=_CLUSTER, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    try:
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.refresh_cluster_shares_for_conduit(owner)
        cloud.get_cluster("cluster-a").elect_leader(owner.id)

        first = owner.meld(spell=spell_id)
        second = owner.meld(spell=spell_id)
        assert first is second, "cluster spell is a singleton in the leader store"
        assert owner._cluster_creations.resolved_store() is owner._creations, (
            "the elected leader's cluster store is the leader conduit's own store"
        )
    finally:
        owner.permanent_cleanup()


def test_cluster_member_facade_resolves_to_leader_store() -> None:
    """A joining member's cluster facade resolves to the elected leader's store.

    Mirrors the proven component pattern: a borrower linked into a LIVE
    (already-elected) cluster gets its facade bound to the leader's store.
    """
    owner_book = Spellbook(configuration=_cluster_config())
    owner_book.bind(spell=_Leaf, existence=_CLUSTER, permissions="create")
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = Spellbook().conjure(dynamic=True, name="borrower")
    try:
        owner.link(borrower)
        cloud = owner._spellbook._aether.get_conduit_cloud(owner._aetheric_frame_name)
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.refresh_cluster_shares_for_conduit(owner)
        cloud.get_cluster("cluster-a").elect_leader(owner.id)
        cloud.add_conduit_to_cluster(borrower, "cluster-a")

        assert borrower._cluster_creations.is_active() is True
        assert borrower._cluster_creations.resolved_store() is owner._creations, (
            "a member resolves the cluster instance from the leader's store"
        )
    finally:
        borrower.cleanup()
        owner.cleanup()


# =====================================================================
# Concurrency -- threadsafety is the top runtime priority on 3.14t (no-GIL).
# =====================================================================
def test_concurrent_meld_unique_yields_single_instance() -> None:
    """Under parallel melds, `unique` must collapse to one frame instance."""
    book = _static_book("conc-unique")
    sid = book.bind(spell=_Leaf, existence=_UNIQUE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    results: List[Any] = []
    lock = threading.Lock()
    barrier = threading.Barrier(8)

    def _worker() -> None:
        barrier.wait()
        inst = root.meld(spell=sid)
        with lock:
            results.append(inst)

    try:
        threads = [threading.Thread(target=_worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(results) == 8
        assert len({id(x) for x in results}) == 1, (
            "unique must be a single instance even under concurrent resolution"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_concurrent_lineage_dependency_resolves_single_root_instance() -> None:
    """Parallel lessers each melding a holder must all resolve the one ROOT lineage dep."""
    book = _static_book("conc-lin")
    leaf_id = book.bind(spell=_Leaf, existence=_LINEAGE, permissions="create")
    parent_id = book.bind(spell=_Parent, existence=_MANY, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    root_leaf = root.meld(spell=leaf_id)
    deps: List[Any] = []
    lock = threading.Lock()
    barrier = threading.Barrier(8)

    def _worker() -> None:
        lesser = root.create_lesser_conduit()
        try:
            barrier.wait()
            holder = lesser.meld(spell=parent_id)
            with lock:
                deps.append(holder.dep)
        finally:
            lesser.cleanup()

    try:
        threads = [threading.Thread(target=_worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(deps) == 8
        assert all(d is root_leaf for d in deps), (
            "every concurrent lesser must resolve the same ROOT lineage instance"
        )
    finally:
        root.permanent_cleanup()
        book.cleanup()
