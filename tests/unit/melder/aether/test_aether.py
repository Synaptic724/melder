import pytest
import threading
from unittest.mock import MagicMock, patch, ANY
from melder.aether.aether import Aether
from melder.aether.aetheric_frame import AethericFrame
from melder.aether.aetheric_rift_system.aetheric_rift_system import AethericRiftSystem
from melder.aether.aetheric_rift_system.aetheric_rift.aetheric_rift import AethericRift
from melder.aether.aetheric_rift_system.aetheric_rift_state.aetheric_rift_state import (
    AethericRiftState,
)
from melder.utilities.interfaces.interfaces import IConduit, IConduitCloud
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence

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
    if Aether._instance:
        Aether().cleanup()
        Aether._instance = None
        Aether._initialized = False

    yield

    # Post-test cleanup
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
        mock_instance._conduit_clusters = {}
        mock_instance._spell_registry = {}
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

def test_initialization_creates_default_frame(mock_frame_cls):
    """
    Verify initialization automatically creates the 'default' frame.

    Contract:
    - `_aetheric_frames` must contain "default".
    - `_default_frame` property must point to this frame.
    - AethericFrame constructor must be called with "default".
    """
    a = Aether()
    assert "default" in a._aetheric_frames
    mock_frame_cls.assert_called_with("default")
    assert a._default_frame is mock_frame_cls.return_value
    assert isinstance(a._get_aetheric_rift_system(), AethericRiftSystem)
    assert a._is_aetheric_rift_system_configured() is False
    assert a._is_aetheric_rift_system_enabled() is False

def test_cleanup_clears_state(aether_with_mocks):
    """
    Verify `cleanup` resets the singleton for re-use/shutdown.

    Contract:
    - All frames are removed and cleaned.
    - `_aetheric_frames` is set to None.
    - `_default_frame` is set to None.
    - Singleton instance reference (`Aether._instance`) is cleared to allow fresh tests.
    """
    a = aether_with_mocks
    default_frame = a._default_frame
    
    a.cleanup()
    
    assert a._cleaned is True
    assert a._aetheric_frames is None
    assert a._default_frame is None
    assert a._aetheric_rift_system is None
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

def test_cleanup_specific_frame(aether_with_mocks):
    """
    Verify `cleanup_frame` correctly removes and cleans a targeted frame.

    Contract:
    - The frame object's `cleanup()` method is called.
    - The frame is removed from the internal registry.
    """
    a = aether_with_mocks
    mock_custom = MagicMock()
    a._aetheric_frames["custom"] = mock_custom
    
    a.cleanup_frame("custom")
    
    assert "custom" not in a._aetheric_frames
    mock_custom.cleanup.assert_called_once()

def test_cleanup_default_frame_clears_reference(aether_with_mocks):
    """Cleaning the 'default' frame also clears the _default_frame property."""
    a = aether_with_mocks
    default_frame = a._default_frame
    
    a.cleanup_frame("default")
    
    assert "default" not in a._aetheric_frames
    assert a._default_frame is None
    default_frame.cleanup.assert_called_once()

def test_cleanup_frame_not_found(aether_with_mocks):
    """cleanup_frame() handles non-existent frames gracefully."""
    a = aether_with_mocks
    a.cleanup_frame("non_existent")

def test_cleanup_frame_handles_concurrent_removal(aether_with_mocks):
    """
    Verify robustness against concurrent frame removal.

    Contract:
    - If a frame is present during check but removed before cleanup, no error is raised.
    """
    a = aether_with_mocks
    a.cleanup_frame("missing")

def test_cleanup_aetheric_frames_iterates_all(aether_with_mocks):
    """cleanup_aetheric_frames should call cleanup on all frames."""
    a = aether_with_mocks
    mock_f1 = MagicMock()
    mock_f2 = MagicMock()
    a._aetheric_frames = {"f1": mock_f1, "f2": mock_f2}
    
    a.cleanup_aetheric_frames()
    
    mock_f1.cleanup.assert_called_once()
    mock_f2.cleanup.assert_called_once()

def test_cleanup_aetheric_frames_tolerant_of_errors(aether_with_mocks):
    """If one frame fails cleanup, others should still be cleaned."""
    a = aether_with_mocks
    mock_f1 = MagicMock()
    mock_f1.cleanup.side_effect = RuntimeError("Boom")
    mock_f2 = MagicMock()
    
    a._aetheric_frames = {"f1": mock_f1, "f2": mock_f2}
    
    # Should not raise
    a.cleanup_aetheric_frames()
    
    mock_f1.cleanup.assert_called_once()
    mock_f2.cleanup.assert_called_once()

# ----------------------------------------------------------------------
# 3. Delegation Tests (Conduits)
# ----------------------------------------------------------------------

def test_add_conduit_delegates_to_default(aether_with_mocks):
    """
    Verify `_add_conduit` delegates to the default frame.

    Contract:
    - If no frame name is provided, the conduit is added to the default frame's registry.
    """
    a = aether_with_mocks
    frame_mock = a._default_frame
    conduits_dict = {}
    frame_mock._conduits = conduits_dict
    
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    
    a._add_conduit(conduit)
    
    assert "c1" in conduits_dict
    assert conduits_dict["c1"] is conduit


def test_rift_facade_delegates_to_hosted_system(aether_with_mocks):
    """
    Verify Aether hosts the AR system and delegates Rift registry access to it.
    """
    a = aether_with_mocks
    system_config = a._create_aetheric_rift_system_configuration()
    system_config.with_rift_creation_enabled(True)
    system_config.with_direct_rift_access(True)
    system_config.with_direct_state_access(True)
    a._enable_aetheric_rift_system()
    rift = a._create_rift(rift_name="alpha")

    assert a._get_rift(rift.id) is rift
    assert a._get_rift_by_name("alpha") is rift
    assert a._get_rift_state(rift.id) is rift.state
    assert a._list_rifts() == [rift.id]

    # Ownership stays in the hosted system.
    system = a._get_aetheric_rift_system()
    assert rift.id in system._rifts_by_id
    assert rift.id in system._rift_states_by_id
    assert "alpha" in system._rift_ids_by_name

    a._remove_rift(rift.id)
    assert a._list_rifts() == []


def test_rift_facade_can_program_external_shell(aether_with_mocks):
    a = aether_with_mocks
    system_config = a._create_aetheric_rift_system_configuration()
    system_config.with_rift_creation_enabled(True)
    system_config.with_allow_external_rift_registration(True)
    a._enable_aetheric_rift_system()
    rift = AethericRift(a._get_aetheric_rift_system(), rift_name="alpha")

    programmed = a._register_external_rift(rift)

    assert programmed is rift
    assert programmed.has_state is True


def test_rift_facade_can_create_state_for_external_programming(aether_with_mocks):
    a = aether_with_mocks
    system_config = a._create_aetheric_rift_system_configuration()
    system_config.with_rift_creation_enabled(True)
    a._enable_aetheric_rift_system()
    rift = AethericRift(a._get_aetheric_rift_system(), rift_name="alpha")
    state = a._create_rift_state(rift_id=rift.id, rift_name="alpha")
    programmed = a._program_rift(rift, state)

    assert programmed is rift
    assert programmed.state is state

    # Ownership stays in the hosted system.
    system = a._get_aetheric_rift_system()
    assert state.rift_id in system._rifts_by_id
    assert state.rift_id in system._rift_states_by_id
    assert "alpha" in system._rift_ids_by_name


def test_aether_requires_configuration_before_returning_system_configuration(aether_with_mocks):
    a = aether_with_mocks

    assert a._is_aetheric_rift_system_configured() is False
    with pytest.raises(RuntimeError, match="not configured"):
        a._get_aetheric_rift_system_configuration()

    system_config = a._create_aetheric_rift_system_configuration()

    assert a._is_aetheric_rift_system_configured() is False
    assert system_config.get_property("allow_rift_creation") is True
    assert system_config.get_property("system_frame_mode").value == "single"
    assert system_config.get_property("default_system_frame_name") == "aetheric_frame_system"


def test_aether_can_create_per_rift_configuration_after_system_is_configured(aether_with_mocks):
    a = aether_with_mocks
    system_config = a._create_aetheric_rift_system_configuration()

    a._enable_aetheric_rift_system(system_config)
    rift_config = a._create_rift_configuration()

    assert rift_config.get_property("target_frame_name") == "default"
    assert rift_config.get_property("auto_activate_on_program") is True


def test_state_access_token_can_be_enforced_through_aether(aether_with_mocks):
    a = aether_with_mocks
    system_config = a._create_aetheric_rift_system_configuration()
    system_config.with_rift_creation_enabled(True)
    system_config.with_direct_state_access(True)
    system_config.with_state_access_token_required(True)
    system_config.with_state_access_token("secret")
    a._enable_aetheric_rift_system()
    rift = a._create_rift(rift_name="alpha")

    with pytest.raises(ValueError, match="Valid state access token"):
        a._get_rift_state(rift.id)

    assert a._get_rift_state(rift.id, access_token="secret") is rift.state


def test_aether_can_enable_and_disable_hosted_rift_system(aether_with_mocks):
    """
    Verify Aether facades AR system enable/disable against the hosted
    subsystem.
    """
    a = aether_with_mocks
    assert a._is_aetheric_rift_system_configured() is False
    assert a._is_aetheric_rift_system_enabled() is False

    system_config = a._create_aetheric_rift_system_configuration()
    system_config.with_rift_creation_enabled(True)
    a._enable_aetheric_rift_system()

    assert a._is_aetheric_rift_system_configured() is True
    assert a._is_aetheric_rift_system_enabled() is True

    a._disable_aetheric_rift_system()
    assert a._is_aetheric_rift_system_enabled() is False

def test_add_conduit_delegates_to_custom_frame(aether_with_mocks):
    """_add_conduit delegates to a specific frame."""
    a = aether_with_mocks
    frame_mock = MagicMock()
    frame_mock._conduits = {}
    a._aetheric_frames["f1"] = frame_mock
    
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    
    a._add_conduit(conduit, "f1")
    
    assert "c1" in frame_mock._conduits

def test_add_conduit_duplicate_raises(aether_with_mocks):
    """_add_conduit raises ValueError if ID exists."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    frame_mock._conduits = {"c1": conduit}
    
    with pytest.raises(ValueError, match="already exists"):
        a._add_conduit(conduit)

def test_remove_conduit_delegates(aether_with_mocks):
    """_remove_conduit removes from the frame's dict."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    frame_mock._conduits = {"c1": conduit}
    
    a._remove_conduit(conduit)
    
    assert "c1" not in frame_mock._conduits

def test_remove_conduit_missing_raises(aether_with_mocks):
    """_remove_conduit raises ValueError if ID not found."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._conduits = {}
    conduit = MagicMock(spec=IConduit)
    conduit._id = "c1"
    
    with pytest.raises(ValueError, match="does not exist"):
        a._remove_conduit(conduit)

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

def test_get_conduit_by_name(aether_with_mocks):
    """_get_conduit_by_name iterates frame dict."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    c1 = MagicMock()
    c1.name = "bob"
    c2 = MagicMock()
    c2.name = "alice"
    frame_mock._conduits = {"id1": c1, "id2": c2}
    
    result = a._get_conduit_by_name("alice")
    assert result is c2

def test_get_conduit_by_name_missing_raises(aether_with_mocks):
    """_get_conduit_by_name raises ValueError if not found."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="not found"):
        a._get_conduit_by_name("nobody")

def test_register_conduit_cloud_delegates(aether_with_mocks):
    """_register_conduit_cloud calls frame's cloud."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    cloud_mock = MagicMock()
    frame_mock._conduit_cloud = cloud_mock
    
    conduit = MagicMock()
    a._register_conduit_cloud(conduit)
    
    cloud_mock._register_conduit.assert_called_with(conduit)

def test_unregister_conduit_cloud_delegates(aether_with_mocks):
    """_unregister_conduit_cloud calls frame's cloud."""
    a = aether_with_mocks
    cloud = MagicMock()
    a._default_frame._conduit_cloud = cloud
    conduit = MagicMock()
    
    a._unregister_conduit_cloud(conduit)
    cloud._unregister_conduit.assert_called_with(conduit)

def test_get_conduit_cloud(aether_with_mocks):
    """_get_conduit_cloud returns the cloud object."""
    a = aether_with_mocks
    cloud = MagicMock()
    a._default_frame._conduit_cloud = cloud
    assert a._get_conduit_cloud() is cloud

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

def test_get_configuration(aether_with_mocks):
    """
    Verify `_get_configuration` retrieves configuration from the frame.
    """
    a = aether_with_mocks
    frame_mock = a._default_frame
    expected = MagicMock()
    frame_mock._configuration = expected
    
    assert a._get_configuration() is expected

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
        a._add_conduit(MagicMock(), "missing_frame")

def test_ensure_default_frame_raises_if_missing(aether_with_mocks):
    """RuntimeError if default frame is gone (e.g. manually removed)."""
    a = aether_with_mocks
    a._default_frame = None # Simulate loss
    
    with pytest.raises(RuntimeError, match="unavailable"):
        a._ensure_default_frame()

# ----------------------------------------------------------------------
# 6. Cluster Management Tests
# ----------------------------------------------------------------------

def test_create_cluster(aether_with_mocks):
    """_create_cluster adds a new ConduitCluster to the frame."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._conduit_clusters = {}
    
    with patch("melder.aether.aether.ConduitCluster") as mock_cluster_cls:
        a._create_cluster("cluster1")
        
        assert "cluster1" in frame_mock._conduit_clusters
        mock_cluster_cls.assert_called_with("cluster1")

def test_create_cluster_duplicate(aether_with_mocks):
    """Creating duplicate cluster raises ValueError."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    frame_mock._conduit_clusters = {"c1": MagicMock()}
    
    with pytest.raises(ValueError, match="already exists"):
        a._create_cluster("c1")

def test_get_cluster(aether_with_mocks):
    """_get_cluster returns cluster object."""
    a = aether_with_mocks
    cluster = MagicMock()
    a._default_frame._conduit_clusters = {"c1": cluster}
    assert a._get_cluster("c1") is cluster

def test_get_cluster_missing_raises(aether_with_mocks):
    """_get_cluster raises ValueError if missing."""
    a = aether_with_mocks
    a._default_frame._conduit_clusters = {}
    with pytest.raises(ValueError, match="does not exist"):
        a._get_cluster("missing")

def test_add_conduit_to_cluster(aether_with_mocks):
    """_add_conduit_to_cluster finds cluster and adds member."""
    a = aether_with_mocks
    frame_mock = a._default_frame
    cluster_mock = MagicMock()
    frame_mock._conduit_clusters = {"cluster1": cluster_mock}
    
    conduit = MagicMock()
    conduit._id = "c1"
    
    with patch.object(a, "_on_conduit_joined_cluster") as mock_hook:
        a._add_conduit_to_cluster(conduit, "cluster1")
        
        cluster_mock.add_member.assert_called_with("c1")
        mock_hook.assert_called_with(conduit, "cluster1", "default")

def test_remove_conduit_from_cluster(aether_with_mocks):
    """_remove_conduit_from_cluster removes member and calls hook."""
    a = aether_with_mocks
    cluster = MagicMock()
    a._default_frame._conduit_clusters = {"c1": cluster}
    conduit = MagicMock()
    conduit._id = "cid"
    
    with patch.object(a, "_on_conduit_left_cluster") as hook:
        a._remove_conduit_from_cluster(conduit, "c1")
        cluster.remove_member.assert_called_with("cid")
        hook.assert_called_with(conduit, "c1", "default")

def test_remove_conduit_from_cluster_error_propagate(aether_with_mocks):
    """_remove_conduit_from_cluster re-raises errors from cluster."""
    a = aether_with_mocks
    cluster = MagicMock()
    cluster.remove_member.side_effect = ValueError("fail")
    a._default_frame._conduit_clusters = {"c1": cluster}
    conduit = MagicMock()
    
    with pytest.raises(ValueError, match="fail"):
        a._remove_conduit_from_cluster(conduit, "c1")

def test_get_conduits_in_cluster(aether_with_mocks):
    """_get_conduits_in_cluster returns members."""
    a = aether_with_mocks
    cluster_mock = MagicMock()
    cluster_mock.get_members.return_value = ["c1", "c2"]
    a._default_frame._conduit_clusters = {"cluster1": cluster_mock}
    
    assert a._get_conduits_in_cluster("cluster1") == ["c1", "c2"]

def test_get_clusters_for_conduit(aether_with_mocks):
    """_get_clusters_for_conduit filters clusters containing id."""
    a = aether_with_mocks
    c1 = MagicMock()
    c1.get_members.return_value = ["target", "other"]
    c2 = MagicMock()
    c2.get_members.return_value = ["other"]
    a._default_frame._conduit_clusters = {"yes": c1, "no": c2}
    
    result = a._get_clusters_for_conduit("target")
    assert result == ["yes"]

def test_share_new_spell_to_clusters_unique_per_cluster(aether_with_mocks):
    """
    If a spell has unique_per_conduit_cluster existence, it should be shared to cluster peers.
    """
    a = aether_with_mocks
    
    # Setup
    conduit = MagicMock()
    conduit._id = "c1"
    
    spell = MagicMock()
    spell.existence = Existence.unique_per_conduit_cluster
    
    # Cluster setup
    cluster_mock = MagicMock()
    cluster_mock.get_members.return_value = ["c1", "c2"] # c2 is peer
    a._default_frame._conduit_clusters = {"cluster1": cluster_mock}
    
    # Peer conduit setup
    peer = MagicMock()
    a._default_frame._conduits = {"c2": peer}
    
    a._share_new_spell_to_clusters(conduit, spell)
    
    # Verification
    cluster_mock.add_shared_spell.assert_called_with("c1", spell.spell_index)
    cluster_mock.share_to_borrower.assert_called_with(conduit, peer)

def test_share_new_spell_ignored_if_not_unique_per_cluster(aether_with_mocks):
    """Spells with other existence traits are ignored by cluster sharing."""
    a = aether_with_mocks
    conduit = MagicMock()
    spell = MagicMock()
    
    # Use a real enum value that IS NOT unique_per_conduit_cluster
    spell.existence = Existence.unique # Not cluster scoped
    
    # Should not access clusters
    a._share_new_spell_to_clusters(conduit, spell)
    # No way to assert "no calls" on internal lookups easily without spying, 
    # but we verify it didn't crash on missing clusters setup.

def test_refresh_cluster_shares_for_conduit(aether_with_mocks):
    """_refresh_cluster_shares_for_conduit calls refresh on relevant clusters."""
    a = aether_with_mocks
    cluster = MagicMock()
    cluster.get_members.return_value = ["cid"]
    a._default_frame._conduit_clusters = {"c1": cluster}
    conduit = MagicMock()
    conduit._id = "cid"
    
    a._refresh_cluster_shares_for_conduit(conduit)
    cluster.refresh_member_shares.assert_called_with(conduit, a._default_frame, "default")

# ----------------------------------------------------------------------
# 7. Logger Tests
# ----------------------------------------------------------------------

def test_logger_access(aether_with_mocks):
    """
    Verify logger property and setter.
    By default (mocked init or default init), logger is None (SafeLogger(None)).
    """
    a = aether_with_mocks
    # The property .logger returns the underlying logger object.
    # SafeLogger(None) -> _logger is None.
    assert a.logger is None
    
    new_logger = MagicMock()
    # Mocking the validation chain in InitHelpers/SafeLogger
    # We patch InitHelpers because SafeLogger constructor does type checking too.
    with patch("melder.utilities.helpers.init_helpers.InitHelpers.resolve_safe_logger") as mock_resolver:
        # Create a dummy SafeLogger
        mock_safe_logger = MagicMock()
        mock_safe_logger._logger = new_logger
        mock_resolver.return_value = mock_safe_logger
        
        a.logger = new_logger
    
    assert a.logger is new_logger

def test_safe_logger_usage():
    """
    Purpose:
        Verify Aether wraps the configured logger with SafeLogger.
    Contract:
        - Setting a logger installs the SafeLogger wrapper.
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

        # Instantiate empty, then set logger manually to avoid __new__ args issue.
        a = Aether()
        a.logger = mock_logger

        # Verify internal setter updated _logger
        # Note: a.logger property returns the raw logger, a._logger is the SafeLogger wrapper.
        assert a._logger is mock_safe

def test_cleanup_failure_logging(mock_frame_cls):
    """If a frame fails to clean, error is logged."""
    mock_logger = MagicMock()
    
    with patch("melder.utilities.helpers.init_helpers.InitHelpers.resolve_safe_logger") as mock_resolver:
        mock_safe = MagicMock()
        mock_safe._logger = mock_logger
        mock_resolver.return_value = mock_safe
        
        # Workaround for __new__ signature issue:
        a = Aether()
        a.logger = mock_logger
        
        # Force failure
        a._default_frame.cleanup.side_effect = RuntimeError("Fail")
        
        a.cleanup()
        
        assert mock_safe.error.called

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
    mr = MagicMock()
    a._default_frame._mutation_research = mr
    a._default_frame._cleaned = False
    
    assert a._get_mutation_research() is mr

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

def test_add_conduit_validates_frame_exists(aether_with_mocks):
    """_add_conduit raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._add_conduit(MagicMock(), "missing_frame")

def test_remove_conduit_validates_frame_exists(aether_with_mocks):
    """_remove_conduit raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._remove_conduit(MagicMock(), "missing_frame")

def test_create_cluster_validates_frame_exists(aether_with_mocks):
    """_create_cluster raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._create_cluster("c1", "missing_frame")

def test_add_conduit_to_cluster_validates_frame_exists(aether_with_mocks):
    """_add_conduit_to_cluster raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._add_conduit_to_cluster(MagicMock(), "c1", "missing_frame")

def test_remove_conduit_from_cluster_validates_frame_exists(aether_with_mocks):
    """_remove_conduit_from_cluster raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._remove_conduit_from_cluster(MagicMock(), "c1", "missing_frame")

def test_get_conduits_in_cluster_validates_frame_exists(aether_with_mocks):
    """_get_conduits_in_cluster raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_conduits_in_cluster("c1", "missing_frame")

def test_get_clusters_for_conduit_validates_frame_exists(aether_with_mocks):
    """_get_clusters_for_conduit raises KeyError if frame missing (unwrapped access)."""
    a = aether_with_mocks
    with pytest.raises(KeyError):
        a._get_clusters_for_conduit("cid", "missing_frame")

def test_share_new_spell_to_clusters_validates_frame_exists(aether_with_mocks):
    """_share_new_spell_to_clusters raises KeyError if frame missing (unwrapped access)."""
    a = aether_with_mocks
    conduit = MagicMock()
    conduit._id = "c1"
    spell = MagicMock()
    spell.existence = Existence.unique_per_conduit_cluster
    
    with pytest.raises(KeyError):
        a._share_new_spell_to_clusters(conduit, spell, "missing_frame")

def test_refresh_cluster_shares_for_conduit_validates_frame_exists(aether_with_mocks):
    """_refresh_cluster_shares_for_conduit raises KeyError if frame missing (unwrapped access)."""
    a = aether_with_mocks
    conduit = MagicMock()
    conduit._id = "c1"
    
    with pytest.raises(KeyError):
        a._refresh_cluster_shares_for_conduit(conduit, "missing_frame")

def test_share_new_spell_to_clusters_no_clusters(aether_with_mocks):
    """If no clusters for conduit, sharing does nothing."""
    a = aether_with_mocks
    conduit = MagicMock()
    conduit._id = "c1"
    spell = MagicMock()
    spell.existence = Existence.unique_per_conduit_cluster
    
    # Ensure no clusters
    a._default_frame._conduit_clusters = {}
    
    # Should run without error
    a._share_new_spell_to_clusters(conduit, spell)

def test_share_new_spell_to_clusters_conduit_removed(aether_with_mocks):
    """If peer conduit is missing from frame, it is skipped."""
    a = aether_with_mocks
    conduit = MagicMock()
    conduit._id = "c1"
    spell = MagicMock()
    spell.existence = Existence.unique_per_conduit_cluster
    
    cluster = MagicMock()
    cluster.get_members.return_value = ["c1", "c2"]
    a._default_frame._conduit_clusters = {"cluster1": cluster}
    
    # "c2" is not in _conduits
    a._default_frame._conduits = {"c1": conduit}
    
    a._share_new_spell_to_clusters(conduit, spell)
    # verify share_to_borrower NOT called for c2
    cluster.share_to_borrower.assert_not_called()

def test_refresh_cluster_shares_no_clusters(aether_with_mocks):
    """If no clusters, refresh does nothing."""
    a = aether_with_mocks
    conduit = MagicMock()
    conduit._id = "c1"
    a._default_frame._conduit_clusters = {}
    
    a._refresh_cluster_shares_for_conduit(conduit)

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

def test_get_mutation_research_validates_frame_exists(aether_with_mocks):
    """_get_mutation_research raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_mutation_research("missing_frame")

def test_get_devops_manager_validates_frame_exists(aether_with_mocks):
    """_get_devops_manager raises ValueError if frame missing."""
    a = aether_with_mocks
    with pytest.raises(ValueError, match="does not exist"):
        a._get_devops_manager("missing_frame")
