import pytest
import threading
from unittest.mock import MagicMock
from melder.aether.conduit_cloud import ConduitCloud
from melder.utilities.interfaces.interfaces import IConduit

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
    conduit.name = "test_conduit"
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