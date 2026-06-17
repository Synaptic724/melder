from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService

from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
)


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_conduit_cloud() -> None:
    """
    Purpose:
        Ensure ConduitCloud component tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_configuration(
        *,
        aether_frame: str,
        dynamic: bool,
        workers: int = 1,
) -> SpellbookConfiguration:
    """
    Purpose:
        Build a configuration for ConduitCloud component tests.
    Contract:
        - system_state is set to automatic or dynamic defaults.
        - phase_scheduler_workers_per_spellbook is configured.
    Args:
        aether_frame: Target frame name.
        dynamic: Whether to enable dynamic defaults.
        workers: Scheduler worker count per spellbook.
    Returns:
        SpellbookConfiguration: Configured instance.
    """
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def _get_local_spell_by_version_id(
        spellbook: Spellbook,
        spell_id: str,
) -> Optional[object]:
    """
    Purpose:
        Resolve one locally owned spell by its current version id.
    Contract:
        - Returns the first local spell whose SpellIndex.selected_spell_id matches the
          supplied version id.
        - Returns None when no local spell matches.
    Args:
        spellbook: Spellbook whose local spell map should be searched.
        spell_id: Current version id to resolve.
    Returns:
        Optional[object]: Matching local spell object, or None when absent.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.selected_spell_id == spell_id:
            return spell
    return None


def _make_spellbook(
        *,
        frame_name: str,
        dynamic: bool,
) -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for ConduitCloud component tests.
    Contract:
        - Uses the supplied frame name and dynamic posture.
    Args:
        frame_name: Target frame name.
        dynamic: Whether the frame should be dynamic.
    Returns:
        Spellbook: Configured spellbook.
    """
    configuration = _make_configuration(
        aether_frame=frame_name,
        dynamic=dynamic,
    )
    return Spellbook(aetheric_frame=frame_name, configuration=configuration)


def test_component_conduit_cloud_create_cluster_registers_identity_and_lookup() -> None:
    """
    Purpose:
        Validate create_cluster registers a live cluster identity and cloud lookup.
    Contract:
        - The new cluster is discoverable through the cloud surface.
        - The dev-ops registry exposes the cluster identity by id.
    Returns:
        None.
    Raises:
        AssertionError: If cluster creation does not mirror runtime state.
    """
    frame_name = "component-cloud-create"
    spellbook = _make_spellbook(frame_name=frame_name, dynamic=True)
    conduit = spellbook.conjure(dynamic=True, name="root")
    registry = conduit._aetheric_frame.devops_information_registry
    cloud = conduit.get_conduit_cloud()
    try:
        cloud.create_cluster("cluster-a")
        cluster = cloud.get_cluster("cluster-a")
        assert cloud.list_cluster_names() == ("cluster-a",)
        assert registry.get_identity(
            owner_kind="conduit_cluster",
            owner_id=cluster.id,
        ) is not None
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_component_conduit_cloud_create_cluster_requires_dynamic_mode() -> None:
    """
    Purpose:
        Validate cluster creation is blocked outside dynamic mode.
    Contract:
        - Automatic posture rejects create_cluster.
    Returns:
        None.
    Raises:
        AssertionError: If automatic posture allows cluster creation.
    """
    frame_name = "component-cloud-automatic"
    spellbook = _make_spellbook(frame_name=frame_name, dynamic=False)
    conduit = spellbook.conjure(name="root")
    cloud = conduit.get_conduit_cloud()
    try:
        with pytest.raises(RuntimeError, match="dynamic mode"):
            cloud.create_cluster("cluster-a")
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_component_conduit_cloud_add_conduit_to_cluster_tracks_membership_in_registry() -> None:
    """
    Purpose:
        Validate add_conduit_to_cluster mirrors membership through cloud and registry state.
    Contract:
        - Cloud membership lookup reports the cluster by name.
        - The dev-ops registry reports the cluster id for each conduit.
    Returns:
        None.
    Raises:
        AssertionError: If membership mirroring is incomplete.
    """
    frame_name = "component-cloud-membership"
    owner_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    borrower_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    cloud = owner.get_conduit_cloud()
    registry = owner._aetheric_frame.devops_information_registry
    try:
        cloud.create_cluster("cluster-a")
        cluster = cloud.get_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")

        assert cloud.get_clusters_for_conduit(owner.id) == ["cluster-a"]
        assert cloud.get_clusters_for_conduit(borrower.id) == ["cluster-a"]
        assert registry.get_clusters_for_conduit(owner.id) == (cluster.id,)
        assert registry.get_clusters_for_conduit(borrower.id) == (cluster.id,)
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_cloud_add_conduit_to_cluster_shares_existing_cluster_spell() -> None:
    """
    Purpose:
        Validate joining a linked borrower shares existing cluster-scoped spells.
    Contract:
        - A pre-bound unique_per_conduit_cluster spell becomes visible to the borrower.
        - No live cluster-link session remains after the join completes.
    Returns:
        None.
    Raises:
        AssertionError: If join-time sharing does not occur cleanly.
    """
    frame_name = "component-cloud-share-existing"
    owner_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    borrower_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    owner_spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    cloud = owner.get_conduit_cloud()
    registry = owner._aetheric_frame.devops_information_registry
    try:
        assert owner.link(borrower) is True
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")

        assert borrower.find_contracted_spell(owner_spell_id) is not None
        assert registry.list_live_transactions_for_type("cluster_link") == ()
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_cloud_refresh_cluster_shares_propagates_late_cluster_spell() -> None:
    """
    Purpose:
        Validate refresh_cluster_shares_for_conduit propagates a late cluster spell.
    Contract:
        - A post-join unique_per_conduit_cluster bind is not visible to the peer
          until refresh_cluster_shares_for_conduit runs.
        - The refresh leaves no live cluster-link session behind.
    Returns:
        None.
    Raises:
        AssertionError: If late cluster shares do not propagate.
    """
    frame_name = "component-cloud-refresh"
    owner_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    borrower_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    cloud = owner.get_conduit_cloud()
    registry = owner._aetheric_frame.devops_information_registry
    try:
        assert owner.link(borrower) is True
        cloud.create_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")

        with owner.transaction("bind"):
            late_spell_id = owner.bind(
                spell=BasicConfig,
                existence=Existence.unique_per_conduit_cluster,
                permissions="create",
                binding_name="late-cluster",
            )

        assert borrower.find_contracted_spell(late_spell_id) is None

        cloud.refresh_cluster_shares_for_conduit(owner)

        assert borrower.find_contracted_spell(late_spell_id) is not None
        assert registry.list_live_transactions_for_type("cluster_link") == ()
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_cloud_remove_conduit_from_cluster_clears_membership_and_contracts() -> None:
    """
    Purpose:
        Validate removing a borrower clears membership and shared spell visibility.
    Contract:
        - Borrowed cluster-scoped spells disappear after removal.
        - Cloud and registry membership views drop the borrower.
    Returns:
        None.
    Raises:
        AssertionError: If removal leaves runtime residue behind.
    """
    frame_name = "component-cloud-remove-member"
    owner_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    borrower_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    owner_spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    cloud = owner.get_conduit_cloud()
    registry = owner._aetheric_frame.devops_information_registry
    try:
        assert owner.link(borrower) is True
        cloud.create_cluster("cluster-a")
        cluster = cloud.get_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")
        assert borrower.find_contracted_spell(owner_spell_id) is not None

        cloud.remove_conduit_from_cluster(borrower, "cluster-a")

        assert borrower.find_contracted_spell(owner_spell_id) is None
        assert cloud.get_clusters_for_conduit(borrower.id) == []
        assert registry.get_clusters_for_conduit(borrower.id) == ()
        assert registry.get_clusters_for_conduit(owner.id) == (cluster.id,)
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_cloud_delete_cluster_cleans_registry_identity_and_memberships() -> None:
    """
    Purpose:
        Validate delete_cluster removes the cluster identity and membership edges.
    Contract:
        - The cluster name disappears from the cloud lookup.
        - The cluster identity is removed from the dev-ops registry.
        - Conduit membership edges are cleared for former members.
    Returns:
        None.
    Raises:
        AssertionError: If delete_cluster leaves registry state behind.
    """
    frame_name = "component-cloud-delete"
    owner_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    borrower_book = _make_spellbook(frame_name=frame_name, dynamic=True)
    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    cloud = owner.get_conduit_cloud()
    registry = owner._aetheric_frame.devops_information_registry
    try:
        cloud.create_cluster("cluster-a")
        cluster = cloud.get_cluster("cluster-a")
        cloud.add_conduit_to_cluster(owner, "cluster-a")
        cloud.add_conduit_to_cluster(borrower, "cluster-a")

        cloud.delete_cluster("cluster-a")

        assert cloud.list_cluster_names() == ()
        assert registry.get_identity(
            owner_kind="conduit_cluster",
            owner_id=cluster.id,
        ) is None
        assert registry.get_clusters_for_conduit(owner.id) == ()
        assert registry.get_clusters_for_conduit(borrower.id) == ()
    finally:
        owner.cleanup()
        borrower.cleanup()


def test_component_conduit_cloud_refresh_cluster_shares_requires_dynamic_mode() -> None:
    """
    Purpose:
        Validate refresh_cluster_shares_for_conduit is blocked in automatic mode.
    Contract:
        - Automatic posture rejects refresh_cluster_shares_for_conduit.
    Returns:
        None.
    Raises:
        AssertionError: If automatic posture allows cluster refresh.
    """
    frame_name = "component-cloud-refresh-automatic"
    spellbook = _make_spellbook(frame_name=frame_name, dynamic=False)
    conduit = spellbook.conjure(name="root")
    cloud = conduit.get_conduit_cloud()
    try:
        with pytest.raises(RuntimeError, match="dynamic mode"):
            cloud.refresh_cluster_shares_for_conduit(conduit)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


@pytest.mark.parametrize(
    "operation_name",
    (
        "create_cluster",
        "delete_cluster",
        "add_conduit_to_cluster",
        "remove_conduit_from_cluster",
        "refresh_cluster_shares_for_conduit",
    ),
)
def test_component_conduit_cloud_cluster_operations_require_dynamic_mode(
        operation_name: str,
) -> None:
    """
    Purpose:
        Validate every public cluster mutation surface is blocked outside dynamic mode.
    Contract:
        - Automatic posture rejects create/delete/add/remove/refresh cluster operations.
        - The dynamic-mode gate fires before any cluster lookup or mutation occurs.
    Args:
        operation_name: Public ConduitCloud operation under test.
    Returns:
        None.
    Raises:
        AssertionError: If any public cluster mutation surface bypasses the posture gate.
    """
    frame_name = f"component-cloud-gate-{operation_name}"
    spellbook = _make_spellbook(frame_name=frame_name, dynamic=False)
    conduit = spellbook.conjure(name="root")
    cloud = conduit.get_conduit_cloud()
    try:
        with pytest.raises(RuntimeError, match="dynamic mode"):
            if operation_name == "create_cluster":
                cloud.create_cluster("cluster-a")
            elif operation_name == "delete_cluster":
                cloud.delete_cluster("cluster-a")
            elif operation_name == "add_conduit_to_cluster":
                cloud.add_conduit_to_cluster(conduit, "cluster-a")
            elif operation_name == "remove_conduit_from_cluster":
                cloud.remove_conduit_from_cluster(conduit, "cluster-a")
            else:
                cloud.refresh_cluster_shares_for_conduit(conduit)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


@pytest.mark.parametrize(
    "operation_name",
    (
        "create_cluster",
        "delete_cluster",
        "add_conduit_to_cluster",
        "remove_conduit_from_cluster",
        "refresh_cluster_shares_for_conduit",
    ),
)
def test_component_conduit_cloud_cluster_operations_respect_disable_all_transactions_flag(
        operation_name: str,
) -> None:
    """
    Purpose:
        Validate cluster mutation surfaces are blocked by disable_all_transactions_after_conjure.
    Contract:
        - Dynamic posture alone is not enough once post-conjure transactions are disabled.
        - The public cloud operation raises before any cluster mutation or lookup can proceed.
    Args:
        operation_name: Public ConduitCloud operation under test.
    Returns:
        None.
    Raises:
        AssertionError: If the post-conjure transaction gate is bypassed.
    """
    frame_name = f"component-cloud-post-conjure-{operation_name}"
    spellbook = _make_spellbook(frame_name=frame_name, dynamic=True)
    spellbook._aetheric_frame_configuration.with_disable_all_transactions_after_conjure(
        True
    )
    conduit = spellbook.conjure(dynamic=True, name="root")
    cloud = conduit.get_conduit_cloud()
    try:
        with pytest.raises(RuntimeError, match="disabled"):
            if operation_name == "create_cluster":
                cloud.create_cluster("cluster-a")
            elif operation_name == "delete_cluster":
                cloud.delete_cluster("cluster-a")
            elif operation_name == "add_conduit_to_cluster":
                cloud.add_conduit_to_cluster(conduit, "cluster-a")
            elif operation_name == "remove_conduit_from_cluster":
                cloud.remove_conduit_from_cluster(conduit, "cluster-a")
            else:
                cloud.refresh_cluster_shares_for_conduit(conduit)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


@pytest.mark.parametrize(
    "operation_name",
    (
        "create_cluster",
        "delete_cluster",
        "add_conduit_to_cluster",
        "remove_conduit_from_cluster",
        "refresh_cluster_shares_for_conduit",
    ),
)
def test_component_conduit_cloud_cluster_operations_respect_disable_cluster_flag(
        operation_name: str,
) -> None:
    """
    Purpose:
        Validate cluster mutation surfaces are blocked by disable_conduit_cluster.
    Contract:
        - Dynamic posture alone is not enough when conduit-cluster operations are disabled.
        - The public cloud operation raises before any cluster mutation or lookup can proceed.
    Args:
        operation_name: Public ConduitCloud operation under test.
    Returns:
        None.
    Raises:
        AssertionError: If the conduit-cluster gate is bypassed.
    """
    frame_name = f"component-cloud-disable-cluster-{operation_name}"
    spellbook = _make_spellbook(frame_name=frame_name, dynamic=True)
    spellbook._aetheric_frame_configuration.with_disable_conduit_cluster(True)
    conduit = spellbook.conjure(dynamic=True, name="root")
    cloud = conduit.get_conduit_cloud()
    try:
        with pytest.raises(RuntimeError, match="disabled"):
            if operation_name == "create_cluster":
                cloud.create_cluster("cluster-a")
            elif operation_name == "delete_cluster":
                cloud.delete_cluster("cluster-a")
            elif operation_name == "add_conduit_to_cluster":
                cloud.add_conduit_to_cluster(conduit, "cluster-a")
            elif operation_name == "remove_conduit_from_cluster":
                cloud.remove_conduit_from_cluster(conduit, "cluster-a")
            else:
                cloud.refresh_cluster_shares_for_conduit(conduit)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


@pytest.mark.parametrize(
    "operation_name",
    (
        "get_cluster",
        "delete_cluster",
        "add_conduit_to_cluster",
        "remove_conduit_from_cluster",
    ),
)
def test_component_conduit_cloud_missing_cluster_operations_raise_value_error(
        operation_name: str,
) -> None:
    """
    Purpose:
        Validate public cluster operations fail cleanly when the target cluster is missing.
    Contract:
        - Missing cluster lookups raise ValueError on the public surface.
        - No public operation silently creates a missing cluster.
    Args:
        operation_name: Public ConduitCloud operation under test.
    Returns:
        None.
    Raises:
        AssertionError: If missing-cluster operations do not fail predictably.
    """
    frame_name = f"component-cloud-missing-{operation_name}"
    spellbook = _make_spellbook(frame_name=frame_name, dynamic=True)
    conduit = spellbook.conjure(dynamic=True, name="root")
    cloud = conduit.get_conduit_cloud()
    try:
        with pytest.raises(ValueError, match="does not exist"):
            if operation_name == "get_cluster":
                cloud.get_cluster("missing")
            elif operation_name == "delete_cluster":
                cloud.delete_cluster("missing")
            elif operation_name == "add_conduit_to_cluster":
                cloud.add_conduit_to_cluster(conduit, "missing")
            else:
                cloud.remove_conduit_from_cluster(conduit, "missing")
    finally:
        conduit.cleanup()
        spellbook.cleanup()
