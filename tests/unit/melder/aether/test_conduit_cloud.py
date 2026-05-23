import threading
from unittest.mock import MagicMock

import pytest

from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.system_state import SystemState


@pytest.fixture
def registry():
    registry = DevopsInformationRegistry("test_frame")
    yield registry
    registry.cleanup()


@pytest.fixture
def mock_frame():
    frame = MagicMock()
    frame_configuration = MagicMock()
    frame_configuration.disable_conduit_cluster = False
    frame_configuration.disable_all_transactions_after_conjure = False
    frame_configuration.system_state = SystemState.dynamic
    frame.frame_configuration = frame_configuration
    return frame


@pytest.fixture
def conduit_cloud(mock_frame, registry):
    """
    Provide a fresh ConduitCloud plus its borrowed backing stores.

    Returns:
        tuple[ConduitCloud, dict[str, Conduit], dict[str, str]]:
            The cloud plus the borrowed root registries.
    """
    root_conduits: dict[str, Conduit] = {}
    conduit_ids_by_name: dict[str, str] = {}
    cloud = ConduitCloud(
        "test_frame",
        mock_frame,
        root_conduits,
        conduit_ids_by_name,
        registry,
    )
    yield cloud, root_conduits, conduit_ids_by_name
    cloud.cleanup()


@pytest.fixture
def mock_conduit():
    """
    Provide a mock root conduit with stable id and name.

    Returns:
        MagicMock: Conduit double for lookup tests.
    """
    conduit = MagicMock()
    conduit.id = "conduit-1"
    conduit._id = "conduit-1"
    conduit.name = "test_conduit"
    conduit._name = "test_conduit"
    conduit.__dynamic_environment__ = True
    conduit._spellbook = None
    return conduit


def test_init(conduit_cloud) -> None:
    """
    Verify initialization stores borrowed registries and owned lock/id state.
    """
    cloud, root_conduits, conduit_ids_by_name = conduit_cloud

    assert cloud._name == "test_frame"
    assert cloud._conduits is root_conduits
    assert cloud._conduit_ids_by_name is conduit_ids_by_name
    assert isinstance(cloud._lock, type(threading.RLock()))
    assert cloud._id is not None
    assert not cloud._cleaned


def test_get_conduit_success(conduit_cloud, mock_conduit) -> None:
    """
    Verify root conduit lookup reads the borrowed frame-owned root stores.
    """
    cloud, root_conduits, conduit_ids_by_name = conduit_cloud
    root_conduits["conduit-1"] = mock_conduit
    conduit_ids_by_name["test_conduit"] = "conduit-1"

    result = cloud.get_conduit("test_conduit")

    assert result is mock_conduit
    assert cloud.get_conduit_by_name("test_conduit") is mock_conduit
    assert cloud.get_conduit_by_id("conduit-1") is mock_conduit


def test_get_conduit_not_found_raises(conduit_cloud) -> None:
    """
    Verify missing conduit lookups fail fast.
    """
    cloud, _, _ = conduit_cloud

    with pytest.raises(ValueError, match="not found"):
        cloud.get_conduit("missing")

    with pytest.raises(ValueError, match="not found"):
        cloud.get_conduit_by_id("missing")


def test_conduit_cloud_discovery_helpers_return_registered_names_and_ids(
        conduit_cloud,
        mock_conduit,
) -> None:
    """
    Verify the root-registry discovery helpers reflect the borrowed root stores.
    """
    cloud, root_conduits, conduit_ids_by_name = conduit_cloud
    root_conduits["conduit-1"] = mock_conduit
    conduit_ids_by_name["test_conduit"] = "conduit-1"

    assert cloud.list_conduit_ids() == ("conduit-1",)
    assert cloud.list_conduit_names() == ("test_conduit",)
    assert cloud.count_conduits() == 1
    assert cloud.has_conduit_id("conduit-1") is True
    assert cloud.has_conduit_name("test_conduit") is True
    assert cloud.find_conduit_id_by_name("test_conduit") == "conduit-1"


def test_conduit_cloud_discovery_helpers_report_missing_entries(
        conduit_cloud,
) -> None:
    """
    Verify missing root-registry entries report cleanly.
    """
    cloud, _, _ = conduit_cloud

    assert cloud.count_conduits() == 0
    assert cloud.has_conduit_id("missing") is False
    assert cloud.has_conduit_name("missing") is False
    assert cloud.find_conduit_id_by_name("missing") is None


def test_list_cloud_names_reflects_borrowed_dynamic_registry(
        conduit_cloud,
        mock_conduit,
) -> None:
    """
    Verify the cloud-name surface is derived from the borrowed root registry.
    """
    cloud, root_conduits, conduit_ids_by_name = conduit_cloud
    root_conduits["conduit-1"] = mock_conduit
    conduit_ids_by_name["test_conduit"] = "conduit-1"

    assert cloud.list_cloud_names() == ("test_conduit",)


def test_cluster_lifecycle_and_membership_apis(conduit_cloud, mock_conduit) -> None:
    """
    Verify cluster APIs still work on the cloud-owned cluster registry.
    """
    cloud, _, _ = conduit_cloud

    cloud.create_cluster("cluster-1")
    cloud.add_conduit_to_cluster(mock_conduit, "cluster-1")

    assert cloud.list_cluster_names() == ("cluster-1",)
    assert cloud.get_clusters_for_conduit("conduit-1") == ["cluster-1"]

    cloud.remove_conduit_from_cluster(mock_conduit, "cluster-1")
    cloud.delete_cluster("cluster-1")

    assert cloud.list_cluster_names() == ()


def test_cleanup_drops_fields_but_does_not_clear_borrowed_registries(
        conduit_cloud,
        mock_conduit,
) -> None:
    """
    Verify cleanup releases the cloud surface without owning borrowed registry data.
    """
    cloud, root_conduits, conduit_ids_by_name = conduit_cloud
    root_conduits["conduit-1"] = mock_conduit
    conduit_ids_by_name["test_conduit"] = "conduit-1"

    cloud.cleanup()

    assert cloud._cleaned
    assert not hasattr(cloud, "_lock")
    assert root_conduits["conduit-1"] is mock_conduit
    assert conduit_ids_by_name["test_conduit"] == "conduit-1"


def test_cleanup_is_idempotent(conduit_cloud) -> None:
    """
    Verify repeated cleanup is safe.
    """
    cloud, _, _ = conduit_cloud
    cloud.cleanup()
    cloud.cleanup()
    assert cloud._cleaned


def test_cleanup_returns_early_when_cleaned_flips_inside_lock(conduit_cloud) -> None:
    """
    Verify cleanup returns safely if another path marks the cloud cleaned inside the lock.
    """
    cloud, root_conduits, _ = conduit_cloud
    root_conduits["x"] = MagicMock()
    original_lock = cloud._lock

    class _LockThatMarksCleaned:
        def __enter__(self_inner):
            cloud._cleaned = True
            return self_inner

        def __exit__(self_inner, exc_type, exc_value, traceback):
            return False

    try:
        cloud._lock = _LockThatMarksCleaned()
        cloud.cleanup()
    finally:
        cloud._lock = original_lock

    assert hasattr(cloud, "_conduits")


def test_context_manager(conduit_cloud) -> None:
    """
    Verify ConduitCloud supports context-manager lock ownership.
    """
    cloud, _, _ = conduit_cloud
    with cloud as entered:
        assert entered is cloud


def test_methods_raise_after_cleanup(conduit_cloud, mock_conduit) -> None:
    """
    Verify public methods guard against use-after-clean.
    """
    cloud, _, _ = conduit_cloud
    cloud.cleanup()

    with pytest.raises(RuntimeError):
        cloud.get_conduit("any")

    with pytest.raises(RuntimeError):
        cloud.list_cloud_names()

    with pytest.raises(RuntimeError):
        cloud.create_cluster("cluster-1")
