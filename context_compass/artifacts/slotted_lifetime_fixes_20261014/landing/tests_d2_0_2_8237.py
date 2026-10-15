"""D2 tests (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, notch 0.2.8237): the cluster owns its team store.

Updates the tests that pinned the old representation (a facade bound to the leader conduit's `_creations` through a
one-argument `bind(store)`) and adds unit tests for the team store, the facade's leader id and the cluster's cleanup.
Run from a tree root: python <this file> [<tree root>]
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import edit_tool

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
FACADE_UNIT = str(ROOT / "tests/unit/melder/aether/conduit/test_cluster_creations.py")
CLUSTER_UNIT = str(ROOT / "tests/unit/melder/aether/conduit/test_conduit_cluster.py")
CLUSTER_COMPONENT = str(ROOT / "tests/component/melder/aether/conduit/test_conduit_component_cluster.py")

facade_edits = [
    (
        '''Unit tests for `melder.aether.conduit.creations.cluster_creations.ClusterCreations`.
Focus: the active-state contract and leader-store ISOLATION, exercised against a
fake store with no Aether / Conduit runtime. (The conduit-unit conftest resets
the singletons automatically; these tests do not need them.)
''',
        '''Unit tests for `melder.aether.conduit.creations.cluster_creations.ClusterCreations`.
Focus: the active-state contract, the elected leader's id and team-store
ISOLATION, exercised against a fake store with no Aether / Conduit runtime. (The
conduit-unit conftest resets the singletons automatically; these tests do not
need them.) Since 0.2.8237 the facade fronts the cluster's own team store and
`bind` takes the elected leader's id with it; these tests were updated from the
one-argument `bind(store)` of the leader-conduit store.
''',
    ),
    (
        '''    """Minimal stand-in for an elected leader's `Creations` store."""
''',
        '''    """Minimal stand-in for a cluster's team store (a `Creations`)."""
''',
    ),
    (
        '''def test_new_facade_is_disabled() -> None:
    assert ClusterCreations().is_active() is False
''',
        '''def test_new_facade_is_disabled() -> None:
    assert ClusterCreations().is_active() is False


def test_new_facade_names_no_leader() -> None:
    assert ClusterCreations().leader_conduit_id is None
''',
    ),
    (
        '''def test_bind_activates_and_delegates_through_to_store() -> None:
    store = _FakeStore("leader")
    facade = ClusterCreations()
    facade.bind(store)
    assert facade.is_active() is True
    assert facade.resolved_store() is store
''',
        '''def test_bind_activates_and_delegates_through_to_store() -> None:
    store = _FakeStore("team")
    facade = ClusterCreations()
    facade.bind(store, "leader-1")
    assert facade.is_active() is True
    assert facade.resolved_store() is store
    assert facade.leader_conduit_id == "leader-1"
''',
    ),
    (
        '''def test_unbind_deactivates_and_drops_store() -> None:
    facade = ClusterCreations()
    facade.bind(_FakeStore("leader"))
    facade.unbind()
    assert facade.is_active() is False
    with pytest.raises(RuntimeError):
        facade.resolved_store()
''',
        '''def test_unbind_deactivates_and_drops_store() -> None:
    facade = ClusterCreations()
    facade.bind(_FakeStore("team"), "leader-1")
    facade.unbind()
    assert facade.is_active() is False
    assert facade.leader_conduit_id is None
    with pytest.raises(RuntimeError):
        facade.resolved_store()
''',
    ),
    (
        '''def test_rebind_retargets_to_new_leader_store() -> None:
    facade = ClusterCreations()
    first = _FakeStore("first")
    second = _FakeStore("second")
    facade.bind(first)
    assert facade.resolved_store() is first
    facade.unbind()
    facade.bind(second)
    assert facade.resolved_store() is second
''',
        '''def test_rebind_retargets_to_new_store_and_leader() -> None:
    facade = ClusterCreations()
    first = _FakeStore("first")
    second = _FakeStore("second")
    facade.bind(first, "leader-1")
    assert facade.resolved_store() is first
    facade.unbind()
    facade.bind(second, "leader-2")
    assert facade.resolved_store() is second
    assert facade.leader_conduit_id == "leader-2"
''',
    ),
    (
        '''def test_two_facades_resolve_their_own_leader_store() -> None:
    """Facade-level isolation: each cluster's facade fronts its OWN leader store."""
    store_a = _FakeStore("a")
    store_b = _FakeStore("b")
    facade_a = ClusterCreations()
    facade_b = ClusterCreations()
    facade_a.bind(store_a)
    facade_b.bind(store_b)
''',
        '''def test_two_facades_resolve_their_own_team_store() -> None:
    """Facade-level isolation: each cluster's facade fronts its OWN team store."""
    store_a = _FakeStore("a")
    store_b = _FakeStore("b")
    facade_a = ClusterCreations()
    facade_b = ClusterCreations()
    facade_a.bind(store_a, "leader-a")
    facade_b.bind(store_b, "leader-b")
''',
    ),
    (
        '''def test_cleanup_is_idempotent_and_disables() -> None:
    facade = ClusterCreations()
    facade.bind(_FakeStore("leader"))
    facade.cleanup()
    facade.cleanup()  # idempotent: must not raise
    with pytest.raises(Exception):
        facade.is_active()  # check_cleaned trips after cleanup
''',
        '''def test_cleanup_is_idempotent_and_disables() -> None:
    facade = ClusterCreations()
    facade.bind(_FakeStore("team"), "leader-1")
    facade.cleanup()
    facade.cleanup()  # idempotent: must not raise
    with pytest.raises(Exception):
        facade.is_active()  # check_cleaned trips after cleanup
    with pytest.raises(RuntimeError):
        facade.leader_conduit_id  # check_cleaned trips after cleanup


def test_cleanup_never_cleans_the_store_it_fronts() -> None:
    """The cluster owns the team store; a member's facade cleanup only drops its reference."""
    store = _FakeStore("team")
    sentinel = object()
    facade = ClusterCreations()
    facade.bind(store, "leader-1")
    facade.add_creation("s", sentinel)
    facade.cleanup()
    assert store.get_creation("s") is sentinel
''',
    ),
]

cluster_edits = [
    (
        '''def test_bind_member_binds_joiner_facade_to_leader_store() -> None:
    """bind_member activates a joiner's facade and points it at the leader store."""
    leader = _FacadeConduit("leader")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader, joiner)
    cluster.master_conduit_id = leader._id

    cluster.bind_member(joiner)

    assert joiner._cluster_creations.is_active() is True
    assert joiner._cluster_creations.resolved_store() is leader._creations
''',
        '''def test_bind_member_binds_joiner_facade_to_the_team_store() -> None:
    """bind_member activates a joiner's facade on the cluster's team store under the current leader.

    Updated with 0.2.8237: the facade used to point at the leader conduit's own `_creations`; the store is now the
    cluster's, and the facade records the leader as the conduit with purge authority.
    """
    leader = _FacadeConduit("leader")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader, joiner)
    cluster.master_conduit_id = leader._id

    cluster.bind_member(joiner)

    assert joiner._cluster_creations.is_active() is True
    assert joiner._cluster_creations.resolved_store() is cluster._team_store
    assert joiner._cluster_creations.resolved_store() is not leader._creations
    assert joiner._cluster_creations.leader_conduit_id == leader._id
''',
    ),
    (
        '''def test_bind_member_binds_to_the_current_leader_store() -> None:
    """bind_member resolves master_conduit_id, binding to the current leader."""
    leader_a = _FacadeConduit("leader-a")
    leader_b = _FacadeConduit("leader-b")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader_a, leader_b, joiner)
    cluster.master_conduit_id = leader_b._id

    cluster.bind_member(joiner)

    assert joiner._cluster_creations.resolved_store() is leader_b._creations
    assert joiner._cluster_creations.resolved_store() is not leader_a._creations
''',
        '''def test_bind_member_records_the_current_leader() -> None:
    """bind_member reads master_conduit_id: the joiner's facade names the current leader.

    Updated with 0.2.8237: every leader serves the same team store, so the current leader shows in the facade's
    leader id rather than in which conduit's store it fronts.
    """
    leader_a = _FacadeConduit("leader-a")
    leader_b = _FacadeConduit("leader-b")
    joiner = _FacadeConduit("joiner")
    cluster = _make_facade_cluster(leader_a, leader_b, joiner)
    cluster.master_conduit_id = leader_b._id

    cluster.bind_member(joiner)

    assert joiner._cluster_creations.resolved_store() is cluster._team_store
    assert joiner._cluster_creations.leader_conduit_id == leader_b._id
''',
    ),
    (
        '''    cluster.master_conduit_id = leader._id
    leaver._cluster_creations.bind(leader._creations)

    cluster.unbind_member(leaver)

    assert leaver._cluster_creations.is_active() is False
    with pytest.raises(RuntimeError):
        leaver._cluster_creations.resolved_store()
''',
        '''    cluster.master_conduit_id = leader._id
    leaver._cluster_creations.bind(cluster._team_store, leader._id)

    cluster.unbind_member(leaver)

    assert leaver._cluster_creations.is_active() is False
    with pytest.raises(RuntimeError):
        leaver._cluster_creations.resolved_store()
''',
    ),
    (
        '''    cluster.master_conduit_id = leader._id
    leader._cluster_creations.bind(leader._creations)
    leaver._cluster_creations.bind(leader._creations)
''',
        '''    cluster.master_conduit_id = leader._id
    leader._cluster_creations.bind(cluster._team_store, leader._id)
    leaver._cluster_creations.bind(cluster._team_store, leader._id)
''',
    ),
    (
        '''    leaver._cluster_creations.bind(leaver._creations)
    cluster.master_conduit_id = None
''',
        '''    leaver._cluster_creations.bind(cluster._team_store, leaver._id)
    cluster.master_conduit_id = None
''',
    ),
    (
        '''def test_drop_member_raises_after_cleanup() -> None:
    """drop_member is guarded by check_cleaned after the cluster is cleaned."""
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    cluster.cleanup()

    with pytest.raises(RuntimeError):
        cluster.drop_member(leaver)
''',
        '''def test_drop_member_raises_after_cleanup() -> None:
    """drop_member is guarded by check_cleaned after the cluster is cleaned."""
    leaver = _FacadeConduit("leaver")
    cluster = _make_facade_cluster(leaver)
    cluster.cleanup()

    with pytest.raises(RuntimeError):
        cluster.drop_member(leaver)


# ----------------------------------------------------------------------
# The cluster's team store (0.2.8237)
# ----------------------------------------------------------------------
class _Closable:
    """A team-store instance whose `close` counts its calls and can be told to fail."""

    def __init__(self, fail: bool = False) -> None:
        """Start unclosed."""
        self.closes = 0
        self.fail = fail

    def close(self) -> None:
        """Count one disposal; raise when told to fail."""
        self.closes += 1
        if self.fail:
            raise RuntimeError("close failed")


def test_bind_elected_leader_binds_every_member_to_the_cluster_team_store() -> None:
    """Election binds every member facade to the store the cluster owns, under the leader's id."""
    leader = _FacadeConduit("leader")
    member = _FacadeConduit("member")
    cluster = _make_facade_cluster(leader, member)
    cluster.add_member(leader._id)
    cluster.add_member(member._id)

    cluster.bind_elected_leader(leader._id)

    for conduit in (leader, member):
        assert conduit._cluster_creations.resolved_store() is cluster._team_store
        assert conduit._cluster_creations.leader_conduit_id == leader._id
    assert cluster.master_conduit_id == leader._id


def test_a_later_election_serves_the_same_team_store() -> None:
    """Unelecting and electing another leader keeps the store, so its instances are served again, not rebuilt."""
    leader = _FacadeConduit("leader")
    member = _FacadeConduit("member")
    cluster = _make_facade_cluster(leader, member)
    cluster.add_member(leader._id)
    cluster.add_member(member._id)
    cluster.bind_elected_leader(leader._id)
    instance = object()
    member._cluster_creations.add_creation("spell-1", instance)

    cluster.unbind_elected_leader()
    cluster.bind_elected_leader(member._id)

    assert member._cluster_creations.get_creation("spell-1") is instance
    assert leader._cluster_creations.leader_conduit_id == member._id


def test_bind_elected_leader_refuses_an_unresolvable_leader() -> None:
    """Electing a conduit the frame registry does not hold raises and leaves the cluster inert."""
    member = _FacadeConduit("member")
    cluster = _make_facade_cluster(member)
    cluster.add_member(member._id)

    with pytest.raises(RuntimeError, match="could not be resolved"):
        cluster.bind_elected_leader("missing")

    assert cluster.master_conduit_id is None
    assert member._cluster_creations.is_active() is False


def test_cleanup_disposes_the_team_store_once() -> None:
    """Cleaning the cluster runs its instances' disposal methods once; a second cleanup does nothing."""
    cluster = _make_cluster("team")
    instance = _Closable()
    cluster._team_store.add_creation(
        "spell-1", instance, has_disposal_methods=True, disposal_methods=["close"]
    )

    cluster.cleanup()
    cluster.cleanup()

    assert instance.closes == 1
    assert cluster.cleaned is True


def test_cleanup_raises_team_store_disposal_failures_after_finishing() -> None:
    """A failing disposal method is raised as one ExceptionGroup after the cluster is fully cleaned."""
    cluster = _make_cluster("team")
    cluster.add_member("conduit-1")
    failing = _Closable(fail=True)
    healthy = _Closable()
    cluster._team_store.add_creation(
        "spell-1", failing, has_disposal_methods=True, disposal_methods=["close"]
    )
    cluster._team_store.add_creation(
        "spell-2", healthy, has_disposal_methods=True, disposal_methods=["close"]
    )
    registry = cluster._devops_information_registry

    with pytest.raises(ExceptionGroup, match="Conduit cluster cleaned with disposal failures."):
        cluster.cleanup()

    assert cluster.cleaned is True
    assert failing.closes == 1
    assert healthy.closes == 1
    assert registry.get_clusters_for_conduit("conduit-1") == ()
''',
    ),
]

component_edits = [
    (
        '''        cluster = cloud.get_cluster("cluster-a")
        assert borrower._cluster_creations.is_active() is True
        assert borrower._cluster_creations.resolved_store() is owner._creations
        assert cluster.master_conduit_id == owner.id
''',
        '''        cluster = cloud.get_cluster("cluster-a")
        assert borrower._cluster_creations.is_active() is True
        # 0.2.8237: the facade fronts the cluster's own team store (it was the
        # leader conduit's `_creations`) and records the elected leader.
        assert borrower._cluster_creations.resolved_store() is cluster._team_store
        assert borrower._cluster_creations.leader_conduit_id == owner.id
        assert cluster.master_conduit_id == owner.id
''',
    ),
]

print("facade unit", edit_tool.apply(FACADE_UNIT, facade_edits))
print("cluster unit", edit_tool.apply(CLUSTER_UNIT, cluster_edits))
print("cluster component", edit_tool.apply(CLUSTER_COMPONENT, component_edits))

# ----------------------------------------------------------------------------------------------------------------
# Integration tests that pinned the leader conduit's store as the cluster store (updated with 0.2.8237).
# ----------------------------------------------------------------------------------------------------------------
ALIGNMENT = str(ROOT / "tests/integration/melder/conduit/test_conduit_integration_scope_resolution_alignment.py")
MANY_CHILD = str(ROOT / "tests/integration/melder/conduit/test_conduit_integration_many_child_disposed_with_its_holder.py")

alignment_edits = [
    (
        '''def test_cluster_meld_with_elected_leader_is_stable_in_leader_store() -> None:
    """A cluster spell resolves into the elected leader's store and is stable there."""
''',
        '''def test_cluster_meld_with_elected_leader_is_stable_in_the_team_store() -> None:
    """A cluster spell resolves into the cluster's team store and is stable there.

    Updated with 0.2.8237: the store was the elected leader conduit's own `_creations`; it is now the cluster's.
    """
''',
    ),
    (
        '''        assert first is second, "cluster spell is a singleton in the leader store"
        assert owner._cluster_creations.resolved_store() is owner._creations, (
            "the elected leader's cluster store is the leader conduit's own store"
        )
''',
        '''        assert first is second, "cluster spell is a singleton in the team store"
        team_store = cloud.get_cluster("cluster-a")._team_store
        assert owner._cluster_creations.resolved_store() is team_store, (
            "the cluster store is the cluster's own team store"
        )
        assert owner._cluster_creations.resolved_store() is not owner._creations, (
            "the cluster store is not the leader conduit's own store"
        )
''',
    ),
    (
        '''def test_cluster_member_facade_resolves_to_leader_store() -> None:
    """A joining member's cluster facade resolves to the elected leader's store.

    Mirrors the proven component pattern: a borrower linked into a LIVE
    (already-elected) cluster gets its facade bound to the leader's store.
    """
''',
        '''def test_cluster_member_facade_resolves_to_the_team_store() -> None:
    """A joining member's cluster facade resolves to the cluster's team store.

    Mirrors the proven component pattern: a borrower linked into a LIVE
    (already-elected) cluster gets its facade bound to the team store, under the
    elected leader. Updated with 0.2.8237 (it was the leader conduit's store).
    """
''',
    ),
    (
        '''        assert borrower._cluster_creations.is_active() is True
        assert borrower._cluster_creations.resolved_store() is owner._creations, (
            "a member resolves the cluster instance from the leader's store"
        )
''',
        '''        assert borrower._cluster_creations.is_active() is True
        assert borrower._cluster_creations.resolved_store() is cloud.get_cluster("cluster-a")._team_store, (
            "a member resolves the cluster instance from the cluster's team store"
        )
        assert borrower._cluster_creations.leader_conduit_id == owner.id
''',
    ),
]

many_child_edits = [
    (
        '''        - a non-leader cluster member melds a `unique_per_conduit_cluster` holder: the holder lives in the elected
          leader's store, the child in the member's, so tearing the member down closes it the same way.
''',
        '''        - a non-leader cluster member melds a `unique_per_conduit_cluster` holder: the holder lives in the elected
          leader's store (since 0.2.8237 the cluster's own team store), the child in the member's, so tearing the
          member down closes it the same way.
''',
    ),
    (
        '''    A non-leader cluster member's teardown must not dispose the `many` child of the cluster's holder.

    Symptom (0.2.8234): the member melds the cluster holder first; the holder is published in the elected
    leader's store and its child recorded in the member's. Tearing the member down closes the child while the
    leader keeps returning the same holder. Corrected: the child is closed once, at the leader's teardown.
    """
''',
        '''    A non-leader cluster member's teardown must not dispose the `many` child of the cluster's holder.

    Symptom (0.2.8234): the member melds the cluster holder first; the holder is published in the elected
    leader's store and its child recorded in the member's. Tearing the member down closes the child while the
    leader keeps returning the same holder. Corrected (0.2.8235): the child is recorded with the holder's owner.
    Since 0.2.8237 that owner is the cluster (its team store, not the leader conduit's store), so neither the
    member's nor the leader's teardown disposes the child; deleting the cluster does, once.
    """
''',
    ),
    (
        '''        cloud.get_cluster("many_child").elect_leader(provider.id)
        first = member.meld(spell_id=holder_id)
        assert list(provider._creations._creations.get(child_id) or []) == [first.child], (
            "the elected leader must record the child of the cluster holder it stores"
        )
        assert first.child not in list(member._creations._creations.get(child_id) or []), (
            "the member root must not record the child"
        )
        member.cleanup()
        assert provider.meld(spell_id=holder_id) is first, "precondition: the holder outlives the member"
        assert first.child.closes == 0, (
            "the member's teardown disposed the many child of a cluster holder the leader still hands out"
        )
    finally:
        member.cleanup()
        provider.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once, with its holder"
''',
        '''        cloud.get_cluster("many_child").elect_leader(provider.id)
        first = member.meld(spell_id=holder_id)
        team_store = cloud.get_cluster("many_child")._team_store
        assert list(team_store._creations.get(child_id) or []) == [first.child], (
            "the cluster's team store must record the child of the cluster holder it stores"
        )
        assert first.child not in list(member._creations._creations.get(child_id) or []), (
            "the member root must not record the child"
        )
        assert first.child not in list(provider._creations._creations.get(child_id) or []), (
            "the leader conduit's own store must not record the child"
        )
        member.cleanup()
        assert provider.meld(spell_id=holder_id) is first, "precondition: the holder outlives the member"
        assert first.child.closes == 0, (
            "the member's teardown disposed the many child of a cluster holder the leader still hands out"
        )
        provider.cleanup()
        assert first.child.closes == 0, "the leader's teardown disposed a child the cluster owns"
        cloud.delete_cluster("many_child")
    finally:
        member.cleanup()
        provider.cleanup()
    assert first.child.closes == 1, "the child must be disposed exactly once, with the cluster that owns its holder"
''',
    ),
]

print("alignment", edit_tool.apply(ALIGNMENT, alignment_edits))
print("many child", edit_tool.apply(MANY_CHILD, many_child_edits))

# ----------------------------------------------------------------------------------------------------------------
# Component test that pinned the leader conduit's store as the cluster store (updated with 0.2.8237).
# ----------------------------------------------------------------------------------------------------------------
CREATIONS_COMPONENT = str(ROOT / "tests/component/melder/aether/conduit/test_conduit_component_creations.py")

creations_component_edits = [
    (
        '''        # unique_per_conduit_cluster requires dynamic mode and an elected leader.
        # Electing this conduit binds its own creation store as the cluster team
        # store, so the meld registers the instance into conduit._creations.
''',
        '''        # unique_per_conduit_cluster requires dynamic mode and an elected leader.
        # The instance registers into the cluster's own team store (0.2.8237;
        # until then electing this conduit bound its own creation store, and the
        # instance landed in conduit._creations).
''',
    ),
    (
        '''        cloud.get_cluster("cluster-a").elect_leader(conduit.id)

        creations = conduit._creations
        instance = conduit.meld(spell_id=spell_id)
        entry = creations._creations.get(spell_id)
        assert entry is not None
        assert entry is instance
''',
        '''        cloud.get_cluster("cluster-a").elect_leader(conduit.id)

        creations = cloud.get_cluster("cluster-a")._team_store
        instance = conduit.meld(spell_id=spell_id)
        entry = creations._creations.get(spell_id)
        assert entry is not None
        assert entry is instance
        assert conduit._creations._creations.get(spell_id) is None
''',
    ),
]

print("creations component", edit_tool.apply(CREATIONS_COMPONENT, creations_component_edits))
