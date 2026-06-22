"""tests/integration/melder/conduit/test_conduit_integration_cluster_dependency.py

Validation: Not run.

`unique_per_conduit_cluster` exercised AS A DEPENDENCY through the real meld front
door, across the realistic topology:
    - multiple clusters,
    - TWO independent ROOT conduits per cluster (each its own spellbook in the
      shared frame; bind ids are content-addressed so the cluster shares them),
    - the elected leader melds AND the other cluster root melds,
    - the cluster spell is a dependency in more than one kind: a `many` parent and
      a `unique_per_conduit` parent.

The bug this targets: under CALLER routing, a dependency step resolves into the
store the PARENT's meld selected. On the elected leader that store IS the cluster
store (passes), but on the OTHER cluster root the parent meld selects that root's
own `_creations`, so the cluster-leaf step lands there -> a fresh per-root
instance instead of the cluster's shared one.

Direct cluster sharing across the two roots is asserted first as a precheck, so a
failure on the dependency assertion is unambiguous.
"""

from __future__ import annotations

from typing import Any, Callable, List, Tuple

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
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


class _ManyParentWithClusterDep:
    def __init__(self, dep: _ClusterLeaf) -> None:
        self.dep = dep


class _UpcParentWithClusterDep:
    def __init__(self, dep: _ClusterLeaf) -> None:
        self.dep = dep


def _cluster_config_for_frame(frame: str) -> SpellbookConfiguration:
    config = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return config


def _form_cluster_multi_root(
    name: str, root_count: int, bind_fn: Callable[[Spellbook], Any]
) -> Tuple[str, List[Spellbook], List[Any], Any, Any]:
    """
    Form a cluster with `root_count` independent ROOT conduits in one shared frame.

    Each root has its OWN spellbook and binds via `bind_fn`; because bind ids are
    content-addressed, every root's bindings share ids, so the cluster shares the
    cluster spell across them. The first root is linked-to by the rest, all are
    added to the cluster, and the first root is elected leader.

    Returns (frame, books, roots, cloud, bound_ids_from_root0).
    """
    frame = f"cdep-{name}"
    books: List[Spellbook] = []
    roots: List[Any] = []
    bound: Any = None
    for i in range(root_count):
        if i == 0:
            book = Spellbook(
                aetheric_frame=frame, configuration=_cluster_config_for_frame(frame)
            )
        else:
            book = Spellbook(aetheric_frame=frame)  # adopt the frame-owned config
        ids = bind_fn(book)
        if bound is None:
            bound = ids
        root = book.conjure(dynamic=True, name=f"{name}-root{i}")
        books.append(book)
        roots.append(root)

    for other in roots[1:]:
        roots[0].link(other)

    cloud = roots[0]._spellbook._aether.get_conduit_cloud(frame)
    cloud.create_cluster(name)
    for root in roots:
        cloud.add_conduit_to_cluster(root, name)
    for root in roots:
        cloud.refresh_cluster_shares_for_conduit(root)
    cloud.get_cluster(name).elect_leader(roots[0].id)
    return frame, books, roots, cloud, bound


def _cleanup(roots: List[Any]) -> None:
    for root in roots:
        root.cleanup()


def test_two_roots_share_cluster_instance_direct() -> None:
    """Precheck: two independent cluster roots resolve one shared instance."""
    _frame, _books, roots, _cloud, leaf_id = _form_cluster_multi_root(
        "share2", 2,
        lambda b: b.bind(spell=_ClusterThing, existence=_CLUSTER, permissions="create"),
    )
    try:
        instances = [root.meld(spell=leaf_id) for root in roots]
        assert instances[1] is instances[0], (
            "both cluster roots must resolve one shared cluster instance"
        )
    finally:
        _cleanup(roots)


def test_cluster_dependency_many_parent_on_every_root() -> None:
    """
    A `many` parent that depends on the cluster spell, melded on BOTH cluster
    roots (the elected leader and the other root). Every root's dependency must
    resolve the cluster's shared instance; the parents themselves are per-conduit.
    """
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterLeaf, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_ManyParentWithClusterDep, existence=_MANY, permissions="create"),
        )

    _frame, _books, roots, _cloud, (leaf_id, parent_id) = _form_cluster_multi_root(
        "depmany", 2, _bind
    )
    try:
        shared = roots[0].meld(spell=leaf_id)
        parents = []
        for index, root in enumerate(roots):
            # precheck: direct cluster meld on this root shares the instance
            assert root.meld(spell=leaf_id) is shared, (
                f"root{index}: direct cluster meld must resolve the shared instance"
            )
            parent = root.meld(spell=parent_id)
            parents.append(parent)
            # the bug: the parent's cluster dependency must also be the shared one
            assert parent.dep is shared, (
                f"root{index}: parent dependency must resolve the cluster's shared instance"
            )
        assert parents[1] is not parents[0], "`many` parents must be per-conduit"
    finally:
        _cleanup(roots)


def test_cluster_dependency_upc_parent_on_every_root() -> None:
    """Same as above but the dependent parent is unique_per_conduit, not many."""
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterLeaf, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_UpcParentWithClusterDep, existence=_UPC, permissions="create"),
        )

    _frame, _books, roots, _cloud, (leaf_id, parent_id) = _form_cluster_multi_root(
        "depupc", 2, _bind
    )
    try:
        shared = roots[0].meld(spell=leaf_id)
        for index, root in enumerate(roots):
            assert root.meld(spell=leaf_id) is shared, (
                f"root{index}: direct cluster meld must resolve the shared instance"
            )
            parent = root.meld(spell=parent_id)
            assert parent.dep is shared, (
                f"root{index}: unique_per_conduit parent dependency must resolve the shared instance"
            )
    finally:
        _cleanup(roots)


def test_multiple_clusters_two_roots_dependency_isolated() -> None:
    """
    Multiple clusters, each with two roots. Within a cluster every root's
    dependency resolves that cluster's shared instance; across clusters those
    instances are DISTINCT.
    """
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterLeaf, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_ManyParentWithClusterDep, existence=_MANY, permissions="create"),
        )

    per_cluster_shared: List[Any] = []
    handles: List[List[Any]] = []
    try:
        for name in ("mca", "mcb"):
            _frame, _books, roots, _cloud, (leaf_id, parent_id) = _form_cluster_multi_root(
                name, 2, _bind
            )
            handles.append(roots)
            shared = roots[0].meld(spell=leaf_id)
            for index, root in enumerate(roots):
                assert root.meld(spell=leaf_id) is shared, (
                    f"{name} root{index}: direct cluster meld must share"
                )
                assert root.meld(spell=parent_id).dep is shared, (
                    f"{name} root{index}: parent dependency must resolve the cluster's shared instance"
                )
            per_cluster_shared.append(shared)
        assert per_cluster_shared[0] is not per_cluster_shared[1], (
            "each cluster's dependency instance must be DISTINCT"
        )
    finally:
        for roots in handles:
            _cleanup(roots)
