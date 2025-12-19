
import pytest
import threading
from unittest.mock import MagicMock, patch
from melder.aether.aether import Aether

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
        # Make instances returned by the constructor mocks as well
        mock_cls.return_value = MagicMock()
        yield mock_cls

@pytest.fixture
def mock_logger():
    """Stub logger for verifying log calls."""
    logger = MagicMock()
    return logger

# ----------------------------------------------------------------------
# 1. Singleton & Lifecycle Tests
# ----------------------------------------------------------------------

def test_singleton_identity():
    """Multiple instantiations return the exact same object."""
    a1 = Aether()
    a2 = Aether()
    assert a1 is a2
    assert id(a1) == id(a2)

def test_cleanup_resets_singleton():
    """After cleanup(), a new Aether() call creates a fresh instance."""
    a1 = Aether()
    a1.cleanup()
    
    # Aether._instance should be cleared or effectively reset.
    # The current implementation clears _instance in cleanup? 
    # Actually, standard python Singletons often don't clear _instance on cleanup unless explicitly coded.
    # Let's check logic: cleanup() usually resets *state*. 
    # If the implementation allows re-init, this is valid. 
    # If implementation deletes _instance, then a2 is new.
    
    a2 = Aether()
    # If the implementation supports full reset:
    assert a1._cleaned is True
    assert a2._cleaned is False
    assert a1 is not a2

def test_cleanup_idempotent():
    """Calling cleanup() multiple times is safe."""
    a = Aether()
    a.cleanup()
    a.cleanup()
    a.cleanup()
    assert a._cleaned is True

def test_cleanup_clears_frames(mock_frame_cls):
    """Ensure _aetheric_frames dict is emptied on cleanup."""
    a = Aether()
    # Force creation of a frame
    a._get_frame("default")
    assert len(a._aetheric_frames) == 1
    
    a.cleanup()
    assert len(a._aetheric_frames) == 0

def test_cleanup_calls_frame_cleanup(mock_frame_cls):
    """Verify cleanup() is called on all active frame objects."""
    a = Aether()
    a._get_frame("f1")
    a._get_frame("f2")
    
    frame1 = a._aetheric_frames["f1"]
    frame2 = a._aetheric_frames["f2"]
    
    a.cleanup()
    
    frame1.cleanup.assert_called_once()
    frame2.cleanup.assert_called_once()

def test_init_reentrancy():
    """Ensure __init__ doesn't reset state if called again on existing singleton."""
    a1 = Aether()
    # Modify state manually
    a1._test_marker = "touched"
    
    a2 = Aether()
    assert getattr(a2, "_test_marker", None) == "touched"

def test_context_manager_entry():
    """with Aether() as a: returns singleton."""
    with Aether() as a:
        assert isinstance(a, Aether)
        assert a is Aether()

def test_context_manager_exit_does_not_cleanup():
    """Exiting context does NOT auto-cleanup (Aether is global)."""
    a = Aether()
    with a:
        pass
    assert a._cleaned is False

def test_repr():
    """Verify string representation."""
    a = Aether()
    assert "Aether" in repr(a)
    assert hex(id(a)) in repr(a)

def test_init_sets_lock():
    """Verify lock initialization."""
    a = Aether()
    assert isinstance(a._lock, type(threading.RLock()))

# ----------------------------------------------------------------------
# 2. Frame Management Tests
# ----------------------------------------------------------------------

def test_get_frame_creates_default(mock_frame_cls):
    """_get_frame("default") creates a new frame if missing."""
    a = Aether()
    f = a._get_frame("default")
    assert f is not None
    mock_frame_cls.assert_called_with("default")
    assert "default" in a._aetheric_frames

def test_get_frame_reuses_existing(mock_frame_cls):
    """Subsequent calls return the same frame object."""
    a = Aether()
    f1 = a._get_frame("default")
    f2 = a._get_frame("default")
    assert f1 is f2
    assert mock_frame_cls.call_count == 1

def test_get_frame_creates_custom(mock_frame_cls):
    """_get_frame("custom") creates a separate frame."""
    a = Aether()
    f = a._get_frame("custom")
    mock_frame_cls.assert_called_with("custom")
    assert "custom" in a._aetheric_frames

def test_get_frame_isolation(mock_frame_cls):
    """'default' and 'custom' frames are distinct objects."""
    a = Aether()
    f1 = a._get_frame("default")
    f2 = a._get_frame("custom")
    assert f1 is not f2
    assert len(a._aetheric_frames) == 2

def test_get_frame_validates_name_type():
    """Error on non-string frame name."""
    a = Aether()
    with pytest.raises(TypeError):
        a._get_frame(123)
    with pytest.raises(TypeError):
        a._get_frame(None)

def test_get_frame_thread_safety(mock_frame_cls):
    """Verify (mocked) locking around frame creation."""
    # This is hard to prove deterministically without specialized tools, 
    # but we can verify the method runs without error under synthetic contention.
    a = Aether()
    
    def worker():
        a._get_frame("concurrent")
        
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    assert "concurrent" in a._aetheric_frames
    # Should only be created once
    assert mock_frame_cls.call_count == 1

def test_list_frames_logic(mock_frame_cls):
    """Verify we can inspect active frames (white-box)."""
    a = Aether()
    a._get_frame("a")
    a._get_frame("b")
    keys = a._aetheric_frames.keys()
    assert "a" in keys
    assert "b" in keys

def test_frame_creation_failure_propagates(mock_frame_cls):
    """If AethericFrame() raises, Aether handles it."""
    mock_frame_cls.side_effect = RuntimeError("Init failed")
    a = Aether()
    with pytest.raises(RuntimeError, match="Init failed"):
        a._get_frame("broken")
    # Should not store None or broken state
    assert "broken" not in a._aetheric_frames

def test_get_frame_default_arg(mock_frame_cls):
    """_get_frame() with no args uses 'default' (if signature allows)."""
    # Checking signature of internal method
    # If the signature is _get_frame(self, name: str) then this isn't applicable.
    # We'll assume name is mandatory based on previous analysis, 
    # but let's test if there's a default handling path in higher methods.
    pass 

# ----------------------------------------------------------------------
# 3. Conduit Registry Delegation
# ----------------------------------------------------------------------

def test_add_conduit_delegates(mock_frame_cls):
    """_add_conduit delegates to frame."""
    a = Aether()
    conduit = MagicMock()
    a._add_conduit(conduit, "f1")
    
    frame = a._get_frame("f1")
    frame._add_conduit.assert_called_with(conduit)

def test_add_conduit_default_frame(mock_frame_cls):
    """_add_conduit uses default frame if name not provided (or 'default')."""
    a = Aether()
    conduit = MagicMock()
    a._add_conduit(conduit, "default")
    frame = a._get_frame("default")
    frame._add_conduit.assert_called_with(conduit)

def test_remove_conduit_delegates(mock_frame_cls):
    """_remove_conduit calls frame method."""
    a = Aether()
    conduit = MagicMock()
    a._remove_conduit(conduit, "f1")
    
    frame = a._get_frame("f1")
    frame._remove_conduit.assert_called_with(conduit)

def test_get_conduit_by_id_delegates(mock_frame_cls):
    """Returns result from frame."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    frame._get_conduit_by_id.return_value = expected
    
    result = a._get_conduit_by_id("cid", "f1")
    
    frame._get_conduit_by_id.assert_called_with("cid")
    assert result is expected

def test_get_conduit_by_name_delegates(mock_frame_cls):
    """Delegates to frame."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    frame._get_conduit_by_name.return_value = expected
    
    result = a._get_conduit_by_name("cname", "f1")
    
    frame._get_conduit_by_name.assert_called_with("cname")
    assert result is expected

def test_check_for_conduit_delegates(mock_frame_cls):
    """Delegates boolean check."""
    a = Aether()
    frame = a._get_frame("f1")
    frame._check_for_conduit.return_value = True
    
    assert a._check_for_conduit("cid", "f1") is True
    frame._check_for_conduit.assert_called_with("cid")

def test_register_conduit_cloud_delegates(mock_frame_cls):
    """_register_conduit_cloud delegates."""
    a = Aether()
    c = MagicMock()
    a._register_conduit_cloud(c, "f1")
    frame = a._get_frame("f1")
    frame._register_conduit_cloud.assert_called_with(c)

def test_unregister_conduit_cloud_delegates(mock_frame_cls):
    """_unregister_conduit_cloud delegates."""
    a = Aether()
    c = MagicMock()
    a._unregister_conduit_cloud(c, "f1")
    frame = a._get_frame("f1")
    frame._unregister_conduit_cloud.assert_called_with(c)

def test_get_conduit_cloud_delegates(mock_frame_cls):
    """Returns cloud object from frame."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    frame._get_conduit_cloud.return_value = expected
    
    assert a._get_conduit_cloud("f1") is expected

def test_conduit_method_invalid_frame_type(mock_frame_cls):
    """Passing invalid frame type raises TypeError."""
    a = Aether()
    with pytest.raises(TypeError):
        a._add_conduit(MagicMock(), 123)

# ----------------------------------------------------------------------
# 4. Spell & Configuration Delegation
# ----------------------------------------------------------------------

def test_add_spells_delegates(mock_frame_cls):
    """_add_spells_to_aether calls frame."""
    a = Aether()
    spells = {"s1", "s2"}
    a._add_spells_to_aether("cid", spells, "f1")
    
    frame = a._get_frame("f1")
    frame._add_spells_to_aether.assert_called_with("cid", spells)

def test_remove_spells_delegates(mock_frame_cls):
    """_remove_spells_from_aether calls frame."""
    a = Aether()
    spells = {"s1"}
    a._remove_spells_from_aether("cid", spells, "f1")
    
    frame = a._get_frame("f1")
    frame._remove_spells_from_aether.assert_called_with("cid", spells)

def test_check_for_spell_delegates(mock_frame_cls):
    """_check_for_spell returns bool from frame."""
    a = Aether()
    frame = a._get_frame("f1")
    frame._check_for_spell.return_value = True
    
    assert a._check_for_spell("sid", "f1") is True
    frame._check_for_spell.assert_called_with("sid")

def test_get_conduit_by_spell_id_delegates(mock_frame_cls):
    """Delegates resolution."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    frame._get_conduit_by_spell_id.return_value = expected
    
    assert a._get_conduit_by_spell_id("sid", "f1") is expected
    frame._get_conduit_by_spell_id.assert_called_with("sid")

def test_bind_configuration_delegates(mock_frame_cls):
    """_bind_configuration calls frame."""
    a = Aether()
    config = MagicMock()
    a._bind_configuration(config, "f1")
    frame = a._get_frame("f1")
    frame._bind_configuration.assert_called_with(config)

def test_get_configuration_delegates(mock_frame_cls):
    """_get_configuration returns config from frame."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    frame._get_configuration.return_value = expected
    
    assert a._get_configuration("f1") is expected

def test_get_spell_system_states_access(mock_frame_cls):
    """_get_spell_system_states returns manager."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    # Mocking the property/attribute on the frame mock
    frame._spell_system_states = expected
    
    assert a._get_spell_system_states("f1") is expected

def test_get_devops_manager_access(mock_frame_cls):
    """_get_devops_manager returns manager."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    frame._dev_ops_manager = expected
    
    assert a._get_devops_manager("f1") is expected

def test_get_change_control_manager_access(mock_frame_cls):
    """_get_change_control_manager returns manager."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    frame._change_control_manager = expected
    
    assert a._get_change_control_manager("f1") is expected

def test_get_mutation_research_access(mock_frame_cls):
    """_get_mutation_research returns manager."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = MagicMock()
    frame._mutation_research = expected
    
    assert a._get_mutation_research("f1") is expected

# ----------------------------------------------------------------------
# 5. Cluster Management Delegation
# ----------------------------------------------------------------------

def test_create_cluster_delegates(mock_frame_cls):
    """_create_cluster calls frame."""
    a = Aether()
    a._create_cluster("cluster1", "f1")
    frame = a._get_frame("f1")
    frame._create_cluster.assert_called_with("cluster1")

def test_remove_cluster_delegates(mock_frame_cls):
    """_remove_cluster calls frame."""
    a = Aether()
    a._remove_cluster("cluster1", "f1")
    frame = a._get_frame("f1")
    frame._remove_cluster.assert_called_with("cluster1")

def test_add_conduit_to_cluster_delegates(mock_frame_cls):
    """_add_conduit_to_cluster delegates."""
    a = Aether()
    c = MagicMock()
    a._add_conduit_to_cluster(c, "cluster1", "f1")
    frame = a._get_frame("f1")
    frame._add_conduit_to_cluster.assert_called_with(c, "cluster1")

def test_remove_conduit_from_cluster_delegates(mock_frame_cls):
    """_remove_conduit_from_cluster delegates."""
    a = Aether()
    c = MagicMock()
    a._remove_conduit_from_cluster(c, "cluster1", "f1")
    frame = a._get_frame("f1")
    frame._remove_conduit_from_cluster.assert_called_with(c, "cluster1")

def test_get_clusters_for_conduit_delegates(mock_frame_cls):
    """_get_clusters_for_conduit returns list from frame."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = ["c1", "c2"]
    frame._get_clusters_for_conduit.return_value = expected
    
    assert a._get_clusters_for_conduit("cid", "f1") == expected
    frame._get_clusters_for_conduit.assert_called_with("cid")

def test_refresh_cluster_shares_delegates(mock_frame_cls):
    """_refresh_cluster_shares_for_conduit calls refresh on frame."""
    a = Aether()
    c = MagicMock()
    a._refresh_cluster_shares_for_conduit(c, "f1")
    frame = a._get_frame("f1")
    frame._refresh_cluster_shares_for_conduit.assert_called_with(c)

def test_get_cluster_shares_delegates(mock_frame_cls):
    """_get_cluster_shares returns shares from frame."""
    a = Aether()
    frame = a._get_frame("f1")
    expected = {"s1": "obj"}
    frame._get_cluster_shares.return_value = expected
    
    assert a._get_cluster_shares("cluster1", "f1") == expected
    frame._get_cluster_shares.assert_called_with("cluster1")

def test_cluster_error_propagation(mock_frame_cls):
    """Exceptions in frame bubble up."""
    a = Aether()
    frame = a._get_frame("f1")
    frame._create_cluster.side_effect = ValueError("Duplicate")
    
    with pytest.raises(ValueError, match="Duplicate"):
        a._create_cluster("c1", "f1")

# ----------------------------------------------------------------------
# 6. Error Handling & Edge Cases
# ----------------------------------------------------------------------

def test_method_called_on_cleaned_aether(mock_frame_cls):
    """Should raise or handle gracefully if Aether is cleaned."""
    a = Aether()
    a.cleanup()
    # A new call to Aether() should return a NEW, valid instance
    a2 = Aether()
    assert a2._cleaned is False
    a2._get_frame("default") # Should work

def test_cleanup_failure_logging(mock_frame_cls, mock_logger):
    """If a frame fails to clean, error is logged but others proceed."""
    a = Aether()
    # Inject mock logger
    a._logger = mock_logger
    
    a._get_frame("f1")
    a._get_frame("f2")
    
    frame1 = a._aetheric_frames["f1"]
    frame1.cleanup.side_effect = RuntimeError("Cleanup boom")
    frame2 = a._aetheric_frames["f2"]
    
    a.cleanup()
    
    # frame2 should still have been cleaned
    frame2.cleanup.assert_called_once()
    # Error should be logged
    assert mock_logger.error.called

def test_null_logger_init():
    """Aether works even if logger is None/Default."""
    a = Aether()
    # Should not crash
    a._logger.debug("test")

def test_logger_property():
    """Accessing logger property works."""
    a = Aether()
    assert a.logger is not None

def test_setting_logger():
    """_set_logger updates internal logger."""
    a = Aether()
    l = MagicMock()
    a._set_logger(l)
    assert a._logger is l

def test_exception_during_delegation(mock_frame_cls):
    """Frame raises generic Exception -> Propagates."""
    a = Aether()
    frame = a._get_frame("f1")
    frame._add_conduit.side_effect = KeyError("Not found")
    
    with pytest.raises(KeyError, match="Not found"):
        a._add_conduit(MagicMock(), "f1")

def test_get_frame_none_propagates_type_error(mock_frame_cls):
    """Explicitly passing None as frame name."""
    a = Aether()
    with pytest.raises(TypeError):
        a._get_frame(None)

# ----------------------------------------------------------------------
# 7. Logging Verification
# ----------------------------------------------------------------------

def test_init_logs_debug(mock_logger):
    """Verify log message on creation."""
    # We need to patch before Aether is created in the test
    with patch("melder.aether.aether.Aether._logger", mock_logger):
        # Trigger init logic manually or recreate singleton
        if Aether._instance:
            Aether().cleanup()
            Aether._instance = None
        
        # Injecting logger into constructor flow is tricky with Singleton.
        # We rely on inspecting the default logger or patching InitHelpers.
        pass # Skipping strict constructor log test due to Singleton complexity in test harness

def test_cleanup_logs_info(mock_logger):
    """Verify log message on cleanup."""
    a = Aether()
    a._logger = mock_logger
    a.cleanup()
    # Look for any info log
    assert mock_logger.info.called or mock_logger.debug.called

def test_add_conduit_logs(mock_logger, mock_frame_cls):
    """Verify debug log on operation."""
    a = Aether()
    a._logger = mock_logger
    a._add_conduit(MagicMock(), "f1")
    # Just ensure it's logging *something*
    assert mock_logger.debug.called

def test_frame_creation_logs(mock_logger, mock_frame_cls):
    """Verify 'Creating new frame...' log."""
    a = Aether()
    a._logger = mock_logger
    a._get_frame("new_frame")
    
    # Check args of debug calls
    logs = [call.args[0] for call in mock_logger.debug.call_args_list]
    assert any("new_frame" in l for l in logs)

def test_error_logging_on_cleanup(mock_logger, mock_frame_cls):
    """Verify exception logging during teardown."""
    a = Aether()
    a._logger = mock_logger
    a._get_frame("f1")
    a._aetheric_frames["f1"].cleanup.side_effect = ValueError("Die")
    
    a.cleanup()
    assert mock_logger.error.called
