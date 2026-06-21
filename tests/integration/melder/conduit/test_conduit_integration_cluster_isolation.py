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
    owner_book = Spellbook(configuration=_cluster_config(name))
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


def test_multiple_clusters_separate_frames_isolated() -> None:
    handles: List[Tuple[Any, List[Any]]] = []
    shared: List[Any] = []
    try:
        for name in ("alpha", "beta", "gamma"):
            _ob, leader, members, _cloud, spell_id = _form_cluster(name, 2, _bind_cluster_thing)
            handles.append((leader, members))
            leader_instance = leader.meld(spell=spell_id)
            for member in members:
                assert member.meld(spell=spell_id) is leader_instance
            shared.append(leader_instance)
        assert len({id(x) for x in shared}) == len(shared), (
            "each cluster must own a DISTINCT instance"
        )
    finally:
        for leader, members in handles:
            for member in members:
                member.cleanup()
            leader.cleanup()


def test_two_clusters_in_one_cloud_isolated() -> None:
    """Two named clusters in ONE frame/cloud must not share an instance."""
    frame = "clu-shared-frame"
    book_a = Spellbook(configuration=_cluster_config_for_frame(frame))
    sid_a = _bind_cluster_thing(book_a)
    leader_a = book_a.conjure(dynamic=True, name="a-leader")
    book_b = Spellbook(configuration=_cluster_config_for_frame(frame))
    sid_b = _bind_cluster_thing(book_b)
    leader_b = book_b.conjure(dynamic=True, name="b-leader")
    try:
        cloud = leader_a._spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("ca")
        cloud.create_cluster("cb")
        cloud.add_conduit_to_cluster(leader_a, "ca")
        cloud.add_conduit_to_cluster(leader_b, "cb")
        cloud.refresh_cluster_shares_for_conduit(leader_a)
        cloud.refresh_cluster_shares_for_conduit(leader_b)
        cloud.get_cluster("ca").elect_leader(leader_a.id)
        cloud.get_cluster("cb").elect_leader(leader_b.id)
        inst_a = leader_a.meld(spell=sid_a)
        inst_b = leader_b.meld(spell=sid_b)
        assert inst_a is not inst_b, "two clusters in one cloud must be isolated"
    finally:
        leader_a.cleanup()
        leader_b.cleanup()


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


def test_dependency_isolated_across_clusters() -> None:
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterLeaf, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_ManyParentWithClusterDep, existence=_MANY, permissions="create"),
        )

    handles: List[Any] = []
    deps: List[Any] = []
    try:
        for name in ("dx", "dy"):
            _ob, leader, members, _cloud, bound = _form_cluster(name, 1, _bind)
            handles.append((leader, members))
            leaf_id, parent_id = bound
            leader_parent = leader.meld(spell=parent_id)
            leader_leaf = leader.meld(spell=leaf_id)
            assert leader_parent.dep is leader_leaf
            deps.append(leader_leaf)
        assert deps[0] is not deps[1], "each cluster's dependency must be DISTINCT"
    finally:
        for leader, members in handles:
            for member in members:
                member.cleanup()
            leader.cleanup()
