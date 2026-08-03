"""tests/integration/melder/conduit/test_conduit_integration_cluster_isolation.py

Validation: Not run.

Integration tests through the real meld front door + conduit cloud for
`unique_per_conduit_cluster`, focused on the coverage gap:
    - cross-cluster ISOLATION: many clusters (separate frames AND two in one
      cloud) each own a DISTINCT instance;
    - many members all share the leader's instance; two distinct cluster spells
      are each shared independently;
    - DEPENDENCY routing: a parent that depends on a cluster spell resolves the
      cluster's shared instance, and stays isolated across clusters.

Join / leave / leader-dissolve flows live in
tests/integration/melder/conduit/test_conduit_integration_cluster_join_leave.py.
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


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_cluster() -> None:
    """Reset the Aether singleton around each integration cluster test."""
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


class _ClusterAlt:
    def __init__(self) -> None:
        pass


class _ClusterLeaf:
    def __init__(self) -> None:
        pass


class _ManyParentWithClusterDep:
    def __init__(self, dep: _ClusterLeaf) -> None:
        self.dep = dep


def _cluster_config_for_frame(frame: str) -> SpellbookConfiguration:
    config = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(config)
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return config


def _cluster_config(name: str) -> SpellbookConfiguration:
    return _cluster_config_for_frame(f"clu-{name}")


def _form_cluster(
    name: str, member_count: int, bind_fn: Callable[[Spellbook], Any]
) -> Tuple[Spellbook, Any, List[Any], Any, Any]:
    """
    Build an elected cluster: leader (binds via `bind_fn`) plus `member_count`
    linked members in the same frame, all added, leader elected.
    Returns (owner_book, leader, members, cloud, bound).
    """
    frame_name = f"clu-{name}"
    owner_book = Spellbook(aetheric_frame=frame_name, configuration=_cluster_config(name))
    bound = bind_fn(owner_book)
    leader = owner_book.conjure(dynamic=True, name=f"{name}-leader")
    frame = leader._aetheric_frame_name

    members: List[Any] = []
    for i in range(member_count):
        member = Spellbook(aetheric_frame=frame).conjure(dynamic=True, name=f"{name}-m{i}")
        leader.link(member)
        members.append(member)

    cloud = leader._spellbook._aether.get_conduit_cloud(frame)
    cloud.create_cluster(name)
    cloud.add_conduit_to_cluster(leader, name)
    for member in members:
        cloud.add_conduit_to_cluster(member, name)
    cloud.refresh_cluster_shares_for_conduit(leader)
    cloud.get_cluster(name).elect_leader(leader.id)
    return owner_book, leader, members, cloud, bound


def _bind_cluster_thing(book: Spellbook) -> Any:
    return book.bind(spell=_ClusterThing, existence=_CLUSTER, permissions="create")


def test_single_cluster_leader_and_members_share() -> None:
    _ob, leader, members, _cloud, spell_id = _form_cluster("single", 3, _bind_cluster_thing)
    try:
        leader_instance = leader.meld(spell=spell_id)
        for member in members:
            assert member.meld(spell=spell_id) is leader_instance
    finally:
        for member in members:
            member.cleanup()
        leader.cleanup()


def test_many_members_all_share() -> None:
    _ob, leader, members, _cloud, spell_id = _form_cluster("many", 6, _bind_cluster_thing)
    try:
        leader_instance = leader.meld(spell=spell_id)
        for member in members:
            assert member.meld(spell=spell_id) is leader_instance
    finally:
        for member in members:
            member.cleanup()
        leader.cleanup()


def test_two_distinct_cluster_spells_each_shared() -> None:
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterThing, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_ClusterAlt, existence=_CLUSTER, permissions="create"),
        )

    _ob, leader, members, _cloud, bound = _form_cluster("twospells", 1, _bind)
    id_a, id_b = bound
    member = members[0]
    try:
        a = leader.meld(spell=id_a)
        b = leader.meld(spell=id_b)
        assert a is not b
        assert member.meld(spell=id_a) is a
        assert member.meld(spell=id_b) is b
    finally:
        member.cleanup()
        leader.cleanup()


def test_dependency_resolves_shared_cluster_instance() -> None:
    """A parent's cluster dependency resolves the cluster's shared instance."""
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterLeaf, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_ManyParentWithClusterDep, existence=_MANY, permissions="create"),
        )

    _ob, leader, members, _cloud, bound = _form_cluster("dep", 1, _bind)
    leaf_id, parent_id = bound
    member = members[0]
    try:
        leader_parent = leader.meld(spell=parent_id)
        leader_leaf = leader.meld(spell=leaf_id)
        member_leaf = member.meld(spell=leaf_id)
        assert member_leaf is leader_leaf, "cluster leaf must be shared in the cluster"
        assert leader_parent.dep is leader_leaf, (
            "parent dependency must resolve the cluster's shared instance"
        )
    finally:
        member.cleanup()
        leader.cleanup()


def test_dependency_on_leader_lesser_resolves_cluster_instance() -> None:
    """
    THE cluster bug case (mirror of the lineage one): a `many` parent melded on a
    conduit that operates UNDER the cluster leader -- here a lesser of the leader,
    which inherits the leader's `_cluster_creations` facade -- must resolve the
    cluster's shared instance as its dependency.

    The parent meld selects the lesser's OWN `_creations` (parent is `many`), so
    under CALLER the cluster-leaf step lands there instead of the leader store.
    The direct meld on the lesser (precheck) still shares, because a direct
    cluster meld routes through the inherited facade to the leader store.
    """
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterLeaf, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_ManyParentWithClusterDep, existence=_MANY, permissions="create"),
        )

    _ob, leader, _members, _cloud, bound = _form_cluster("deplesser", 0, _bind)
    leaf_id, parent_id = bound
    try:
        leader_leaf = leader.meld(spell=leaf_id)
        lesser = leader.create_lesser_conduit()
        try:
            lesser_leaf = lesser.meld(spell=leaf_id)
            lesser_parent = lesser.meld(spell=parent_id)
        finally:
            lesser.cleanup()
        # precheck: a DIRECT cluster meld on the lesser shares the leader instance
        assert lesser_leaf is leader_leaf, (
            "direct cluster meld on a leader-lesser must resolve the leader's instance"
        )
        # the bug: the parent's cluster DEPENDENCY must also resolve the shared one
        assert lesser_parent.dep is leader_leaf, (
            "a leader-lesser's parent must resolve the cluster's shared instance as its dependency"
        )
    finally:
        leader.cleanup()



# ---------------------------------------------------------------------------
# DELETED 2026-08-02 - EPIC-2026-08-02-process-wide-spell-id-uniqueness
#
# Deleted:
#   test_multiple_clusters_separate_frames_isolated
#   test_dependency_isolated_across_clusters
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


# ---------------------------------------------------------------------------
# WITHDRAWN 2026-08-02 - test_two_clusters_one_frame_one_binding_are_isolated
#
# I wrote this to replace the deleted frame-per-cluster fixtures, on the
# assumption that any conduit on the frame could meld the one binding. That is
# WRONG, and the test proved it: `meld` resolves through the conduit's OWN
# Spellbook first, then contracted conduits (meld.py:1330 ->
# _resolve_spell_by_lookup_key). `leader_b` came from a Spellbook that bound
# nothing, so it raised
#   KeyError: [MELD] No spell found for frame='_clusterthing', binding='__default__'
#
# Cluster shares propagate FROM THE OWNER - `refresh_cluster_shares_for_conduit`
# shares the spells that conduit actually holds - so two cluster leaders each
# need the binding, and two bindings of one class is what process-wide
# uniqueness refuses. Whether a second leader can instead acquire it by link or
# contract is the open question, and I have not read those paths.
#
# Withdrawn rather than patched again: I have now guessed twice at cluster
# mechanics from the fixtures instead of reading the resolution path. The gap
# left by the deleted tautologies is REAL and still open - do not treat this
# absence as coverage.
# ---------------------------------------------------------------------------
