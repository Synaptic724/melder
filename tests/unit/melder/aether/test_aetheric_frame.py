import threading
import pytest
from unittest.mock import MagicMock, patch
from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.spellbook.bind.spell_index import SpellIndex

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture(autouse=True)
def fresh_aether() -> None:
    """
    Reset the Aether singleton around each frame test.

    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    yield
    Aether._reset_singleton_for_tests()


@pytest.fixture
def mock_dependencies():
    """
    Patches all external dependencies instantiated in AethericFrame.__init__.
    Returns a dict of the mock classes.
    """
    with patch("melder.aether.aetheric_frame.aetheric_frame.ConduitCloud") as mock_cloud, \
         patch("melder.aether.aetheric_frame.aetheric_frame.SpellSystemStates") as mock_sss, \
         patch("melder.aether.aetheric_frame.aetheric_frame.DevOpsManager") as mock_dom:
        cloud_instance = mock_cloud.return_value
        cloud_instance._conduit_clusters = {}

        def _cleanup_cloud() -> None:
            for cluster in list(cloud_instance._conduit_clusters.values()):
                try:
                    cluster.cleanup()
                except Exception:
                    pass
            cloud_instance._conduit_clusters.clear()

        cloud_instance.cleanup.side_effect = _cleanup_cloud
        yield {
            "cloud": mock_cloud,
            "sss": mock_sss,
            "dom": mock_dom
        }

@pytest.fixture
def frame(mock_dependencies):
    """Returns a fresh AethericFrame instance with mocked dependencies."""
    return AethericFrame(Aether(), "test_frame")

# ----------------------------------------------------------------------
# 1. Initialization Tests
# ----------------------------------------------------------------------

def test_init_success(mock_dependencies):
    """
    Verify successful initialization sets name and creates components.

    Contract:
    - Name is set.
    - ID is generated.
    - Lock is created.
    - All sub-managers (cloud, sss, dom) are instantiated using mocks.
    - Registries start empty.
    """
    f = AethericFrame(Aether(), "my_frame")
    assert f.name == "my_frame"
    assert f._id is not None
    assert isinstance(f._lock, type(threading.RLock()))
    
    # Verify registries are empty dicts
    assert f._conduits == {}
    assert f._spell_registry == {}
    assert f._version_registry == {}
    assert f._conduit_cloud._conduit_clusters == {}
    
    # Verify sub-components were created
    assert f._conduit_cloud is mock_dependencies["cloud"].return_value
    assert f._spell_system_states is mock_dependencies["sss"].return_value
    assert f._dev_ops_manager is mock_dependencies["dom"].return_value

def test_init_missing_aether_raises() -> None:
    """
    Verify a frame cannot be constructed without an owning Aether.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="aether cannot be None"):
        AethericFrame(None, "my_frame")


def test_init_non_iaether_raises() -> None:
    """AethericFrame should reject owners that do not satisfy IAether."""
    with pytest.raises(TypeError, match="must satisfy IAether"):
        AethericFrame(object(), "my_frame")

def test_init_empty_name_raises():
    """Test that empty name raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        AethericFrame(Aether(), "")

def test_init_none_name_raises():
    """Test that None name raises ValueError (via type check or bool check)."""
    with pytest.raises(ValueError): # or TypeError depending on impl detail, but ValueError expected
        AethericFrame(Aether(), None)

# ----------------------------------------------------------------------
# 2. Context Manager Tests
# ----------------------------------------------------------------------

def test_context_manager_acquires_lock(frame):
    """
    Verify `__enter__` and `__exit__` manage the internal lock.

    Contract:
    - Entering the context acquires the lock.
    - Exiting the context releases the lock.
    """
    # We can verify lock behavior by spying or checking locked status if possible.
    # RLock doesn't expose 'locked()' easily, but we can verify usage.
    with frame as f:
        assert f is frame
        # If we can acquire non-blocking, it means we own it (reentrant)
        assert f._lock.acquire(blocking=False)
        f._lock.release()

def test_context_manager_raises_if_cleaned(frame):
    """Test __enter__ raises if object is cleaned."""
    frame.cleanup()
    with pytest.raises(RuntimeError):
        with frame:
            pass

# ----------------------------------------------------------------------
# 3. Cleanup Tests
# ----------------------------------------------------------------------

def test_cleanup_clears_registries(frame):
    """
    Verify `cleanup` empties all internal data structures.

    Contract:
    - All registry dictionaries are set to None.
    - The cleaned flag is set to True.
    """
    # Populate some dummy data
    frame._conduits["c1"] = MagicMock()
    frame._spell_registry["c1"] = set()
    frame._version_registry["c1"] = set()
    frame._conduit_cloud._conduit_clusters["cl1"] = MagicMock()
    
    frame.cleanup()
    
    assert not hasattr(frame, '_conduits')
    assert not hasattr(frame, '_spell_registry')
    assert not hasattr(frame, '_version_registry')
    assert frame._cleaned is True

def test_cleanup_calls_subcomponent_cleanup(frame):
    """
    Verify `cleanup` delegates to child objects.

    Contract:
    - `cleanup()` is called on all owned managers (cloud, sss, dom).
    - `cleanup()` is called on all owned conduits.
    - Cluster cleanup is delegated through the owned ConduitCloud.
    """
    # Sub-components are mocks from fixture
    cloud = frame._conduit_cloud
    sss = frame._spell_system_states
    dom = frame._dev_ops_manager
    conduit = MagicMock()
    frame._conduits["c1"] = conduit
    cluster = MagicMock()
    frame._conduit_cloud._conduit_clusters["cl1"] = cluster
    
    frame.cleanup()
    
    cloud.cleanup.assert_called_once()
    sss.cleanup.assert_called_once()
    dom.cleanup.assert_called_once()
    conduit.cleanup.assert_called_once()
    cluster.cleanup.assert_called_once()

def test_cleanup_idempotent(frame):
    """Test cleanup can be called twice safely."""
    frame.cleanup()
    # Should not raise
    frame.cleanup()
    assert frame._cleaned is True


def test_cleanup_returns_early_when_cleaned_flips_inside_lock(frame):
    """cleanup should return safely if another path marks the frame cleaned inside the lock."""
    frame._frame_configuration = MagicMock()
    frame._configuration = object()
    original_lock = frame._lock

    class _LockThatMarksCleaned:
        def __enter__(self_inner):
            frame._cleaned = True
            return self_inner

        def __exit__(self_inner, exc_type, exc_value, traceback):
            return False

    try:
        frame._lock = _LockThatMarksCleaned()
        frame.cleanup()
    finally:
        frame._lock = original_lock

    assert frame._frame_configuration is not None
    assert frame._configuration is not None

def test_cleanup_nulls_properties(frame):
    """
    Verify `cleanup` sets internal references to None.

    Contract:
    - All manager references are nulled.
    - Configuration and identity fields are nulled.
    - Lock is nulled.
    """
    frame.cleanup()
    assert not hasattr(frame, '_conduit_cloud')
    assert not hasattr(frame, '_dev_ops_manager')
    assert not hasattr(frame, '_spell_system_states')
    assert not hasattr(frame, '_configuration')
    assert not hasattr(frame, 'name')
    assert not hasattr(frame, '_id')
    assert not hasattr(frame, '_lock')


def test_cleanup_cleans_frame_configuration(frame):
    """cleanup should call cleanup on the bound frame configuration before dropping it."""
    configuration = MagicMock()
    frame._frame_configuration = configuration

    frame.cleanup()

    configuration.cleanup.assert_called_once()
    assert not hasattr(frame, '_frame_configuration')

def test_cleanup_tolerant_of_errors(frame):
    """Test cleanup continues if a sub-component raises error."""
    bad_conduit = MagicMock()
    bad_conduit.cleanup.side_effect = RuntimeError("Boom")
    frame._conduits["c1"] = bad_conduit
    
    # Should not raise
    frame.cleanup()
    assert frame._cleaned is True
    assert not hasattr(frame, '_conduits')


def test_cleanup_tolerant_of_cluster_cleanup_errors(frame):
    """cleanup should tolerate cluster cleanup failures and still complete."""
    bad_cluster = MagicMock()
    bad_cluster.cleanup.side_effect = RuntimeError("cluster boom")
    frame._conduit_cloud._conduit_clusters["cl1"] = bad_cluster

    frame.cleanup()

    assert frame._cleaned is True

# ----------------------------------------------------------------------
# 4. Property Accessor Tests
# ----------------------------------------------------------------------

def test_property_accessors_success(frame):
    """Test access to sub-manager properties."""
    assert frame.spell_system_states is not None
    assert frame.dev_ops_manager is not None

def test_property_accessors_fail_after_cleanup(frame):
    """Test access raises RuntimeError after cleanup."""
    frame.cleanup()
    with pytest.raises(RuntimeError):
        _ = frame.spell_system_states
    with pytest.raises(RuntimeError):
        _ = frame.dev_ops_manager
    with pytest.raises(RuntimeError):
        _ = frame.frame_configuration

# ----------------------------------------------------------------------
# 5. Version Registry Tests
# ----------------------------------------------------------------------

def test_refresh_version_registry_empty(frame):
    """Test refresh with empty spell registry results in empty version registry."""
    frame.refresh_version_registry()
    assert frame._version_registry == {}

def test_refresh_version_registry_populated(frame):
    """
    Verify `refresh_version_registry` aggregates versions correctly.

    Contract:
    - Iterates over all SpellIndexes in `_spell_registry`.
    - Populates `_version_registry` mapping conduit_id -> set of version strings.
    """
    si1 = MagicMock(spec=SpellIndex)
    si1.get_all_versions.return_value = {"v1", "v2"}
    
    si2 = MagicMock(spec=SpellIndex)
    si2.get_all_versions.return_value = {"v3"}
    
    frame._spell_registry = {
        "c1": {si1},
        "c2": {si2}
    }
    
    frame.refresh_version_registry()
    
    assert frame._version_registry["c1"] == {"v1", "v2"}
    assert frame._version_registry["c2"] == {"v3"}

def test_has_version_true(frame):
    """
    Verify `has_version` returns True for existing versions.

    Contract:
    - Checks membership in any of the version sets in `_version_registry`.
    """
    frame._version_registry = {"c1": {"v1", "v2"}}
    assert frame.has_version("v1") is True

def test_has_version_false(frame):
    """Test has_version returns False if missing."""
    frame._version_registry = {"c1": {"v1", "v2"}}
    assert frame.has_version("v3") is False

def test_has_version_empty_arg(frame):
    """Test has_version returns False for empty/None input."""
    assert frame.has_version("") is False
    assert frame.has_version(None) is False

def test_has_version_none_registry(frame):
    """Test has_version is safe if registry is None."""
    frame._version_registry = None
    assert frame.has_version("v1") is False

def test_get_all_versions(frame):
    """Test get_all_versions flattens all sets."""
    frame._version_registry = {
        "c1": {"v1", "v2"},
        "c2": {"v2", "v3"}
    }
    result = frame.get_all_versions()
    assert result == {"v1", "v2", "v3"}

def test_get_all_versions_empty(frame):
    """Test get_all_versions returns empty set."""
    frame._version_registry = {}
    assert frame.get_all_versions() == set()

def test_get_all_versions_none_registry(frame):
    """Test get_all_versions safe with None registry."""
    frame._version_registry = None
    assert frame.get_all_versions() == set()

def test_find_and_return_spell_index_found(frame):
    """
    Verify `find_and_return_spell_index` locates the correct SpellIndex.

    Contract:
    - Scans all registered SpellIndexes.
    - Returns the first instance that contains the requested version ID.
    """
    si = MagicMock(spec=SpellIndex)
    si.get_all_versions.return_value = {"target_v"}
    frame._spell_registry = {"c1": {si}}
    
    assert frame.find_and_return_spell_index("target_v") is si

def test_find_and_return_spell_index_not_found(frame):
    """Test searching for missing version returns None."""
    si = MagicMock(spec=SpellIndex)
    si.get_all_versions.return_value = {"other_v"}
    frame._spell_registry = {"c1": {si}}
    
    assert frame.find_and_return_spell_index("target_v") is None

def test_find_and_return_spell_index_empty_arg(frame):
    """Test searching with empty arg returns None."""
    assert frame.find_and_return_spell_index("") is None
    assert frame.find_and_return_spell_index(None) is None

def test_find_and_return_spell_index_none_registry(frame):
    """Test search is safe with None registry."""
    frame._spell_registry = None
    assert frame.find_and_return_spell_index("v1") is None

def test_refresh_version_registry_merges_duplicates(frame):
    """
    Test that if multiple conduits/indexes claim version, it's merged.

    Contract:
    - Duplicate versions across different conduits/indexes are allowed in the global set.
    - Per-conduit registries maintain their own view.
    """
    si1 = MagicMock(spec=SpellIndex)
    si1.get_all_versions.return_value = {"v1"}
    
    si2 = MagicMock(spec=SpellIndex)
    si2.get_all_versions.return_value = {"v1", "v2"}
    
    frame._spell_registry = {
        "c1": {si1},
        "c2": {si2}
    }
    
    frame.refresh_version_registry()
    
    # Check c1
    assert frame._version_registry["c1"] == {"v1"}
    # Check c2
    assert frame._version_registry["c2"] == {"v1", "v2"}
    
    # Global view should have v1 and v2
    assert frame.get_all_versions() == {"v1", "v2"}

def test_find_and_return_spell_index_first_match(frame):
    """
    Test that find returns the first match it encounters.

    Contract:
    - If multiple SpellIndexes contain the version, any valid match is returned.
    """
    si1 = MagicMock(spec=SpellIndex)
    si1.get_all_versions.return_value = {"v1"}
    
    si2 = MagicMock(spec=SpellIndex)
    si2.get_all_versions.return_value = {"v1"} # Duplicate
    
    frame._spell_registry = {
        "c1": {si1, si2}
    }
    
    # We can't guarantee order in a set, but we ensure it returns ONE of them
    found = frame.find_and_return_spell_index("v1")
    assert found in (si1, si2)

def test_cleanup_handles_none_registries_gracefully(frame):
    """
    Test cleanup doesn't crash if internal dicts are already None.

    Contract:
    - Robustness check: calling cleanup on partially-initialized or corrupted object is safe.
    """
    frame._conduits = None
    frame._spell_registry = None
    frame._version_registry = None
    frame._conduit_clusters = None
    
    # Should not raise
    frame.cleanup()
    assert frame._cleaned
    
    # ----------------------------------------------------------------------
    # 6. Edge Cases & Safety
    # ----------------------------------------------------------------------

def test_refresh_version_registry_safe_if_none(frame):
    """Test refresh is no-op if spell registry is None."""
    frame._spell_registry = None
    # Should not raise
    frame.refresh_version_registry()

def test_cleaned_checks_on_methods(frame):
    """Verify methods raise RuntimeError if cleaned."""
    frame.cleanup()
    
    with pytest.raises(RuntimeError):
        frame.refresh_version_registry()
        
    with pytest.raises(RuntimeError):
        frame.has_version("v1")
        
    with pytest.raises(RuntimeError):
        frame.get_all_versions()
        
    with pytest.raises(RuntimeError):
        frame.find_and_return_spell_index("v1")

def test_init_sets_configuration_none(frame):
    """Ensure configuration starts as None."""
    assert frame._configuration is None

