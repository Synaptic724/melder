"""tests/integration/melder/conduit/test_conduit_integration_cluster_dependency.py

`unique_per_conduit_cluster` exercised AS A DEPENDENCY through the real meld
front door.

Cluster formation model (see src/melder/aether/conduit/conduit_cluster.py and
the ContractProviderPresenceStrategy):
  - The cluster leaf (`unique_per_conduit_cluster`) is bound ONCE, on a PROVIDER
    root. spell_ids are frame-unique for EVERY existence, so re-binding the same
    leaf in a sibling book of the same frame is a correct collision -- the
    cluster does not re-bind, it SHARES.
  - On cluster join the cluster auto-shares the provider's shareable roots
    (filtered to `unique_per_conduit_cluster` by `_get_shareable_spells`) into
    every peer as CONTRACTS, and leader election points every member's
    `_cluster_creations` at the leader's store -- so every member resolves the
    one shared instance.
  - A dependent parent (`many` / `unique_per_conduit`) reaches the leaf through
    a late-bound `SpellContract` socket (dynamic mode), NOT plain type-hint DI.
    `ContractProviderPresenceStrategy` satisfies a contract socket only from a
    CONTRACTED (cross-conduit) provider -- never a local binding -- so the
    parents live on CONSUMER roots that BORROW the leaf, not on the provider
    root that owns it. Each consumer binds its OWN distinct parent (`many` /
    `unique_per_conduit` parents are not cluster-shareable, and re-binding the
    same class collides).

Direct cluster sharing across the roots is asserted first as a precheck, so a
failure on the dependency assertion is unambiguous.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)

_CLUSTER = Existence.unique_per_conduit_cluster
_MANY = Existence.many
_UPC = Existence.unique_per_conduit


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_cluster_dependency() -> None:
    """Reset the Aether singleton around each cluster-dependency test."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


class _ClusterThing:
    def __init__(self) -> None:
        pass


class _ClusterLeaf:
    def __init__(self) -> None:
        pass


# Consumer parents reach the cluster leaf through a LATE-BOUND `SpellContract`
# socket (dynamic mode), satisfied by the cluster-shared (contracted) leaf at
# runtime -- never a local binding (ContractProviderPresenceStrategy only
# considers contracted providers). Each consumer root needs its OWN parent
# class: `many` / `unique_per_conduit` parents are not cluster-shareable, and
# re-binding the same class into a sibling book of the same frame is a (correct)
# spell_id collision. Across DISTINCT frames (separate clusters) the same class
# is reused safely, since collisions are frame-scoped.
class _ManyParentClusterDepA:
    def __init__(self, dep=SpellContract(spell=_ClusterLeaf)) -> None:
        self.dep = dep


class _ManyParentClusterDepB:
    def __init__(self, dep=SpellContract(spell=_ClusterLeaf)) -> None:
        self.dep = dep


class _UpcParentClusterDepA:
    def __init__(self, dep=SpellContract(spell=_ClusterLeaf)) -> None:
        self.dep = dep


class _UpcParentClusterDepB:
    def __init__(self, dep=SpellContract(spell=_ClusterLeaf)) -> None:
        self.dep = dep


def _cluster_config_for_frame(frame: str) -> SpellbookConfiguration:
    config = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return config


def _form_cluster_multi_root(
    name: str,
    *,
    leaf_cls: Any,
    parents: Optional[List[Tuple[Any, Existence]]] = None,
    consumer_count: int = 1,
) -> Tuple[str, List[Spellbook], List[Any], Any, Any, List[Any]]:
    """
    Form a cluster in one shared frame.

    `roots[0]` is the PROVIDER root: it owns the cluster leaf, is elected leader,
    and hosts NO parent. `roots[1:]` are CONSUMER roots: each borrows the leaf
    via cluster join and, when `parents` is given, binds its OWN
    `(class, existence)` parent whose dependency on the leaf is a late-bound
    `SpellContract`. `parent_ids[i]` corresponds to `roots[i + 1]`.

    Returns (frame, books, roots, cloud, leaf_id, parent_ids).
    """
    if parents is not None:
        consumer_count = len(parents)
    frame = f"cdep-{name}"
    books: List[Spellbook] = []
    roots: List[Any] = []
    parent_ids: List[Any] = []

    # Provider / leader root owns the cluster leaf exactly once.
    provider_book = Spellbook(
        aetheric_frame=frame, configuration=_cluster_config_for_frame(frame)
    )
    leaf_id = provider_book.bind(
        spell=leaf_cls, existence=_CLUSTER, permissions="create"
    )
    provider = provider_book.conjure(dynamic=True, name=f"{name}-provider")
    books.append(provider_book)
    roots.append(provider)

    # Consumer roots borrow the leaf via the cluster and host the parents.
    for i in range(consumer_count):
        book = Spellbook(aetheric_frame=frame)  # adopt the frame-owned config
        if parents is not None:
            parent_cls, parent_existence = parents[i]
            parent_ids.append(
                book.bind(
                    spell=parent_cls,
                    existence=parent_existence,
                    permissions="create",
                )
            )
        consumer = book.conjure(dynamic=True, name=f"{name}-consumer{i}")
        books.append(book)
        roots.append(consumer)

    for consumer in roots[1:]:
        provider.link(consumer)

    cloud = provider._spellbook._aether.get_conduit_cloud(frame)
    cloud.create_cluster(name)
    for root in roots:
        cloud.add_conduit_to_cluster(root, name)
    for root in roots:
        cloud.refresh_cluster_shares_for_conduit(root)
    cloud.get_cluster(name).elect_leader(provider.id)
    return frame, books, roots, cloud, leaf_id, parent_ids


def _cleanup(roots: List[Any]) -> None:
    for root in roots:
        root.cleanup()


def test_two_roots_share_cluster_instance_direct() -> None:
    """Precheck: provider + borrower resolve one shared cluster instance."""
    _frame, _books, roots, _cloud, leaf_id, _parents = _form_cluster_multi_root(
        "share2", leaf_cls=_ClusterThing,
    )
    try:
        instances = [root.meld(spell_id=leaf_id) for root in roots]
        assert instances[1] is instances[0], (
            "both cluster roots must resolve one shared cluster instance"
        )
    finally:
        _cleanup(roots)


def test_cluster_dependency_many_parent_on_every_root() -> None:
    """
    A `many` parent that depends on the cluster spell, melded on every CONSUMER
    root. Every consumer's dependency must resolve the cluster's shared
    instance; the parents themselves are per-conduit.
    """
    _frame, _books, roots, _cloud, leaf_id, parent_ids = _form_cluster_multi_root(
        "depmany",
        leaf_cls=_ClusterLeaf,
        parents=[(_ManyParentClusterDepA, _MANY), (_ManyParentClusterDepB, _MANY)],
    )
    try:
        shared = roots[0].meld(spell_id=leaf_id)
        # precheck: every cluster member resolves the one shared leaf instance
        for index, root in enumerate(roots):
            assert root.meld(spell_id=leaf_id) is shared, (
                f"root{index}: direct cluster meld must resolve the shared instance"
            )
        # the SpellContract parents live on the consumer roots (roots[1:])
        parents = [
            roots[i + 1].meld(spell_id=parent_ids[i]) for i in range(len(parent_ids))
        ]
        for index, parent in enumerate(parents):
            assert parent.dep is shared, (
                f"consumer{index}: parent dependency must resolve the cluster's shared instance"
            )
        assert parents[1] is not parents[0], "`many` parents must be per-conduit"
    finally:
        _cleanup(roots)


def test_cluster_dependency_upc_parent_on_every_root() -> None:
    """Same as above but the dependent parent is unique_per_conduit, not many."""
    _frame, _books, roots, _cloud, leaf_id, parent_ids = _form_cluster_multi_root(
        "depupc",
        leaf_cls=_ClusterLeaf,
        parents=[(_UpcParentClusterDepA, _UPC), (_UpcParentClusterDepB, _UPC)],
    )
    try:
        shared = roots[0].meld(spell_id=leaf_id)
        for index, root in enumerate(roots):
            assert root.meld(spell_id=leaf_id) is shared, (
                f"root{index}: direct cluster meld must resolve the shared instance"
            )
        for i in range(len(parent_ids)):
            parent = roots[i + 1].meld(spell_id=parent_ids[i])
            assert parent.dep is shared, (
                f"consumer{i}: unique_per_conduit parent dependency must resolve the shared instance"
            )
    finally:
        _cleanup(roots)



# ---------------------------------------------------------------------------
# DELETED 2026-08-02 - EPIC-2026-08-02-process-wide-spell-id-uniqueness
#
# Deleted:
#   test_multiple_clusters_two_roots_dependency_isolated
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
# passed by construction and would have kept passing with unique_per_conduit_cluster
# resolution entirely removed. There is no coverage here to preserve.
#
# REAL coverage needs several scopes sharing ONE binding inside ONE frame. That
# shape IS reachable and always was - `_form_cluster` already builds it: one
# book binds, further Spellbooks on the SAME frame conjure WITHOUT binding, and
# clusters are created on the CONDUIT CLOUD, not the frame. Two clusters off one
# binding is `create_cluster("a")` + `create_cluster("b")` on the same cloud.
# Only that shape actually exercises unique_per_conduit_cluster; the deleted
# tests never did.
# ---------------------------------------------------------------------------
