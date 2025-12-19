import threading
import pytest
from unittest.mock import MagicMock, patch, ANY
from melder.aether.aetheric_frame import AethericFrame
from melder.spellbook.bind.spell_index import SpellIndex

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_dependencies():
    """
    Patches all external dependencies instantiated in AethericFrame.__init__.
    Returns a dict of the mock classes.
    """
    with patch("melder.aether.aetheric_frame.ConduitCloud") as mock_cloud, \
         patch("melder.aether.aetheric_frame.MutationResearch") as mock_mr, \
         patch("melder.aether.aetheric_frame.SpellSystemStates") as mock_sss, \
         patch("melder.aether.aetheric_frame.DevOpsManager") as mock_dom:
        yield {
            "cloud": mock_cloud,
            "mr": mock_mr,
            "sss": mock_sss,
            "dom": mock_dom
        }

@pytest.fixture
def frame(mock_dependencies):
    """Returns a fresh AethericFrame instance with mocked dependencies."""
    return AethericFrame("test_frame")

# ----------------------------------------------------------------------
# 1. Initialization Tests
# ----------------------------------------------------------------------

def test_init_success(mock_dependencies):
    """Test successful initialization sets name and creates components."""
    f = AethericFrame("my_frame")
    assert f.name == "my_frame"
    assert f._id is not None
    assert isinstance(f._lock, type(threading.RLock()))
    
    # Verify registries are empty dicts
    assert f._conduits == {}
    assert f._spell_registry == {}
    assert f._version_registry == {}
    assert f._conduit_clusters == {}
    
    # Verify sub-components were created
    assert f._conduit_cloud is mock_dependencies["cloud"].return_value
    assert f._mutation_research is mock_dependencies["mr"].return_value
    assert f._spell_system_states is mock_dependencies["sss"].return_value
    assert f._dev_ops_manager is mock_dependencies["dom"].return_value

def test_init_empty_name_raises():
    """Test that empty name raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        AethericFrame("")

def test_init_none_name_raises():
    """Test that None name raises ValueError (via type check or bool check)."""
    with pytest.raises(ValueError): # or TypeError depending on impl detail, but ValueError expected
        AethericFrame(None)

# ----------------------------------------------------------------------
# 2. Context Manager Tests
# ----------------------------------------------------------------------

def test_context_manager_acquires_lock(frame):
    """Test __enter__ and __exit__ manage the lock."""
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
    """Test cleanup empties all dictionaries."""
    # Populate some dummy data
    frame._conduits["c1"] = MagicMock()
    frame._spell_registry["c1"] = set()
    frame._version_registry["c1"] = set()
    frame._conduit_clusters["cl1"] = MagicMock()
    
    frame.cleanup()
    
    assert frame._conduits is None
    assert frame._spell_registry is None
    assert frame._version_registry is None
    assert frame._conduit_clusters is None
    assert frame._cleaned is True

def test_cleanup_calls_subcomponent_cleanup(frame):
    """Test cleanup delegates to child objects."""
    # Sub-components are mocks from fixture
    cloud = frame._conduit_cloud
    mr = frame._mutation_research
    sss = frame._spell_system_states
    dom = frame._dev_ops_manager
    conduit = MagicMock()
    frame._conduits["c1"] = conduit
    cluster = MagicMock()
    frame._conduit_clusters["cl1"] = cluster
    
    frame.cleanup()
    
    cloud.cleanup.assert_called_once()
    mr.cleanup.assert_called_once()
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

def test_cleanup_nulls_properties(frame):
    """Test cleanup sets internal references to None."""
    frame.cleanup()
    assert frame._conduit_cloud is None
    assert frame._mutation_research is None
    assert frame._dev_ops_manager is None
    assert frame._spell_system_states is None
    assert frame._configuration is None
    assert frame.name is None
    assert frame._id is None
    assert frame._lock is None

def test_cleanup_tolerant_of_errors(frame):
    """Test cleanup continues if a sub-component raises error."""
    bad_conduit = MagicMock()
    bad_conduit.cleanup.side_effect = RuntimeError("Boom")
    frame._conduits["c1"] = bad_conduit
    
    # Should not raise
    frame.cleanup()
    assert frame._cleaned is True
    assert frame._conduits is None

# ----------------------------------------------------------------------
# 4. Property Accessor Tests
# ----------------------------------------------------------------------

def test_property_accessors_success(frame):
    """Test access to sub-manager properties."""
    assert frame.spell_system_states is not None
    assert frame.dev_ops_manager is not None
    assert frame.mutation_research is not None

def test_property_accessors_fail_after_cleanup(frame):
    """Test access raises RuntimeError after cleanup."""
    frame.cleanup()
    with pytest.raises(RuntimeError):
        _ = frame.spell_system_states
    with pytest.raises(RuntimeError):
        _ = frame.dev_ops_manager
    with pytest.raises(RuntimeError):
        _ = frame.mutation_research

# ----------------------------------------------------------------------
# 5. Version Registry Tests
# ----------------------------------------------------------------------

def test_refresh_version_registry_empty(frame):
    """Test refresh with empty spell registry results in empty version registry."""
    frame.refresh_version_registry()
    assert frame._version_registry == {}

def test_refresh_version_registry_populated(frame):
    """Test refresh correctly aggregates versions from SpellIndex objects."""
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
    """Test has_version returns True if present."""
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
    """Test finding a SpellIndex by version."""
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
