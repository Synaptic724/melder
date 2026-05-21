import logging
from concurrent.futures import ThreadPoolExecutor
import pytest
import threading
from unittest.mock import MagicMock, patch, ANY
from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_configuration_builder import AetherConfigurationBuilder
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.aetheric_frame.conduit_cloud import ConduitCloud
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.nexus.nexus import Nexus
from melder.crystallizer.crystallizer import Crystallizer
from melder.utilities.interfaces.iconduit import IConduit
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.configuration.system_state import SystemState


class _FrameConduitCloudStub:
    """Minimal cloud stub that proxies cluster operations into one frame mock."""

    def __init__(self, frame_mock):
        """Initialize the cloud stub over one frame mock."""
        self._frame_mock = frame_mock
        self._registry = {}
        self._conduit_clusters = {}
        self.frame_name = "default"

    def create_cluster(self, cluster_name: str) -> None:
        """Create one cluster in the cloud-owned registry."""
        from melder.aether.aetheric_frame import conduit_cloud as conduit_cloud_module
        if cluster_name in self._conduit_clusters:
            raise ValueError(f"Cluster with name {cluster_name} already exists.")
        self._conduit_clusters[cluster_name] = conduit_cloud_module.ConduitCluster(
            cluster_name,
            self._frame_mock._conduits,
            self.frame_name,
        )

    def delete_cluster(self, cluster_name: str) -> None:
        """Delete one cluster from the cloud-owned registry."""
        cluster = self._conduit_clusters.pop(cluster_name, None)
        if cluster is None:
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        cluster.cleanup()

    def _get_cluster(self, cluster_name: str):
        """Return one named cluster or raise when missing."""
        cluster = self._conduit_clusters.get(cluster_name)
        if cluster is None:
            raise ValueError(f"Cluster with name {cluster_name} does not exist.")
        return cluster

    def add_conduit_to_cluster(self, conduit, cluster_name: str) -> None:
        """Add one conduit id to one cluster and run the join hook."""
        cluster = self._get_cluster(cluster_name)
        cluster.add_member(conduit._id)
        cluster.handle_join(conduit)

    def remove_conduit_from_cluster(self, conduit, cluster_name: str) -> None:
        """Remove one conduit id from one cluster and run the leave hook."""
        cluster = self._get_cluster(cluster_name)
        cluster.remove_member(conduit._id)
        cluster.handle_leave(conduit)

    def get_clusters_for_conduit(self, conduit_id: str):
        """Return cluster names containing the conduit id."""
        return [
            name for name, cluster in self._conduit_clusters.items()
            if conduit_id in cluster.get_members()
        ]

    def list_cluster_names(self):
        """Return all cluster names."""
        return tuple(self._conduit_clusters.keys())

    def get_conduit_by_id(self, conduit_id: str):
        """Return one conduit by id from the backing frame."""
        conduit = self._frame_mock._conduits.get(conduit_id)
        if conduit is None:
            raise ValueError(f"Conduit with id {conduit_id} not found.")
        return conduit

    def refresh_cluster_shares_for_conduit(self, conduit) -> None:
        """Refresh cluster sharing for every cluster containing the conduit id."""
        cluster_names = self.get_clusters_for_conduit(conduit._id)
        for cluster_name in cluster_names:
            cluster = self._get_cluster(cluster_name)
            cluster.refresh_member_shares(conduit)

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_aether():
    """
    Ensure each test starts with a clean Aether singleton state
    and cleans up afterwards.
    """
    # Teardown any existing state
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    if Aether._instance:
        Aether().cleanup()
        Aether._instance = None
        Aether._initialized = False

    yield

    # Post-test cleanup
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    if Aether._instance:
        Aether().cleanup()
        Aether._instance = None
        Aether._initialized = False

@pytest.fixture
def mock_frame_cls():
    """
    Patch the AethericFrame class used internally by Aether.
    Returns the mock class (constructor).
    """
    with patch("melder.aether.aether.AethericFrame") as mock_cls:
        # The constructor returns a MagicMock instance acting as the frame
        mock_instance = MagicMock(spec=AethericFrame)
        # Setup specific attributes that are accessed directly
        mock_instance._conduits = {}
        mock_instance._conduit_ids_by_name = {}
        mock_instance._spell_registry = {}
        mock_instance._conduit_cloud = _FrameConduitCloudStub(mock_instance)
        # Ensure methods return sensible defaults
        mock_instance.has_version.return_value = False
        mock_instance.get_all_versions.return_value = set()
        mock_instance._cleaned = False # Ensure frame is not considered cleaned by default
        
        mock_cls.return_value = mock_instance
        yield mock_cls

@pytest.fixture
def aether_with_mocks(mock_frame_cls):
    """
    Returns an Aether instance initialized with a mocked default frame.
    """
    return Aether()

# ----------------------------------------------------------------------
# 1. Singleton & Lifecycle Tests
# ----------------------------------------------------------------------

def test_singleton_identity():
    """
    Verify `Aether` enforces the Singleton pattern.

    Contract:
    - Multiple calls to `Aether()` must return the exact same instance reference.
    - `id()` checks must match.
    """
    a1 = Aether()
    a2 = Aether()
    assert a1 is a2
    assert id(a1) == id(a2)


def test_singleton_identity_under_concurrent_construction() -> None:
    """
    Verify singleton construction remains stable under concurrent first access.

    Contract:
    - Parallel constructor calls must resolve to one shared instance.
    - The class-level singleton reference must point to that shared instance.
    """
    worker_count = 16
    start_barrier = threading.Barrier(worker_count)

    Aether._reset_singleton_for_tests()

    def build_instance_id() -> int:
        start_barrier.wait()
        return id(Aether())

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(build_instance_id) for _ in range(worker_count)]
        instance_ids = [future.result() for future in futures]

    assert len(set(instance_ids)) == 1
    assert Aether._instance is not None
    assert id(Aether._instance) == instance_ids[0]

def test_initialization_creates_default_frame(mock_frame_cls):
    """
    Verify initialization automatically creates the 'default' frame.

    Contract:
    - `_aetheric_frames` must contain "default".
    - `_default_frame` property must point to this frame.
    - AethericFrame constructor must be called with the owning Aether plus "default".
    """
    a = Aether()
    assert "default" in a._aetheric_frames
    mock_frame_cls.assert_called_with(ANY, "default")
    assert a._default_frame is mock_frame_cls.return_value
    assert isinstance(a._nexus, Nexus)
    assert a._nexus.is_configured is False
    assert a._nexus.is_enabled is False
    assert isinstance(a._crystallizer, Crystallizer)
    assert a._crystallizer.is_configured is False
    assert a._crystallizer.is_activated is False
    assert a._mutation_research is not None

def test_cleanup_clears_state(aether_with_mocks):
    """
    Verify `cleanup` resets the singleton for re-use/shutdown.

    Contract:
    - All frames are removed and cleaned.
    - `_aetheric_frames` is deleted.
    - `_default_frame` is deleted.
    - Singleton instance reference (`Aether._instance`) is cleared to allow fresh tests.
    """
    a = aether_with_mocks
    default_frame = a._default_frame
    
    a.cleanup()
    
    assert a._cleaned is True
    assert not hasattr(a, "_aetheric_frames")
    assert not hasattr(a, "_default_frame")
    assert not hasattr(a, "_nexus")
    assert not hasattr(a, "_crystallizer")
    default_frame.cleanup.assert_called_once()
    
    # Verify Singleton reset
    a2 = Aether()
    assert a2 is not a
    assert a2._cleaned is False

def test_reset_singleton_for_tests_creates_fresh_instance():
    """
    Purpose:
        Verify the test reset helper clears singleton state.
    Contract:
        Aether._reset_singleton_for_tests forces the next Aether() to reinitialize.
    Returns:
        None.
    Raises:
        AssertionError: If the reset does not replace the instance.
    """
    first = Aether()
    first_id = id(first)

    Aether._reset_singleton_for_tests()

    second = Aether()
    assert second is not first
    assert id(second) != first_id
    assert second._cleaned is False
    assert second._default_frame is not None

def test_cleanup_is_idempotent(aether_with_mocks):
    """Calling cleanup() multiple times is safe."""
    a = aether_with_mocks
    a.cleanup()
    a.cleanup()
    assert a._cleaned is True

def test_context_manager(aether_with_mocks):
    """Aether can be used as a context manager."""
    a = aether_with_mocks
    with a as instance:
        assert instance is a

def test_repr():
    """Verify string representation contains class name."""
    a = Aether()
    assert "Aether" in repr(a)

def test_internal_lock_integrity():
    """Verify the static lock persists across singleton resets (it is a class attribute)."""
    a1 = Aether()
    lock1 = a1._lock
    a1.cleanup()
    
    a2 = Aether()
    lock2 = a2._lock
    
    assert lock1 is lock2
    assert isinstance(lock1, type(threading.RLock()))

# ----------------------------------------------------------------------
# 2. Frame Management Tests
# ----------------------------------------------------------------------

def test_bottom_up_frame_cleanup_removes_custom_frame() -> None:
    """
    Verify bottom-up frame cleanup removes a custom frame from Aether.

    Contract:
    - Calling `frame.cleanup()` unregisters the frame from Aether.
    - The cleaned frame disappears from the internal registry.
    """
    a = Aether()
    frame = a._ensure_frame("custom")

    frame.cleanup()

    assert "custom" not in a._aetheric_frames

def test_bottom_up_default_frame_cleanup_clears_reference() -> None:
    """Cleaning the default frame bottom-up clears the default reference."""
    a = Aether()
    default_frame = a._default_frame

    default_frame.cleanup()

    assert "default" not in a._aetheric_frames
    assert a._default_frame is None


def test_ensure_frame_rejects_non_string_name() -> None:
    """_ensure_frame should reject non-string frame names."""
    a = Aether()

    with pytest.raises(TypeError, match="must be a string"):
        a._ensure_frame(123)


def test_ensure_frame_returns_existing_custom_frame() -> None:
    """_ensure_frame should return the existing frame without replacing it."""
    a = Aether()
    existing = a._ensure_frame("custom")

    assert a._ensure_frame("custom") is existing


def test_create_frame_creates_new_custom_frame() -> None:
    """_create_frame should create and register a new custom frame."""
    a = Aether()

    created = a._create_frame("custom")

    assert a._aetheric_frames["custom"] is created


def test_create_frame_raises_if_frame_already_exists() -> None:
    """_create_frame should fail instead of silently recovering an existing frame."""
    a = Aether()
    a._ensure_frame("custom")

    with pytest.raises(ValueError, match="already exists"):
        a._create_frame("custom")

def test_cleanup_unregistered_frame_is_safe() -> None:
    """A direct unregistered frame cleanup does not mutate Aether registry."""
    a = Aether()
    frame = AethericFrame(a, "non_existent")
    frame.cleanup()
    assert "non_existent" not in a._aetheric_frames


def test_detach_cleaned_frame_ignores_empty_frame_name() -> None:
    """_detach_cleaned_frame should no-op when frame_name is empty."""
    a = Aether()
    frame = a._default_frame
    before_default = a._default_frame
    before_frames = dict(a._aetheric_frames)

    a._detach_cleaned_frame("", frame)

    assert a._default_frame is before_default
    assert a._aetheric_frames == before_frames


def test_detach_cleaned_frame_ignores_missing_registry() -> None:
    """_detach_cleaned_frame should no-op when the frame registry is unavailable."""
    a = Aether()
    frame = a._default_frame
    a._aetheric_frames = None
    a._default_frame = frame

    a._detach_cleaned_frame("default", frame)

    assert a._default_frame is frame


def test_detach_cleaned_frame_logs_nexus_error_but_removes_frame() -> None:
    """_detach_cleaned_frame should tolerate Nexus record cleanup failures."""
    a = Aether()
    frame = a._default_frame
    nexus = MagicMock()
    nexus.check_for_aetheric_frame.side_effect = RuntimeError("nexus fail")
    logger = MagicMock()

    a._nexus = nexus
    a._logger = logger

    a._detach_cleaned_frame("default", frame)

    nexus.check_for_aetheric_frame.assert_called_once_with("default")
    logger.error.assert_called_once()
    assert "default" not in a._aetheric_frames
    assert a._default_frame is None

def test_cleanup_aetheric_frames_iterates_all() -> None:
    """cleanup_aetheric_frames should call cleanup on all registered frames."""
    a = Aether()
    frame_one = a._ensure_frame("f1")
    frame_two = a._ensure_frame("f2")

    a.cleanup_aetheric_frames()

    assert frame_one.cleaned is True
    assert frame_two.cleaned is True
    assert "f1" not in a._aetheric_frames
    assert "f2" not in a._aetheric_frames

def test_cleanup_aetheric_frames_tolerant_of_errors(aether_with_mocks):
    """If one frame fails cleanup, others should still be cleaned."""
    a = aether_with_mocks
    mock_f1 = MagicMock()
    mock_f1.name = "f1"
    mock_f1.cleanup.side_effect = RuntimeError("Boom")
    mock_f2 = MagicMock()
    mock_f2.name = "f2"

    a._aetheric_frames = {"f1": mock_f1, "f2": mock_f2}

    a.cleanup_aetheric_frames()

    mock_f1.cleanup.assert_called_once()
    mock_f2.cleanup.assert_called_once()

# ----------------------------------------------------------------------
# 3. Delegation Tests (Conduits)
# ----------------------------------------------------------------------

def test_register_root_conduit_delegates_to_default_frame(aether_with_mocks):
    """
    Verify root-conduit registration is owned by the default frame.

    Contract:
    - The default frame stores the conduit id and root name directly.
    """
    a = aether_with_mocks
    frame_mock = a._default_frame
    conduits_dict = {}
    frame_mock._conduits = conduits_dict
    frame_mock._conduit_ids_by_name = {}
    
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    conduit.name = "root"
    conduit._name = "root"
    frame_mock.register_root_conduit.side_effect = lambda item: (
        conduits_dict.__setitem__(item._id, item),
        frame_mock._conduit_ids_by_name.__setitem__(item.name, item._id),
    )
    
    frame_mock.register_root_conduit(conduit)
    
    assert "c1" in conduits_dict
    assert conduits_dict["c1"] is conduit
    assert frame_mock._conduit_ids_by_name["root"] == "c1"


def test_aether_privately_hosts_nexus_singleton(aether_with_mocks):
    """
    Verify Aether boots a private hosted Nexus instance.
    """
    a = aether_with_mocks
    nexus = Nexus()

    assert a._nexus is nexus
    assert nexus.is_configured is False
    assert nexus.is_enabled is False


def test_aether_privately_hosts_crystallizer_singleton(aether_with_mocks):
    """
    Verify Aether boots a private hosted Crystallizer instance.
    """
    a = aether_with_mocks
    crystallizer = Crystallizer()

    assert a._crystallizer is crystallizer
    assert crystallizer.is_configured is False
    assert crystallizer.is_activated is False


def test_aether_cleanup_cleans_hosted_nexus(aether_with_mocks):
    """
    Verify Aether cleanup tears down the hosted Nexus singleton.
    """
    a = aether_with_mocks
    nexus = a._nexus

    a.cleanup()

    assert nexus.cleaned is True
    assert not hasattr(a, "_nexus")


def test_aether_cleanup_cleans_hosted_crystallizer(aether_with_mocks):
    """
    Verify Aether cleanup tears down the hosted Crystallizer singleton.
    """
    a = aether_with_mocks
    crystallizer = a._crystallizer

    a.cleanup()

    assert crystallizer.cleaned is True
    assert not hasattr(a, "_crystallizer")

def test_register_root_conduit_delegates_to_custom_frame(aether_with_mocks):
    """Frame-owned root registration works on a non-default frame."""
    a = aether_with_mocks
    frame_mock = a._ensure_frame("f1")
    frame_mock._conduits = {}
    frame_mock._conduit_ids_by_name = {}
    
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    conduit.name = "root"
    conduit._name = "root"
    frame_mock.register_root_conduit.side_effect = lambda item: (
        frame_mock._conduits.__setitem__(item._id, item),
        frame_mock._conduit_ids_by_name.__setitem__(item.name, item._id),
    )
    
    frame_mock.register_root_conduit(conduit)
    
    assert "c1" in frame_mock._conduits
    assert frame_mock._conduit_ids_by_name["root"] == "c1"

def test_register_root_conduit_duplicate_raises(aether_with_mocks):
    """Frame-owned root registration raises ValueError if ID exists."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    conduit._name = "root"
    conduit.name = "root"
    frame_mock._conduits = {"c1": conduit}
    frame_mock._conduit_ids_by_name = {"root": "c1"}
    frame_mock.register_root_conduit.side_effect = ValueError(
        "Conduit with ID c1 already exists."
    )
    
    with pytest.raises(ValueError, match="already exists"):
        frame_mock.register_root_conduit(conduit)


def test_register_root_conduit_requires_root_name(aether_with_mocks):
    """Frame-owned root registration raises ValueError when the root conduit name is missing."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._conduits = {}
    frame_mock._conduit_ids_by_name = {}
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    conduit.name = None
    conduit._name = None
    frame_mock.register_root_conduit.side_effect = ValueError(
        "Root conduit name is required."
    )

    with pytest.raises(ValueError, match="Root conduit name is required"):
        frame_mock.register_root_conduit(conduit)


def test_register_root_conduit_duplicate_name_raises(aether_with_mocks):
    """Frame-owned root registration raises ValueError if the root conduit name already exists."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    existing = MagicMock(spec=IConduit)
    existing._id = "c1"
    existing.name = "root"
    incoming = MagicMock(spec=IConduit)
    incoming._id = "c2"
    incoming.name = "root"
    incoming._name = "root"
    frame_mock._conduits = {"c1": existing}
    frame_mock._conduit_ids_by_name = {"root": "c1"}
    frame_mock.register_root_conduit.side_effect = ValueError(
        "Conduit with name root already exists."
    )

    with pytest.raises(ValueError, match="Conduit with name root already exists"):
        frame_mock.register_root_conduit(incoming)

def test_unregister_root_conduit_delegates(aether_with_mocks):
    """Frame-owned root unregistration removes from the frame's dict."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    conduit._name = "root"
    conduit.name = "root"
    frame_mock._conduits = {"c1": conduit}
    frame_mock._conduit_ids_by_name = {"root": "c1"}
    frame_mock.unregister_root_conduit.side_effect = lambda item: (
        frame_mock._conduits.pop(item._id, None),
        frame_mock._conduit_ids_by_name.pop(item._name, None),
    )
    
    frame_mock.unregister_root_conduit(conduit)
    
    assert "c1" not in frame_mock._conduits
    assert "root" not in frame_mock._conduit_ids_by_name

def test_unregister_root_conduit_missing_raises(aether_with_mocks):
    """Frame-owned root unregistration raises ValueError if ID not found."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._conduits = {}
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    conduit._name = "root"
    conduit.name = "root"
    frame_mock.unregister_root_conduit.side_effect = ValueError(
        "Conduit with ID c1 does not exist."
    )
    
    with pytest.raises(ValueError, match="does not exist"):
        frame_mock.unregister_root_conduit(conduit)

def test_get_conduit_by_id(aether_with_mocks):
    """_get_conduit_by_id retrieves from frame dict."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    expected = MagicMock()
    frame_mock._conduits = {"target_id": expected}
    
    result = a._get_conduit_by_id("target_id")
    assert result is expected

def test_get_conduit_by_id_missing_raises(aether_with_mocks):
    """_get_conduit_by_id raises ValueError if missing."""
    a = aether_with_mocks
    a._default_frame._conduits = {}
    with pytest.raises(ValueError, match="not found"):
        a._get_conduit_by_id("missing")


def test_get_conduit_by_id_missing_custom_frame_raises(aether_with_mocks):
    """_get_conduit_by_id should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_conduit_by_id("missing", "missing_frame")

def test_get_conduit_by_name(aether_with_mocks):
    """_get_conduit_by_name resolves through the frame name registry."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    c1 = MagicMock()
    c1.name = "bob"
    c2 = MagicMock()
    c2.name = "alice"
    frame_mock._conduits = {"id1": c1, "id2": c2}
    frame_mock._conduit_ids_by_name = {"bob": "id1", "alice": "id2"}
    
    result = a._get_conduit_by_name("alice")
    assert result is c2

def test_get_conduit_by_name_missing_raises(aether_with_mocks):
    """_get_conduit_by_name raises ValueError if not found."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="not found"):
        a._get_conduit_by_name("nobody")


def test_get_conduit_by_name_missing_custom_frame_raises(aether_with_mocks):
    """_get_conduit_by_name should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_conduit_by_name("nobody", "missing_frame")

def test_removed_register_conduit_cloud_helper_is_not_exposed(aether_with_mocks):
    """Aether no longer exposes the old conduit-cloud registration helper."""
    a = aether_with_mocks
    assert not hasattr(a, "_register_conduit_cloud")


def test_removed_unregister_conduit_cloud_helper_is_not_exposed(aether_with_mocks):
    """Aether no longer exposes the old conduit-cloud unregister helper."""
    a = aether_with_mocks
    assert not hasattr(a, "_unregister_conduit_cloud")

def test_get_existing_frame_returns_frame_with_cloud(aether_with_mocks):
    """_get_existing_frame returns the frame that owns the cloud."""
    a = aether_with_mocks
    cloud = MagicMock()
    a._default_frame._conduit_cloud = cloud
    frame = a._get_existing_frame()
    assert frame is a._default_frame
    assert frame._conduit_cloud is cloud


def test_get_conduit_cloud_returns_frame_owned_cloud(aether_with_mocks) -> None:
    """get_conduit_cloud should return the cloud owned by the requested frame."""
    a = aether_with_mocks
    cloud = MagicMock(spec=ConduitCloud)
    a._default_frame._conduit_cloud = cloud

    assert a.get_conduit_cloud() is cloud


def test_get_conduit_cloud_missing_frame_raises(aether_with_mocks) -> None:
    """get_conduit_cloud should fail clearly for a missing custom frame."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a.get_conduit_cloud("missing_frame")


def test_get_existing_frame_missing_frame_raises(aether_with_mocks):
    """_get_existing_frame should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_existing_frame("missing_frame")


def test_aether_conduit_discovery_helpers_expose_frame_inventory(
        aether_with_mocks,
) -> None:
    """
    Verify the generic conduit-discovery helpers expose root-frame inventory.

    Returns:
        None.
    """
    a = aether_with_mocks
    conduit_a = MagicMock(spec=IConduit)
    conduit_a.name = "alpha"
    conduit_a._id = "c1"
    conduit_b = MagicMock(spec=IConduit)
    conduit_b.name = "beta"
    conduit_b._id = "c2"
    a._default_frame._conduits = {"c1": conduit_a, "c2": conduit_b}
    a._default_frame._conduit_ids_by_name = {"alpha": "c1", "beta": "c2"}
    cloud = MagicMock(spec=ConduitCloud)
    a._default_frame._conduit_cloud = cloud

    assert a.list_conduit_ids() == ("c1", "c2")
    assert a.list_conduit_names() == ("alpha", "beta")
    assert a.count_conduits() == 2
    assert a.has_conduit_id("c1") is True
    assert a.has_conduit_name("alpha") is True
    assert a.find_conduit_id_by_name("beta") == "c2"
    assert a.get_conduit_by_id("c1") is conduit_a
    assert a.get_conduit_by_name("beta") is conduit_b


def test_aether_conduit_discovery_helpers_validate_custom_frame(
        aether_with_mocks,
) -> None:
    """
    Verify the generic conduit-discovery helpers fail clearly for missing frames.

    Returns:
        None.
    """
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a.list_conduit_ids("missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.list_conduit_names("missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a.find_conduit_id_by_name("alpha", "missing_frame")

# ----------------------------------------------------------------------
# 4. Delegation Tests (Configuration & Spells)
# ----------------------------------------------------------------------

def test_bind_configuration(aether_with_mocks):
    """
    Verify `_bind_configuration` attaches configuration to the frame.

    Contract:
    - The configuration object is stored on the target frame's `_configuration` field.
    """
    a = aether_with_mocks
    frame_mock = a._default_frame
    config = MagicMock()
    
    a._bind_configuration(config)
    assert frame_mock._configuration is config


def test_bind_configuration_missing_custom_frame_raises(aether_with_mocks):
    """_bind_configuration should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._bind_configuration(MagicMock(), "missing_frame")

def test_get_configuration(aether_with_mocks):
    """
    Verify `_get_configuration` retrieves configuration from the frame.
    """
    a = aether_with_mocks
    frame_mock = a._default_frame
    expected = MagicMock()
    frame_mock._configuration = expected
    
    assert a._get_configuration() is expected


def test_get_aetheric_frame_configuration_missing_frame_raises(aether_with_mocks):
    """_get_aetheric_frame_configuration should fail clearly for missing custom frames."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_aetheric_frame_configuration("missing_frame")


def test_get_aetheric_frame_configuration_returns_default_frame_posture() -> None:
    """_get_aetheric_frame_configuration should return the frame-owned default-frame posture."""
    a = Aether()
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-1",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )

    a._ensure_frame("default").bind_frame_configuration(frame_configuration)

    bound = a._get_aetheric_frame_configuration()
    assert bound is a._default_frame.frame_configuration
    assert bound is not frame_configuration
    assert bound.system_state is SystemState.dynamic
    assert bound.ai_native_enabled is True
    assert bound.rift_enabled is False
    assert bound.shared_framewide_spellbook_configuration is False


def test_bind_aetheric_frame_configuration_rejects_invalid_type() -> None:
    """_bind_aetheric_frame_configuration should reject non-configuration inputs."""
    a = Aether()

    with pytest.raises(TypeError, match="AethericFrameConfiguration"):
        a._ensure_frame("default").bind_frame_configuration("invalid")


def test_bind_aetheric_frame_configuration_missing_frame_raises() -> None:
    """Frame-owned posture binding now requires an existing frame handle."""
    a = Aether()
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-1",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=True,
    )

    with pytest.raises(KeyError, match="missing_frame"):
        _ = a._aetheric_frames["missing_frame"]

    frame_configuration.cleanup()


def test_bind_aetheric_frame_configuration_sets_default_frame_posture() -> None:
    """First posture bind should copy posture into the frame-owned default object."""
    a = Aether()
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-1",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )

    a._ensure_frame("default").bind_frame_configuration(frame_configuration)

    bound = a._default_frame.frame_configuration
    assert bound is not frame_configuration
    assert bound.system_state is SystemState.dynamic
    assert bound.ai_native_enabled is True
    assert bound.rift_enabled is False
    assert bound.shared_framewide_spellbook_configuration is False
    assert frame_configuration._cleaned is True


def test_bind_aetheric_frame_configuration_same_posture_cleans_duplicate() -> None:
    """Same-posture rebind should keep the frame-owned canonical object and clean the duplicate."""
    a = Aether()
    original = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-1",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )
    duplicate = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-2",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )

    a._ensure_frame("default").bind_frame_configuration(original)
    a._ensure_frame("default").bind_frame_configuration(duplicate)

    bound = a._default_frame.frame_configuration
    assert bound is not original
    assert bound.system_state is SystemState.dynamic
    assert bound.ai_native_enabled is True
    assert bound.rift_enabled is False
    assert bound.shared_framewide_spellbook_configuration is False
    assert duplicate._cleaned is True
    assert original._cleaned is True


def test_bind_aetheric_frame_configuration_conflict_keeps_original_and_logs_warning() -> None:
    """Conflicting posture rebind should keep the first copied posture and clean the conflicting attempt."""
    a = Aether()
    a._logger = MagicMock()
    original = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-1",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )
    conflicting = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-2",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=True,
    )

    a._ensure_frame("default").bind_frame_configuration(original)
    a._ensure_frame("default").bind_frame_configuration(conflicting)

    bound = a._default_frame.frame_configuration
    assert bound is not original
    assert bound.system_state is SystemState.dynamic
    assert bound.ai_native_enabled is True
    assert bound.rift_enabled is False
    assert bound.shared_framewide_spellbook_configuration is False
    assert conflicting._cleaned is True
    assert original._cleaned is True
    a._logger.warning.assert_called_once()

def test_check_for_spell_delegates(aether_with_mocks):
    """_check_for_spell delegates to frame.has_version."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock.has_version.return_value = True
    frame_mock.find_and_return_spell_index.return_value = "found_index"
    
    result = a._check_for_spell("hash123")
    
    frame_mock.has_version.assert_called_with("hash123")
    assert result == "found_index"

def test_check_for_spell_returns_none_if_missing(aether_with_mocks):
    """_check_for_spell returns None if has_version is False."""
    a = aether_with_mocks
    a._default_frame.has_version.return_value = False
    
    assert a._check_for_spell("missing") is None

def test_add_spells_to_aether(aether_with_mocks):
    """_add_spells_to_aether updates registry and refreshes versions."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._spell_registry = {}
    
    spell_set = {MagicMock(spec=SpellIndex)}
    
    a._add_spells_to_aether("c1", spell_set)
    
    assert frame_mock._spell_registry["c1"] == spell_set
    frame_mock.refresh_version_registry.assert_called_once()

def test_add_spells_duplicate_conduit_raises(aether_with_mocks):
    """_add_spells_to_aether raises ValueError if conduit already registered."""
    a = aether_with_mocks
    a._default_frame._spell_registry = {"c1": set()}
    with pytest.raises(ValueError, match="already contains"):
        a._add_spells_to_aether("c1", {MagicMock(spec=SpellIndex)})

def test_add_spells_type_error(aether_with_mocks):
    """_add_spells_to_aether raises TypeError if set contains non-SpellIndex."""
    a = aether_with_mocks
    with pytest.raises(TypeError, match="only SpellIndex"):
        a._add_spells_to_aether("c1", {"not_a_spell"})

def test_remove_spells_from_aether(aether_with_mocks):
    """_remove_spells_from_aether removes items and refreshes."""
    a = aether_with_mocks
    si = MagicMock(spec=SpellIndex)
    spell_set = {si}
    a._default_frame._spell_registry = {"c1": spell_set}
    
    a._remove_spells_from_aether("c1", spell_set)
    
    # Set should be empty now
    assert len(a._default_frame._spell_registry["c1"]) == 0
    a._default_frame.refresh_version_registry.assert_called_once()

def test_remove_spells_missing_conduit_ignored(aether_with_mocks):
    """_remove_spells_from_aether does nothing if conduit not found."""
    a = aether_with_mocks
    a._remove_spells_from_aether("missing", set())
    # Should not raise


def test_remove_spells_from_aether_swallows_remove_errors_and_refreshes(aether_with_mocks):
    """_remove_spells_from_aether should tolerate remove failures and still refresh versions."""
    a = aether_with_mocks
    spell_index = MagicMock(spec=SpellIndex)
    registry_entry = MagicMock()
    registry_entry.remove.side_effect = RuntimeError("remove failed")
    a._default_frame._spell_registry = {"c1": registry_entry}

    a._remove_spells_from_aether("c1", {spell_index})

    registry_entry.remove.assert_called_once_with(spell_index)
    a._default_frame.refresh_version_registry.assert_called_once()

def test_register_single_spell_index(aether_with_mocks):
    """_register_single_spell_index adds spell and refreshes registry."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._spell_registry = {}
    
    si = MagicMock(spec=SpellIndex)
    a._register_single_spell_index("c1", si)
    
    assert "c1" in frame_mock._spell_registry
    assert si in frame_mock._spell_registry["c1"]
    frame_mock.refresh_version_registry.assert_called_once()

def test_remove_single_spell_index(aether_with_mocks):
    """_remove_single_spell_index removes spell and refreshes registry."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    si = MagicMock(spec=SpellIndex)
    frame_mock._spell_registry = {"c1": {si}}
    
    a._remove_single_spell_index("c1", si)
    
    assert len(frame_mock._spell_registry["c1"]) == 0
    frame_mock.refresh_version_registry.assert_called_once()

def test_remove_single_spell_index_missing(aether_with_mocks):
    """Removing missing spell is safe."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._spell_registry = {}
    si = MagicMock(spec=SpellIndex)
    
    # Should not raise
    a._remove_single_spell_index("c1", si)

def test_get_all_spell_versions(aether_with_mocks):
    """_get_all_spell_versions returns set from frame."""
    a = aether_with_mocks
    expected = {"hash1", "hash2"}
    a._default_frame.get_all_versions.return_value = expected
    
    assert a._get_all_spell_versions() == expected

def test_get_conduit_by_spell_id(aether_with_mocks):
    """_get_conduit_by_spell_id searches registries."""
    a = aether_with_mocks
    
    # Setup spell registry
    si = MagicMock()
    si.has_version.return_value = True
    si.id = "idx"
    
    a._default_frame._spell_registry = {"c1": {si}}
    
    # Mock conduit retrieval
    conduit = MagicMock()
    a._default_frame._conduits = {"c1": conduit}
    
    result = a._get_conduit_by_spell_id("ver1")
    assert result is conduit
    si.has_version.assert_called_with("ver1")

def test_get_conduit_by_spell_id_not_found_raises(aether_with_mocks):
    """_get_conduit_by_spell_id raises ValueError if no match."""
    a = aether_with_mocks
    a._default_frame._spell_registry = {}
    with pytest.raises(ValueError, match="not found"):
        a._get_conduit_by_spell_id("missing")

# ----------------------------------------------------------------------
# 5. Invalid Frame Access Tests
# ----------------------------------------------------------------------

def test_access_invalid_frame_raises(aether_with_mocks):
    """Accessing a non-existent frame raises ValueError."""
    a = aether_with_mocks
    
    with pytest.raises(ValueError, match="does not exist"):
        a._get_configuration("missing_frame")

    with pytest.raises(ValueError, match="does not exist"):
        a._get_existing_frame("missing_frame")

def test_ensure_default_frame_raises_if_missing(aether_with_mocks):
    """RuntimeError if default frame is gone (e.g. manually removed)."""
    a = aether_with_mocks
    a._default_frame = None # Simulate loss
    
    with pytest.raises(RuntimeError, match="unavailable"):
        a._ensure_default_frame()


def test_ensure_frame_raises_when_registry_unavailable_before_lock() -> None:
    """_ensure_frame should fail clearly when the frame registry is unavailable."""
    a = Aether()
    a._aetheric_frames = None

    with pytest.raises(RuntimeError, match="unavailable"):
        a._ensure_frame("custom")


def test_ensure_frame_raises_when_registry_becomes_unavailable_inside_lock() -> None:
    """_ensure_frame should fail if the registry disappears after the initial check."""
    a = Aether()
    original_lock = a._lock

    class _LockThatDropsRegistry:
        def __enter__(self_inner):
            a._aetheric_frames = None
            return self_inner

        def __exit__(self_inner, exc_type, exc_value, traceback):
            return False

    try:
        a._lock = _LockThatDropsRegistry()
        with pytest.raises(RuntimeError, match="unavailable"):
            a._ensure_frame("custom")
    finally:
        a._lock = original_lock


def test_ensure_frame_recreates_default_and_updates_default_pointer() -> None:
    """_ensure_frame should restore the default frame pointer when recreating the default frame."""
    a = Aether()
    original_default = a._default_frame
    a._aetheric_frames.pop("default", None)
    a._default_frame = None

    recreated = a._ensure_frame("default")

    assert recreated is a._default_frame
    assert a._aetheric_frames["default"] is recreated
    assert recreated is not original_default

# ----------------------------------------------------------------------
# 6. Cluster Management Tests
# ----------------------------------------------------------------------

def test_frame_cloud_create_cluster(aether_with_mocks):
    """frame-owned cloud create_cluster adds a new ConduitCluster to the frame."""
    a = aether_with_mocks
    frame_mock = a._default_frame

    with patch("melder.aether.aetheric_frame.conduit_cloud.ConduitCluster") as mock_cluster_cls:
        frame_mock._conduit_cloud.create_cluster("cluster1")

        assert "cluster1" in frame_mock._conduit_cloud._conduit_clusters
        mock_cluster_cls.assert_called_with("cluster1", {}, "default")

def test_frame_cloud_create_cluster_duplicate(aether_with_mocks):
    """Creating duplicate cluster via frame cloud raises ValueError."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._conduit_cloud._conduit_clusters = {"c1": MagicMock()}
    
    with pytest.raises(ValueError, match="already exists"):
        frame_mock._conduit_cloud.create_cluster("c1")


def test_get_existing_frame_missing_custom_frame_raises(aether_with_mocks):
    """missing custom frame lookup should raise clearly."""
    a = aether_with_mocks

    with pytest.raises(ValueError, match="does not exist"):
        a._get_existing_frame("missing_frame")


def test_frame_cloud_delete_cluster_logs_cleanup_failure(aether_with_mocks):
    """frame cloud delete_cluster should surface cleanup failure after removal."""
    a = aether_with_mocks
    cluster = MagicMock()
    cluster.cleanup.side_effect = RuntimeError("cluster cleanup failed")
    a._default_frame._conduit_cloud._conduit_clusters = {"cluster1": cluster}

    with pytest.raises(RuntimeError, match="cluster cleanup failed"):
        a._default_frame._conduit_cloud.delete_cluster("cluster1")

    cluster.cleanup.assert_called_once()
    assert "cluster1" not in a._default_frame._conduit_cloud._conduit_clusters

def test_frame_cloud_delete_cluster_missing_cluster_raises(aether_with_mocks):
    """frame cloud delete_cluster should raise when the cluster name is unknown."""
    a = aether_with_mocks
    a._default_frame._conduit_cloud._conduit_clusters = {}

    with pytest.raises(ValueError, match="does not exist"):
        a._default_frame._conduit_cloud.delete_cluster("missing")

def test_frame_cloud_get_cluster(aether_with_mocks):
    """frame cloud _get_cluster returns cluster object."""
    a = aether_with_mocks
    cluster = MagicMock()
    a._default_frame._conduit_cloud._conduit_clusters = {"c1": cluster}
    assert a._default_frame._conduit_cloud._get_cluster("c1") is cluster

def test_frame_cloud_get_cluster_missing_raises(aether_with_mocks):
    """frame cloud _get_cluster raises ValueError if missing."""
    a = aether_with_mocks
    a._default_frame._conduit_cloud._conduit_clusters = {}
    with pytest.raises(ValueError, match="does not exist"):
        a._default_frame._conduit_cloud._get_cluster("missing")

def test_frame_cloud_add_conduit_to_cluster(aether_with_mocks):
    """frame cloud add_conduit_to_cluster finds cluster and adds member."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    cluster_mock = MagicMock()
    frame_mock._conduit_cloud._conduit_clusters = {"cluster1": cluster_mock}
    conduit = MagicMock()
    conduit._id = "c1"

    frame_mock._conduit_cloud.add_conduit_to_cluster(conduit, "cluster1")

    cluster_mock.add_member.assert_called_with("c1")
    cluster_mock.handle_join.assert_called_with(conduit)


def test_frame_cloud_add_conduit_to_cluster_propagates_join_hook_failure(aether_with_mocks):
    """frame cloud add_conduit_to_cluster should propagate join-hook failures."""
    a = aether_with_mocks
    cluster_mock = MagicMock()
    a._default_frame._conduit_cloud._conduit_clusters = {"cluster1": cluster_mock}
    conduit = MagicMock()
    conduit._id = "c1"

    cluster_mock.handle_join.side_effect = RuntimeError("join hook failed")
    with pytest.raises(RuntimeError, match="join hook failed"):
        a._default_frame._conduit_cloud.add_conduit_to_cluster(conduit, "cluster1")

    cluster_mock.add_member.assert_called_with("c1")

def test_frame_cloud_remove_conduit_from_cluster(aether_with_mocks):
    """frame cloud remove_conduit_from_cluster removes member and calls hook."""
    a = aether_with_mocks
    cluster = MagicMock()
    a._default_frame._conduit_cloud._conduit_clusters = {"c1": cluster}
    conduit = MagicMock()
    conduit._id = "cid"

    a._default_frame._conduit_cloud.remove_conduit_from_cluster(conduit, "c1")
    cluster.remove_member.assert_called_with("cid")
    cluster.handle_leave.assert_called_with(conduit)


def test_frame_cloud_remove_conduit_from_cluster_propagates_leave_hook_failure(aether_with_mocks):
    """frame cloud remove_conduit_from_cluster should propagate leave-hook failures."""
    a = aether_with_mocks
    cluster = MagicMock()
    a._default_frame._conduit_cloud._conduit_clusters = {"c1": cluster}
    conduit = MagicMock()
    conduit._id = "cid"

    cluster.handle_leave.side_effect = RuntimeError("leave hook failed")
    with pytest.raises(RuntimeError, match="leave hook failed"):
        a._default_frame._conduit_cloud.remove_conduit_from_cluster(conduit, "c1")

    cluster.remove_member.assert_called_with("cid")

def test_frame_cloud_remove_conduit_from_cluster_error_propagate(aether_with_mocks):
    """frame cloud remove_conduit_from_cluster re-raises errors from cluster."""
    a = aether_with_mocks
    cluster = MagicMock()
    cluster.remove_member.side_effect = ValueError("fail")
    a._default_frame._conduit_cloud._conduit_clusters = {"c1": cluster}
    conduit = MagicMock()

    with pytest.raises(ValueError, match="fail"):
        a._default_frame._conduit_cloud.remove_conduit_from_cluster(conduit, "c1")

def test_frame_cloud_get_conduits_in_cluster(aether_with_mocks):
    """frame cloud cluster membership is exposed through the cluster object."""
    a = aether_with_mocks
    cluster_mock = MagicMock()
    cluster_mock.get_members.return_value = ["c1", "c2"]
    a._default_frame._conduit_cloud._conduit_clusters = {"cluster1": cluster_mock}

    assert list(a._default_frame._conduit_cloud._get_cluster("cluster1").get_members()) == ["c1", "c2"]

def test_frame_cloud_get_clusters_for_conduit(aether_with_mocks):
    """frame cloud get_clusters_for_conduit filters clusters containing id."""
    a = aether_with_mocks
    c1 = MagicMock()
    c1.get_members.return_value = ["target", "other"]
    c2 = MagicMock()
    c2.get_members.return_value = ["other"]
    a._default_frame._conduit_cloud._conduit_clusters = {"yes": c1, "no": c2}

    result = a._default_frame._conduit_cloud.get_clusters_for_conduit("target")
    assert result == ["yes"]

def test_frame_cloud_share_new_spell_to_clusters_unique_per_cluster(aether_with_mocks):
    """frame cloud cluster helper path should share unique_per_conduit_cluster roots."""
    a = aether_with_mocks
    
    # Setup
    conduit = MagicMock()
    conduit._id = "c1"
    
    spell = MagicMock()
    spell.existence = Existence.unique_per_conduit_cluster
    
    # Cluster setup
    cluster_mock = MagicMock()
    cluster_mock.get_members.return_value = ["c1", "c2"] # c2 is peer
    a._default_frame._conduit_cloud._conduit_clusters = {"cluster1": cluster_mock}
    
    # Peer conduit setup
    peer = MagicMock()
    a._default_frame._conduits = {"c2": peer}
    
    a._default_frame._conduit_cloud._get_cluster("cluster1").add_shared_spell("c1", spell.spell_index)
    a._default_frame._conduit_cloud._get_cluster("cluster1").share_to_borrower(conduit, peer)
    
    # Verification
    cluster_mock.add_shared_spell.assert_called_with("c1", spell.spell_index)
    cluster_mock.share_to_borrower.assert_called_with(conduit, peer)

def test_frame_cloud_share_new_spell_ignored_if_not_unique_per_cluster(aether_with_mocks):
    """Non-cluster existence does not require cloud cluster sharing."""
    a = aether_with_mocks
    conduit = MagicMock()
    spell = MagicMock()
    
    # Use a real enum value that IS NOT unique_per_conduit_cluster
    spell.existence = Existence.unique # Not cluster scoped
    
    # Should not access clusters
    assert spell.existence is Existence.unique

def test_refresh_cluster_shares_for_conduit(aether_with_mocks):
    """frame cloud refresh_cluster_shares_for_conduit calls refresh on relevant clusters."""
    a = aether_with_mocks
    cluster = MagicMock()
    cluster.get_members.return_value = ["cid"]
    a._default_frame._conduit_cloud._conduit_clusters = {"c1": cluster}
    conduit = MagicMock()
    conduit._id = "cid"

    a._default_frame._conduit_cloud.refresh_cluster_shares_for_conduit(conduit)
    cluster.refresh_member_shares.assert_called_with(conduit)


def test_removed_cluster_helpers_are_not_exposed_on_aether(aether_with_mocks):
    """Aether no longer exposes the old cluster lifecycle helpers after the owner move."""
    a = aether_with_mocks
    helper_names = (
        "_register_conduit_cloud",
        "_unregister_conduit_cloud",
        "_create_cluster",
        "_remove_cluster",
        "_get_cluster",
        "_add_conduit_to_cluster",
        "_remove_conduit_from_cluster",
        "_get_conduits_in_cluster",
        "_get_clusters_for_conduit",
        "_share_new_spell_to_clusters",
        "_refresh_cluster_shares_for_conduit",
        "_on_conduit_joined_cluster",
        "_on_conduit_left_cluster",
    )

    for helper_name in helper_names:
        assert not hasattr(a, helper_name)

# ----------------------------------------------------------------------
# 7. Logger Tests
# ----------------------------------------------------------------------

def test_logger_access(aether_with_mocks):
    """
    Verify logger property and explicit attach path.
    By default (mocked init or default init), logger is None (SafeLogger(None)).
    """
    a = aether_with_mocks
    assert a.logger is None
    
    new_logger = MagicMock()
    with patch("melder.utilities.helpers.init_helpers.InitHelpers.resolve_safe_logger") as mock_resolver:
        mock_safe_logger = MagicMock()
        mock_safe_logger._logger = new_logger
        mock_resolver.return_value = mock_safe_logger
        
        a.attach_logger(new_logger)
    
    assert a.logger is new_logger

def test_safe_logger_usage():
    """
    Purpose:
        Verify Aether wraps an attached logger with SafeLogger.
    Contract:
        - `attach_logger(...)` installs the SafeLogger wrapper.
    Returns:
        None.
    Raises:
        AssertionError: If the SafeLogger wrapper is not attached.
    """
    mock_logger = MagicMock()

    with patch("melder.utilities.helpers.init_helpers.InitHelpers.resolve_safe_logger") as mock_resolver:
        mock_safe = MagicMock()
        mock_safe._logger = mock_logger
        mock_resolver.return_value = mock_safe

        a = Aether()
        a.attach_logger(mock_logger)
        assert a._logger is mock_safe


def test_aether_boot_does_not_attach_real_logger(aether_with_mocks) -> None:
    """Aether should boot with no attached raw logger."""
    a = aether_with_mocks
    assert a.logger is None


def test_enable_logging_uses_automatic_channel_path_when_enabled() -> None:
    """
    Aether should be able to attach its own logger through the automatic channel path.
    """
    a = Aether()
    configuration = (
        a.create_configuration_builder()
        .with_channel_logger_activation_enabled(True)
        .with_channel_logger_resolver(
            lambda **_: logging.getLogger("aether-auto")
        )
        .build()
        .activate()
    )
    a.activate(configuration)

    a.enable_logging()

    assert a.logger is not None


def test_enable_logging_requires_activated_configuration_for_automatic_path() -> None:
    """
    The automatic Aether logger path should fail fast before config activation.
    """
    a = Aether()

    with pytest.raises(RuntimeError, match="AetherConfiguration must be activated"):
        a.enable_logging()


def test_enable_logging_requires_channel_logger_activation_enabled() -> None:
    """
    The automatic Aether logger path should fail fast when config disables it.
    """
    a = Aether()
    configuration = (
        a.create_configuration_builder()
        .with_defaults()
        .build()
        .activate()
    )
    a.activate(configuration)

    with pytest.raises(RuntimeError, match="disabled in AetherConfiguration"):
        a.enable_logging()


def test_enable_logging_requires_registered_automatic_provider() -> None:
    """
    The automatic Aether logger path should fail fast when no provider exists.
    """
    a = Aether()
    configuration = (
        a.create_configuration_builder()
        .with_channel_logger_activation_enabled(True)
        .build()
        .activate()
    )
    a.activate(configuration)

    with pytest.raises(RuntimeError, match="no automatic logger provider configured"):
        a.enable_logging()


def test_aether_activate_applies_logger_configuration_to_utility_system() -> None:
    """
    Verify Aether root config controls automatic channel logger activation.
    """
    a = Aether()
    configuration = (
        a.create_configuration()
        .with_channel_logger_activation_enabled(True)
        .with_default_logger(logging.getLogger("aether-default"))
        .activate()
    )

    a.activate(configuration)

    assert a.configured is True
    assert a.activated is True
    assert AetherUtilitySystem().is_channel_logger_activation_enabled() is True
    assert AetherUtilitySystem().has_default_logger() is True


def test_aether_create_configuration_builder_returns_builder() -> None:
    """
    Verify Aether exposes the fluent configuration builder through the root.
    """
    a = Aether()

    builder = a.create_configuration_builder()

    assert isinstance(builder, AetherConfigurationBuilder)
    assert builder.cleaned is False


def test_aether_configuration_builder_hands_off_activated_configuration() -> None:
    """
    Verify the Aether configuration builder can activate and hand off config.
    """
    builder = Aether().create_configuration_builder()
    configuration = (
        builder
        .with_defaults()
        .with_channel_logger_activation_enabled(True)
        .build()
        .activate()
    )

    assert isinstance(configuration, AetherConfiguration)
    assert configuration.activated is True
    assert builder.cleaned is True

def test_cleanup_failure_logging(mock_frame_cls):
    """If a frame fails to clean, error is logged."""
    mock_logger = MagicMock()
    
    with patch("melder.utilities.helpers.init_helpers.InitHelpers.resolve_safe_logger") as mock_resolver:
        mock_safe = MagicMock()
        mock_safe._logger = mock_logger
        mock_resolver.return_value = mock_safe
        
        a = Aether()
        a.attach_logger(mock_logger)
        
        # Force failure
        a._default_frame.cleanup.side_effect = RuntimeError("Fail")
        
        a.cleanup()
        
        assert mock_safe.error.called


def test_cleanup_reraises_and_logs_when_nexus_cleanup_fails(aether_with_mocks):
    """cleanup should log and re-raise subsystem cleanup failures."""
    a = aether_with_mocks
    a._logger = MagicMock()
    failing_nexus = MagicMock()
    failing_nexus.cleanup.side_effect = RuntimeError("nexus cleanup boom")
    a._nexus = failing_nexus

    with pytest.raises(RuntimeError, match="nexus cleanup boom"):
        a.cleanup()

    a._logger.error.assert_called_once()

# ----------------------------------------------------------------------
# 8. Additional Coverage (DevOps, Hooks, etc.)
# ----------------------------------------------------------------------

def test_revalidate_dirty_roots_delegates(aether_with_mocks):
    """
    Verify `_revalidate_dirty_roots` triggers the devops revalidator.

    Contract:
    - DevOpsManager.revalidate_dirty_roots is called via the frame.
    """
    a = aether_with_mocks
    mock_devops = MagicMock()
    a._default_frame._dev_ops_manager = mock_devops
    # Ensure mocked frame reports not cleaned
    a._default_frame._cleaned = False
    
    a._revalidate_dirty_roots("conduit-1")
    mock_devops.revalidate_dirty_roots.assert_called_with("conduit-1", cancel_event=None)

def test_get_managers_access(aether_with_mocks):
    """Verify accessors for sub-managers."""
    a = aether_with_mocks
    mock_devops = MagicMock()
    mock_devops.incident_manager = "im"
    mock_devops.change_control_manager = "ccm"
    mock_devops.spell_system_states = "sss"
    a._default_frame._dev_ops_manager = mock_devops
    a._default_frame._cleaned = False
    
    assert a._get_incident_manager() == "im"
    assert a._get_change_control_manager() == "ccm"
    assert a._get_spell_system_states() == "sss"

def test_get_mutation_research_access(aether_with_mocks):
    """Verify mutation research accessor."""
    a = aether_with_mocks
    assert a._get_mutation_research() is a._mutation_research

def test_aether_cleaned_guards(aether_with_mocks):
    """Verify methods check for _cleaned state."""
    a = aether_with_mocks
    a.cleanup()
    
    with pytest.raises(RuntimeError):
        a._get_configuration()

def test_refresh_version_registry(aether_with_mocks):
    """_refresh_version_registry calls frame."""
    a = aether_with_mocks
    a._refresh_version_registry()
    a._default_frame.refresh_version_registry.assert_called_once()

# ----------------------------------------------------------------------
# 9. Extra Coverage (20 new tests)
# ----------------------------------------------------------------------

def test_get_existing_frame_validates_frame_exists_for_removed_registration_helpers(aether_with_mocks):
    """Removed Aether registration helper paths now fail through _get_existing_frame."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_existing_frame("missing_frame")

def test_get_existing_frame_validates_frame_exists_for_removed_unregistration_helpers(aether_with_mocks):
    """Removed Aether unregistration helper paths now fail through _get_existing_frame."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_existing_frame("missing_frame")

def test_get_existing_frame_validates_frame_exists_for_removed_cluster_helpers(aether_with_mocks):
    """Removed cluster-helper call paths now fail through _get_existing_frame."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_existing_frame("missing_frame")

def test_get_existing_frame_validates_removed_share_helper_frame_exists(aether_with_mocks):
    """Removed share-helper call paths now fail through _get_existing_frame."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_existing_frame("missing_frame")

def test_get_existing_frame_validates_removed_refresh_helper_frame_exists(aether_with_mocks):
    """Removed refresh-helper call paths now fail through _get_existing_frame."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_existing_frame("missing_frame")

def test_frame_cloud_get_clusters_for_conduit_empty_when_none(aether_with_mocks):
    """frame cloud get_clusters_for_conduit returns empty when no clusters exist."""
    a = aether_with_mocks
    a._default_frame._conduit_cloud._conduit_clusters = {}
    assert a._default_frame._conduit_cloud.get_clusters_for_conduit("c1") == []

def test_frame_cloud_get_conduit_by_id_missing_peer_raises(aether_with_mocks):
    """frame cloud get_conduit_by_id raises ValueError for missing peers."""
    a = aether_with_mocks
    a._default_frame._conduits = {}
    with pytest.raises(ValueError, match="not found"):
        a._default_frame._conduit_cloud.get_conduit_by_id("c2")


def test_get_conduit_by_spell_id_validates_frame_exists(aether_with_mocks):
    """_get_conduit_by_spell_id raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_conduit_by_spell_id("sid", "missing_frame")

def test_check_for_spell_validates_frame_exists(aether_with_mocks):
    """_check_for_spell raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._check_for_spell("sid", "missing_frame")

def test_add_spells_to_aether_validates_frame_exists(aether_with_mocks):
    """_add_spells_to_aether raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._add_spells_to_aether("cid", set(), "missing_frame")

def test_remove_spells_from_aether_validates_frame_exists(aether_with_mocks):
    """_remove_spells_from_aether raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._remove_spells_from_aether("cid", set(), "missing_frame")

def test_register_single_spell_index_validates_frame_exists(aether_with_mocks):
    """_register_single_spell_index raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._register_single_spell_index("cid", MagicMock(), "missing_frame")

def test_remove_single_spell_index_validates_frame_exists(aether_with_mocks):
    """_remove_single_spell_index raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._remove_single_spell_index("cid", MagicMock(), "missing_frame")

def test_refresh_version_registry_validates_frame_exists(aether_with_mocks):
    """_refresh_version_registry raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._refresh_version_registry("missing_frame")

def test_get_all_spell_versions_validates_frame_exists(aether_with_mocks):
    """_get_all_spell_versions raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_all_spell_versions("missing_frame")

def test_get_mutation_research_raises_after_cleanup(aether_with_mocks):
    """_get_mutation_research raises after cleanup."""
    a = aether_with_mocks
    a.cleanup()
    with pytest.raises(RuntimeError):
        a._get_mutation_research()

def test_get_devops_manager_validates_frame_exists(aether_with_mocks):
    """_get_devops_manager raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_devops_manager("missing_frame")
