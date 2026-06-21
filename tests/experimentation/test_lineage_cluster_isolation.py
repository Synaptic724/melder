"""
Isolation / sharing / dependency SUITE for `unique_per_conduit_lineage` and
`unique_per_conduit_cluster` across MANY roots and MANY clusters.

This is the coverage gap: no integration tests spin up multiple roots each
spawning a lineage, or multiple clusters each electing a leader, and assert both
that scopes SHARE internally and stay ISOLATED from each other -- plus the
dependency case (a parent that DEPENDS on a lineage/cluster spell), which is where
the creation-store routing bug actually bites.

LINEAGE (root and its lessers share one spellbook)
  L1  single root: root + lessers share one instance, stored in the root creations
  L2  N=5 roots: each root owns a DISTINCT lineage instance (no cross-leak)
  L3  deep chain: root -> lesser -> lesser-of-lesser all share the ROOT instance
  L4  two distinct lineage spells in one root are each isolated + each shared
  L5  differential: in one root a lineage spell is shared across lessers but a
      `unique_per_conduit` spell is per-conduit (NOT shared)
  L6  re-meld on the same conduit is idempotent
  L7  DEPENDENCY (many parent): a lesser's parent resolves the ROOT lineage dep
  L8  DEPENDENCY (unique_per_conduit parent): same -- resolves the ROOT lineage dep
  L9  DEPENDENCY across N roots: each root's parents resolve their own root's dep

CLUSTER (members are separate spellbooks; the cluster shares the cluster spell)
  C1  single cluster: leader + members share the leader's instance
  C2  M=3 clusters (separate frames): each owns a DISTINCT instance
  C3  two clusters in ONE frame/cloud stay isolated
  C4  many members (6) all share the leader's instance
  C5  two distinct cluster spells in one cluster are each shared independently
  C6  leader re-meld is idempotent
  C7  member re-meld is idempotent
  C8  a member joining an already-elected cluster melds the leader's instance
  C9  a non-leader leaving keeps the leader's shared instance intact
  C10 DEPENDENCY: a parent's cluster dependency resolves the cluster's shared one
  C11 DEPENDENCY across M clusters: each cluster's parent-dep is its own instance

Grounded in the existing working tests:
  - lineage setup: tests/experimentation/test_lineage_root_scoped_instance.py
  - lineage-as-dependency: tests/experimentation/test_lineage_as_dependency.py
  - cluster setup: tests/integration/melder/conduit/test_conduit_integration_cluster_join_leave.py
  - lesser-of-lesser -> root: src/melder/aether/conduit/conduit.py::create_lesser_conduit

Run (3.14t), whole suite:
    .venv_new\\Scripts\\python.exe -m pytest tests/experimentation/test_lineage_cluster_isolation.py -q
Or standalone (no pytest, resets between tests itself):
    .venv_new\\Scripts\\python.exe tests/experimentation/test_lineage_cluster_isolation.py
"""

import sys
from pathlib import Path
from typing import Any, Callable, List, Tuple

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT / "src"), str(_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

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
_MANY = Existence.many
_UPC = Existence.unique_per_conduit


def _reset_runtime_singletons() -> None:
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def _reset_runtime() -> None:
    """Clean Aether + Nexus singletons around each test for isolation."""
    _reset_runtime_singletons()
    yield
    _reset_runtime_singletons()


# ---------------------------------------------------------------------------
# Spells under test
# ---------------------------------------------------------------------------
class _LineageThing:
    def __init__(self) -> None:
        pass


class _LineageAlt:
    def __init__(self) -> None:
        pass


class _ClusterThing:
    def __init__(self) -> None:
        pass


class _ClusterAlt:
    def __init__(self) -> None:
        pass


class _UpcThing:
    """unique_per_conduit -> a fresh instance per conduit (NOT lineage-shared)."""

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


class _ClusterLeaf:
    def __init__(self) -> None:
        pass


class _ManyParentWithClusterDep:
    def __init__(self, dep: _ClusterLeaf) -> None:
        self.dep = dep


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _lineage_book(tag: str) -> Spellbook:
    book = Spellbook(aetheric_frame=f"lin-{tag}")
    book.get_configuration().set_property("phase_scheduler_workers_per_spellbook", 1)
    book.configure_aether_frame(
        system_state=None,
        disposal=None,
        disposal_method_names=None,
        system_caching_enabled=False,
    )
    return book


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
    Build an elected cluster: leader (owner_book binds via `bind_fn`) plus
    `member_count` linked members in the same frame, all added, leader elected.
    Returns (owner_book, leader, members, cloud, bound).
    """
    owner_book = Spellbook(configuration=_cluster_config(name))
    bound = bind_fn(owner_book)
    leader = owner_book.conjure(dynamic=True, name=f"{name}-leader")
    frame = leader._aetheric_frame_name

    members: List[Any] = []
    for i in range(member_count):
        member = Spellbook(aetheric_frame=frame).conjure(
            dynamic=True, name=f"{name}-m{i}"
        )
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


# ===========================================================================
# LINEAGE
# ===========================================================================
def test_L1_single_root_shares_across_lessers() -> None:
    book = _lineage_book("single")
    spell_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_instance = root.meld(spell=spell_id)
        lesser_instances = []
        for _ in range(3):
            lesser = root.create_lesser_conduit()
            try:
                lesser_instances.append(lesser.meld(spell=spell_id))
            finally:
                lesser.cleanup()
        assert root._creations.get_creation(spell_id) is root_instance
        for instance in lesser_instances:
            assert instance is root_instance, "root and lessers must share one instance"
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_L2_multiple_roots_are_isolated() -> None:
    n_roots = 5
    keepalive: List[Tuple[Spellbook, Any]] = []
    shared: List[Any] = []
    try:
        for i in range(n_roots):
            book = _lineage_book(f"iso-{i}")
            spell_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
            root = book.conjure(name=f"root-{i}", dynamic=False)
            keepalive.append((book, root))
            root_instance = root.meld(spell=spell_id)
            for _ in range((i % 3) + 1):
                lesser = root.create_lesser_conduit()
                try:
                    assert lesser.meld(spell=spell_id) is root_instance
                finally:
                    lesser.cleanup()
            shared.append(root_instance)
        assert len({id(x) for x in shared}) == n_roots, (
            "each root must own a DISTINCT lineage instance"
        )
    finally:
        for book, root in keepalive:
            root.permanent_cleanup()
            book.cleanup()


def test_L3_deep_chain_shares_root_instance() -> None:
    """root -> lesser -> lesser-of-lesser must all resolve the ROOT instance."""
    book = _lineage_book("deep")
    spell_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_instance = root.meld(spell=spell_id)
        lesser = root.create_lesser_conduit()
        deep = lesser.create_lesser_conduit()
        try:
            assert lesser.meld(spell=spell_id) is root_instance
            assert deep.meld(spell=spell_id) is root_instance, (
                "lesser-of-a-lesser must still resolve the ROOT lineage instance"
            )
        finally:
            deep.cleanup()
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_L4_two_distinct_spells_each_isolated() -> None:
    book = _lineage_book("two")
    id_a = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    id_b = book.bind(spell=_LineageAlt, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        a = root.meld(spell=id_a)
        b = root.meld(spell=id_b)
        assert a is not b, "two distinct lineage spells must be distinct instances"
        lesser = root.create_lesser_conduit()
        try:
            assert lesser.meld(spell=id_a) is a
            assert lesser.meld(spell=id_b) is b
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_L5_lineage_shared_but_unique_per_conduit_is_not() -> None:
    """Differential: lineage shares across lessers; unique_per_conduit does not."""
    book = _lineage_book("diff")
    lin_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    upc_id = book.bind(spell=_UpcThing, existence=_UPC, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        root_lin = root.meld(spell=lin_id)
        root_upc = root.meld(spell=upc_id)
        lesser = root.create_lesser_conduit()
        try:
            assert lesser.meld(spell=lin_id) is root_lin, "lineage must be shared"
            assert lesser.meld(spell=upc_id) is not root_upc, (
                "unique_per_conduit must be per-conduit, not lineage-shared"
            )
        finally:
            lesser.cleanup()
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_L6_remeld_is_idempotent() -> None:
    book = _lineage_book("idem")
    spell_id = book.bind(spell=_LineageThing, existence=_LINEAGE, permissions="create")
    root = book.conjure(name="root", dynamic=False)
    try:
        assert root.meld(spell=spell_id) is root.meld(spell=spell_id)
    finally:
        root.permanent_cleanup()
        book.cleanup()


def test_L7_dependency_many_parent_resolves_root_instance() -> None:
    """THE bug case: a `many` parent on a lesser must get the ROOT lineage dep."""
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


def test_L8_dependency_upc_parent_resolves_root_instance() -> None:
    """Same as L7 but the parent is unique_per_conduit instead of many."""
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


def test_L9_dependency_isolated_across_roots() -> None:
    n_roots = 3
    keepalive: List[Tuple[Spellbook, Any]] = []
    deps: List[Any] = []
    try:
        for i in range(n_roots):
            book = _lineage_book(f"dep-iso-{i}")
            leaf_id = book.bind(spell=_LineageLeaf, existence=_LINEAGE, permissions="create")
            parent_id = book.bind(spell=_ManyParentWithLineageDep, existence=_MANY, permissions="create")
            root = book.conjure(name=f"root-{i}", dynamic=False)
            keepalive.append((book, root))
            root_leaf = root.meld(spell=leaf_id)
            lesser = root.create_lesser_conduit()
            try:
                lesser_parent = lesser.meld(spell=parent_id)
            finally:
                lesser.cleanup()
            assert lesser_parent.dep is root_leaf
            deps.append(root_leaf)
        assert len({id(x) for x in deps}) == n_roots, (
            "each root's lineage dependency must be DISTINCT"
        )
    finally:
        for book, root in keepalive:
            root.permanent_cleanup()
            book.cleanup()


# ===========================================================================
# CLUSTER
# ===========================================================================
def test_C1_single_leader_shares_across_members() -> None:
    owner_book, leader, members, _cloud, spell_id = _form_cluster(
        "single", 3, _bind_cluster_thing
    )
    try:
        leader_instance = leader.meld(spell=spell_id)
        for member in members:
            assert member.meld(spell=spell_id) is leader_instance
    finally:
        for member in members:
            member.cleanup()
        leader.cleanup()


def test_C2_multiple_clusters_separate_frames_isolated() -> None:
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


def test_C3_two_clusters_same_frame_isolated() -> None:
    """Two named clusters in ONE cloud/frame must not share an instance."""
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


def test_C4_many_members_all_share() -> None:
    owner_book, leader, members, _cloud, spell_id = _form_cluster(
        "many", 6, _bind_cluster_thing
    )
    try:
        leader_instance = leader.meld(spell=spell_id)
        for member in members:
            assert member.meld(spell=spell_id) is leader_instance
    finally:
        for member in members:
            member.cleanup()
        leader.cleanup()


def test_C5_two_distinct_spells_each_shared() -> None:
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterThing, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_ClusterAlt, existence=_CLUSTER, permissions="create"),
        )

    owner_book, leader, members, _cloud, bound = _form_cluster("twospells", 1, _bind)
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


def test_C6_leader_remeld_is_idempotent() -> None:
    owner_book, leader, members, _cloud, spell_id = _form_cluster(
        "idem-l", 1, _bind_cluster_thing
    )
    try:
        assert leader.meld(spell=spell_id) is leader.meld(spell=spell_id)
    finally:
        for member in members:
            member.cleanup()
        leader.cleanup()


def test_C7_member_remeld_is_idempotent() -> None:
    owner_book, leader, members, _cloud, spell_id = _form_cluster(
        "idem-m", 1, _bind_cluster_thing
    )
    member = members[0]
    try:
        leader.meld(spell=spell_id)
        assert member.meld(spell=spell_id) is member.meld(spell=spell_id)
    finally:
        member.cleanup()
        leader.cleanup()


def test_C8_member_joins_live_cluster_shares_leader_instance() -> None:
    config = _cluster_config("live")
    owner_book = Spellbook(configuration=config)
    spell_id = _bind_cluster_thing(owner_book)
    leader = owner_book.conjure(dynamic=True, name="live-leader")
    frame = leader._aetheric_frame_name
    latecomer = Spellbook(aetheric_frame=frame).conjure(dynamic=True, name="latecomer")
    try:
        leader.link(latecomer)
        cloud = leader._spellbook._aether.get_conduit_cloud(frame)
        cloud.create_cluster("live")
        cloud.add_conduit_to_cluster(leader, "live")
        cloud.refresh_cluster_shares_for_conduit(leader)
        cloud.get_cluster("live").elect_leader(leader.id)
        leader_instance = leader.meld(spell=spell_id)
        cloud.add_conduit_to_cluster(latecomer, "live")
        cloud.refresh_cluster_shares_for_conduit(leader)
        assert latecomer.meld(spell=spell_id) is leader_instance
    finally:
        latecomer.cleanup()
        leader.cleanup()


def test_C9_non_leader_leave_keeps_shared_instance() -> None:
    owner_book, leader, members, cloud, spell_id = _form_cluster(
        "leave", 1, _bind_cluster_thing
    )
    member = members[0]
    try:
        leader_instance = leader.meld(spell=spell_id)
        assert member.meld(spell=spell_id) is leader_instance
        cloud.remove_conduit_from_cluster(member, "leave")
        assert leader.meld(spell=spell_id) is leader_instance, "leader instance intact"
        assert member._cluster_creations.is_active() is False, "leaver facade dropped"
    finally:
        member.cleanup()
        leader.cleanup()


def test_C10_dependency_resolves_shared_instance() -> None:
    """A parent's cluster dependency resolves the cluster's shared instance."""
    def _bind(book: Spellbook) -> Tuple[Any, Any]:
        return (
            book.bind(spell=_ClusterLeaf, existence=_CLUSTER, permissions="create"),
            book.bind(spell=_ManyParentWithClusterDep, existence=_MANY, permissions="create"),
        )

    owner_book, leader, members, _cloud, bound = _form_cluster("dep", 1, _bind)
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


def test_C11_dependency_isolated_across_clusters() -> None:
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


if __name__ == "__main__":
    _suite = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    failures = 0
    for test in _suite:
        _reset_runtime_singletons()
        try:
            test()
        except Exception as exc:  # noqa: BLE001 - standalone runner reporting
            failures += 1
            print(f"FAIL {test.__name__}: {type(exc).__name__}: {exc}")
        else:
            print(f"PASS {test.__name__}")
        finally:
            _reset_runtime_singletons()
    print(f"\n{len(_suite) - failures}/{len(_suite)} passed")
    sys.exit(1 if failures else 0)
