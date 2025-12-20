import pytest
from unittest.mock import MagicMock, patch
import threading
from threading import RLock

from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.spellbook.bind.spell_index import SpellIndex # Direct import for mocking

# Fixtures for common mocked objects
@pytest.fixture
def mock_spell_index():
    """Mock for SpellIndex."""
    mock = MagicMock(spec=SpellIndex)
    mock._versions = {"sha123": "version_data"}
    return mock

@pytest.fixture
def mock_permissions():
    """Mock for Permissions enum, using a real member for value."""
    return Permissions.create

@pytest.fixture
def mock_contract_type():
    """Mock for ContractTypes enum."""
    return ContractTypes.received

@pytest.fixture
def mock_detail_reason():
    """Mock for DetailReason enum."""
    return DetailReason.other

@pytest.fixture
def sample_detail(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """A basic Detail instance for testing."""
    return Detail(
        spell_index=mock_spell_index,
        spell_id="initial_sha",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason,
        sources={"root_spell_a"}
    )

# ----------------------------------------------------------------------
# Initialization Tests
# ----------------------------------------------------------------------

def test_detail_init_success(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """Verify successful initialization of Detail."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="test_spell_id",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason,
        sources={"root_a", "root_b"}
    )
    assert detail.spell_index == mock_spell_index
    assert detail.spell_id == "test_spell_id"
    assert detail.permissions == mock_permissions
    assert detail.contract_type == mock_contract_type
    assert detail.reason == mock_detail_reason
    assert detail.sources == {"root_a", "root_b"}
    assert isinstance(detail._lock, threading.RLock)
    assert not detail._cleaned
    assert detail._id is not None

def test_detail_init_default_sources(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """Verify sources default to an empty set if None is provided."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="test_spell_id",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason,
        sources=None
    )
    assert detail.sources == set()

def test_detail_init_type_error_spell_index():
    """Verify TypeError for invalid spell_index type."""
    with pytest.raises(TypeError, match="spell_index must be SpellIndex"):
        Detail(
            spell_index=None, # Invalid type
            spell_id="test_spell_id",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
            reason=DetailReason.other
        )

def test_detail_init_type_error_permissions(mock_spell_index):
    """Verify TypeError for invalid permissions type."""
    with pytest.raises(TypeError, match="permissions must be Permissions"):
        Detail(
            spell_index=mock_spell_index,
            spell_id="test_spell_id",
            permissions="invalid_perm", # Invalid type
            contract_type=ContractTypes.received,
            reason=DetailReason.other
        )

def test_detail_init_type_error_contract_type(mock_spell_index):
    """Verify TypeError for invalid contract_type type."""
    with pytest.raises(TypeError, match="contract_type must be ContractTypes"):
        Detail(
            spell_index=mock_spell_index,
            spell_id="test_spell_id",
            permissions=Permissions.read,
            contract_type="invalid_type", # Invalid type
            reason=DetailReason.other
        )

def test_detail_init_type_error_reason(mock_spell_index):
    """Verify TypeError for invalid reason type."""
    with pytest.raises(TypeError, match="reason must be DetailReason"):
        Detail(
            spell_index=mock_spell_index,
            spell_id="test_spell_id",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
            reason="invalid_reason" # Invalid type
        )

def test_detail_init_type_error_sources(mock_spell_index):
    """Verify TypeError for invalid sources type."""
    with pytest.raises(TypeError, match="sources must be a set of spell_ids"):
        Detail(
            spell_index=mock_spell_index,
            spell_id="test_spell_id",
            permissions=Permissions.read,
            contract_type=ContractTypes.received,
            sources=["not_a_set"] # Invalid type
        )


# ----------------------------------------------------------------------
# Cleanup Tests
# ----------------------------------------------------------------------

def test_detail_cleanup_success(sample_detail):
    """Verify cleanup nulls out attributes and marks cleaned."""
    sample_detail.cleanup()
    assert sample_detail._cleaned
    assert sample_detail.spell_index is None
    assert sample_detail.spell_id is None
    assert sample_detail.permissions is None
    assert sample_detail.contract_type is None
    assert sample_detail.reason is None
    assert sample_detail.sources is None
    assert sample_detail._lock is None
    assert sample_detail._id is None

def test_detail_cleanup_idempotent(sample_detail):
    """Verify cleanup is idempotent."""
    sample_detail.cleanup()
    assert sample_detail._cleaned
    sample_detail.cleanup() # Second call should not raise or change state further
    assert sample_detail._cleaned

# ----------------------------------------------------------------------
# has_version Tests
# ----------------------------------------------------------------------

def test_has_version_exists(sample_detail):
    """Verify has_version returns True when version exists in SpellIndex."""
    assert sample_detail.has_version("sha123")

def test_has_version_does_not_exist(sample_detail):
    """Verify has_version returns False when version does not exist."""
    assert not sample_detail.has_version("non_existent_sha")

def test_has_version_empty_spell_index(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """Verify has_version handles empty SpellIndex _versions."""
    mock_spell_index._versions = {}
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="initial_sha",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason
    )
    assert not detail.has_version("any_sha")

def test_has_version_after_cleanup(sample_detail):
    """Verify has_version raises RuntimeError after cleanup."""
    sample_detail.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        sample_detail.has_version("sha123")

# ----------------------------------------------------------------------
# add_source Tests
# ----------------------------------------------------------------------

def test_add_source_new_source(sample_detail):
    """Verify adding a new source to an existing Detail."""
    sample_detail.add_source("new_root_spell")
    assert "new_root_spell" in sample_detail.sources
    assert len(sample_detail.sources) == 2

def test_add_source_existing_source(sample_detail):
    """Verify adding an existing source does not change the set."""
    sample_detail.add_source("root_spell_a")
    assert "root_spell_a" in sample_detail.sources
    assert len(sample_detail.sources) == 1 # Still 1 unique source

def test_add_source_none(sample_detail):
    """Verify adding a None source does nothing."""
    initial_len = len(sample_detail.sources)
    sample_detail.add_source(None)
    assert len(sample_detail.sources) == initial_len # No change

def test_add_source_after_cleanup(sample_detail):
    """Verify add_source raises RuntimeError after cleanup."""
    sample_detail.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        sample_detail.add_source("new_root")

# ----------------------------------------------------------------------
# remove_source Tests
# ----------------------------------------------------------------------

def test_remove_source_existing(sample_detail):
    """Verify removing an existing source that isn't the last one."""
    sample_detail.add_source("root_spell_b")
    assert sample_detail.remove_source("root_spell_a") is False
    assert "root_spell_a" not in sample_detail.sources
    assert "root_spell_b" in sample_detail.sources
    assert len(sample_detail.sources) == 1

def test_remove_source_last_one(sample_detail):
    """Verify removing the last source returns True."""
    assert sample_detail.remove_source("root_spell_a") is True
    assert "root_spell_a" not in sample_detail.sources
    assert len(sample_detail.sources) == 0

def test_remove_source_non_existent(sample_detail):
    """Verify removing a non-existent source returns False."""
    assert sample_detail.remove_source("non_existent_root") is False
    assert len(sample_detail.sources) == 1 # No change

def test_remove_source_none(sample_detail):
    """Verify removing a None source does nothing."""
    initial_len = len(sample_detail.sources)
    assert sample_detail.remove_source(None) is False
    assert len(sample_detail.sources) == initial_len # No change

def test_remove_source_from_empty(mock_spell_index, mock_permissions, mock_contract_type, mock_detail_reason):
    """Verify removing from an initially empty sources set."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="initial_sha",
        permissions=mock_permissions,
        contract_type=mock_contract_type,
        reason=mock_detail_reason,
        sources=None
    )
    assert detail.sources == set()
    assert detail.remove_source("any_root") is False

def test_remove_source_after_cleanup(sample_detail):
    """Verify remove_source raises RuntimeError after cleanup."""
    sample_detail.cleanup()
    with pytest.raises(RuntimeError, match="cleaned"):
        sample_detail.remove_source("root_spell_a")