import pytest
import threading
from unittest.mock import MagicMock
from melder.aether.conduit_cloud import ConduitCloud
from melder.utilities.interfaces import IConduit

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def conduit_cloud():
    """
    Fixture to provide a fresh ConduitCloud instance for each test.
    Ensures cleanup is called after each test.
    """
    cloud = ConduitCloud("test_frame")
    yield cloud
    cloud.cleanup()

@pytest.fixture
def mock_conduit():
    """
    Fixture to provide a mock IConduit with a name.
    """
    conduit = MagicMock(spec=IConduit)
    conduit.id = "conduit-1"
    conduit.name = "test_conduit"
    conduit._name = "test_conduit"
    return conduit

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_init(conduit_cloud):
    """
    Verify initialization sets up the cloud correctly.

    Contract:
    - Name is stored.
    - Registry is initialized empty.
    - Lock and ID are created.
    - Cleaned flag is False.
    """
    assert conduit_cloud._name == "test_frame"
    assert conduit_cloud._registry == {}
    assert isinstance(conduit_cloud._lock, type(threading.RLock()))
    assert conduit_cloud._id is not None
    assert not conduit_cloud._cleaned

def test_register_conduit_success(conduit_cloud, mock_conduit):
    """
    Verify successful registration of a conduit.

    Contract:
    - The conduit is stored in the internal registry by name.
    """
    conduit_cloud._register_conduit(mock_conduit)
    assert "test_conduit" in conduit_cloud._registry
    assert conduit_cloud._registry["test_conduit"] is mock_conduit

def test_register_conduit_duplicate_raises(conduit_cloud, mock_conduit):
    """
    Test that registering a conduit with a duplicate name raises ValueError.
    """
    conduit_cloud._register_conduit(mock_conduit)
    
    with pytest.raises(ValueError, match="already exists"):
        conduit_cloud._register_conduit(mock_conduit)

def test_register_conduit_none_name_raises(conduit_cloud):
    """
    Test that registering a conduit with None name raises ValueError.
    """
    conduit = MagicMock(spec=IConduit)
    conduit.name = None
    conduit._name = None
    
    with pytest.raises(ValueError, match="cannot be None"):
        conduit_cloud._register_conduit(conduit)

def test_get_conduit_success(conduit_cloud, mock_conduit):
    """
    Verify retrieval of a registered conduit.

    Contract:
    - `get_conduit` returns the exact instance registered with the name.
    """
    conduit_cloud._register_conduit(mock_conduit)
    result = conduit_cloud.get_conduit("test_conduit")
    assert result is mock_conduit

def test_get_conduit_not_found_raises(conduit_cloud):
    """
    Test that retrieving a non-existent conduit raises ValueError.
    """
    with pytest.raises(ValueError, match="not found"):
        conduit_cloud.get_conduit("missing")


def test_conduit_cloud_discovery_helpers_return_registered_names_and_ids(
        conduit_cloud,
        mock_conduit,
):
    """
    Verify the cloud exposes the new discovery mesh helpers.

    Returns:
        None.
    """
    conduit_cloud._register_conduit(mock_conduit)

    assert conduit_cloud.list_conduit_ids() == ("conduit-1",)
    assert conduit_cloud.list_conduit_names() == ("test_conduit",)
    assert conduit_cloud.count_conduits() == 1
    assert conduit_cloud.has_conduit_id("conduit-1") is True
    assert conduit_cloud.has_conduit_name("test_conduit") is True
    assert conduit_cloud.find_conduit_id_by_name("test_conduit") == "conduit-1"
    assert conduit_cloud.get_conduit_by_name("test_conduit") is mock_conduit
    assert conduit_cloud.get_conduit_by_id("conduit-1") is mock_conduit


def test_conduit_cloud_discovery_helpers_report_missing_entries(
        conduit_cloud,
) -> None:
    """
    Verify the new cloud discovery helpers handle missing entries cleanly.

    Returns:
        None.
    """
    assert conduit_cloud.count_conduits() == 0
    assert conduit_cloud.has_conduit_id("missing") is False
    assert conduit_cloud.has_conduit_name("missing") is False
    assert conduit_cloud.find_conduit_id_by_name("missing") is None

    with pytest.raises(ValueError, match="not found"):
        conduit_cloud.get_conduit_by_id("missing")

def test_unregister_conduit_success(conduit_cloud, mock_conduit):
    """
    Test successful unregistration of a conduit.
    """
    conduit_cloud._register_conduit(mock_conduit)
    conduit_cloud._unregister_conduit(mock_conduit)
    assert "test_conduit" not in conduit_cloud._registry

def test_unregister_conduit_not_found_raises(conduit_cloud, mock_conduit):
    """
    Test that unregistering a non-existent conduit raises ValueError.
    """
    with pytest.raises(ValueError, match="not registered"):
        conduit_cloud._unregister_conduit(mock_conduit)

def test_unregister_conduit_none_name_raises(conduit_cloud):
    """
    Test that unregistering a conduit with None name raises ValueError.
    """
    conduit = MagicMock(spec=IConduit)
    conduit._name = None
    conduit.name = None
    
    with pytest.raises(ValueError, match="cannot be None"):
        conduit_cloud._unregister_conduit(conduit)

def test_cleanup_clears_registry(conduit_cloud, mock_conduit):
    """
    Verify cleanup resets internal state.

    Contract:
    - Registry is cleared/nulled.
    - Cleaned flag is True.
    - Lock is nulled.
    """
    conduit_cloud._register_conduit(mock_conduit)
    conduit_cloud.cleanup()
    
    assert conduit_cloud._cleaned
    assert conduit_cloud._registry is None
    assert conduit_cloud._lock is None

def test_cleanup_is_idempotent(conduit_cloud):
    """
    Test that calling cleanup multiple times is safe.
    """
    conduit_cloud.cleanup()
    conduit_cloud.cleanup()
    assert conduit_cloud._cleaned


def test_cleanup_returns_early_when_cleaned_flips_inside_lock(conduit_cloud):
    """cleanup should return safely if another path marks the cloud cleaned inside the lock."""
    conduit_cloud._registry["x"] = MagicMock(spec=IConduit)
    original_lock = conduit_cloud._lock

    class _LockThatMarksCleaned:
        def __enter__(self_inner):
            conduit_cloud._cleaned = True
            return self_inner

        def __exit__(self_inner, exc_type, exc_value, traceback):
            return False

    try:
        conduit_cloud._lock = _LockThatMarksCleaned()
        conduit_cloud.cleanup()
    finally:
        conduit_cloud._lock = original_lock

    assert conduit_cloud._registry is not None

def test_context_manager(conduit_cloud):
    """
    Test that ConduitCloud can be used as a context manager.
    """
    with conduit_cloud as cloud:
        assert cloud is conduit_cloud

def test_methods_raise_after_cleanup(conduit_cloud, mock_conduit):
    """
    Verify public methods raise RuntimeError after cleanup.

    Contract:
    - All functional methods must guard against use-after-free.
    """
    conduit_cloud.cleanup()
    
    with pytest.raises(RuntimeError):
        conduit_cloud.get_conduit("any")
        
    with pytest.raises(RuntimeError):
        conduit_cloud._register_conduit(mock_conduit)
        
    with pytest.raises(RuntimeError):
        conduit_cloud._unregister_conduit(mock_conduit)
