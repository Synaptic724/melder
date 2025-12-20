import pytest
from unittest.mock import MagicMock, patch
import threading
from threading import RLock

from melder.aether.conduit.conduit_ward.contract.contract import Contract
from melder.aether.conduit.conduit_ward.contract.details import Detail
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason
from melder.utilities.interfaces.interfaces import IConduitWard, IConduit, IContract
from melder.spellbook.bind.spell_index import SpellIndex

# Fixtures
@pytest.fixture
def mock_conduit_ward_a():
    """Mock for IConduitWard a."""
    ward = MagicMock(spec=IConduitWard)
    ward._id = "ward_a_id"
    ward._conduit = MagicMock(spec=IConduit)
    ward._conduit._id = "conduit_a_id"
    ward._conduit_ward = ward # Self-reference for _get_peer
    return ward

@pytest.fixture
def mock_conduit_ward_b():
    """Mock for IConduitWard b."""
    ward = MagicMock(spec=IConduitWard)
    ward._id = "ward_b_id"
    ward._conduit = MagicMock(spec=IConduit)
    ward._conduit._id = "conduit_b_id"
    ward._conduit_ward = ward # Self-reference for _get_peer
    return ward

@pytest.fixture
def mock_spell_index():
    """Mock for SpellIndex."""
    mock = MagicMock(spec=SpellIndex)
    mock._versions = {"sha123": "version_data"}
    return mock

@pytest.fixture
def sample_detail_a(mock_spell_index):
    """A sample Detail for ward_a."""
    detail = MagicMock(spec=Detail)
    detail.spell_id = "spell_a_id"
    detail.cleanup = MagicMock()
    return detail

@pytest.fixture
def sample_detail_b(mock_spell_index):
    """A sample Detail for ward_b."""
    detail = MagicMock(spec=Detail)
    detail.spell_id = "spell_b_id"
    detail.cleanup = MagicMock()
    return detail

@pytest.fixture
def contract(mock_conduit_ward_a, mock_conduit_ward_b):
    """A Contract instance for testing."""
    return Contract(mock_conduit_ward_a, mock_conduit_ward_b)

# ----------------------------------------------------------------------
# Initialization Tests
# ----------------------------------------------------------------------

def test_contract_init_success(mock_conduit_ward_a, mock_conduit_ward_b):
    """Verify successful initialization of Contract."""
    c = Contract(mock_conduit_ward_a, mock_conduit_ward_b)
    assert c._ward_a == mock_conduit_ward_a
    assert c._ward_b == mock_conduit_ward_b
    assert c._details_a == {}
    assert c._details_b == {}
    assert isinstance(c._lock, threading.RLock)
    assert not c._cleaned
    assert c._id is not None

# ----------------------------------------------------------------------
# Cleanup Tests
# ----------------------------------------------------------------------

def test_contract_cleanup_success(contract, sample_detail_a, sample_detail_b):
    """Verify cleanup nulls out attributes and calls detail cleanup."""
    contract._details_a["spell_a_id"] = sample_detail_a
    contract._details_b["spell_b_id"] = sample_detail_b
    
    contract.cleanup()
    
    assert contract._cleaned
    assert contract._ward_a is None
    assert contract._ward_b is None
    assert contract._details_a is None
    assert contract._details_b is None
    assert sample_detail_a.cleanup.called
    assert sample_detail_b.cleanup.called

def test_contract_cleanup_idempotent(contract):
    """Verify cleanup is idempotent."""
    contract.cleanup()
    assert contract._cleaned
    contract.cleanup() # Second call should not raise or change state further
    assert contract._cleaned

# ----------------------------------------------------------------------
# _get_peer Tests
# ----------------------------------------------------------------------

def test_get_peer_returns_correct_ward(contract, mock_conduit_ward_a, mock_conduit_ward_b):
    """Verify _get_peer returns the opposite ward."""
    assert contract._get_peer(mock_conduit_ward_a) == mock_conduit_ward_b
    assert contract._get_peer(mock_conduit_ward_b) == mock_conduit_ward_a

def test_get_peer_raises_for_invalid_ward(contract):
    """Verify _get_peer raises ValueError for a ward not in the contract."""
    invalid_ward = MagicMock(spec=IConduitWard)
    with pytest.raises(ValueError, match="Ward is not a member of this contract."):
        contract._get_peer(invalid_ward)

# ----------------------------------------------------------------------
# _get_opposite_conduit Tests
# ----------------------------------------------------------------------

def test_get_opposite_conduit_found(contract, mock_conduit_ward_a, mock_conduit_ward_b):
    """Verify _get_opposite_conduit returns the correct conduit."""
    assert contract._get_opposite_conduit(contract, "ward_a_id") == mock_conduit_ward_b._conduit
    assert contract._get_opposite_conduit(contract, "ward_b_id") == mock_conduit_ward_a._conduit

def test_get_opposite_conduit_not_found(contract):
    """Verify _get_opposite_conduit returns None if ID not in contract."""
    assert contract._get_opposite_conduit(contract, "non_existent_id") is None

# ----------------------------------------------------------------------
# _get_detail_map Tests
# ----------------------------------------------------------------------

def test_get_detail_map_returns_correct_map(contract, mock_conduit_ward_a, mock_conduit_ward_b):
    """Verify _get_detail_map returns the correct dictionary for each ward."""
    assert contract._get_detail_map(mock_conduit_ward_a) is contract._details_a
    assert contract._get_detail_map(mock_conduit_ward_b) is contract._details_b

def test_get_detail_map_raises_for_invalid_ward(contract):
    """Verify _get_detail_map raises ValueError for an invalid ward."""
    invalid_ward = MagicMock(spec=IConduitWard)
    with pytest.raises(ValueError, match="Invalid ward for contract access."):
        contract._get_detail_map(invalid_ward)

# ----------------------------------------------------------------------
# _add Tests
# ----------------------------------------------------------------------

def test_add_new_detail(contract, mock_conduit_ward_a, sample_detail_a):
    """Verify adding a new detail to a ward's map."""
    assert contract._add(mock_conduit_ward_a, sample_detail_a) is True
    assert contract._details_a["spell_a_id"] == sample_detail_a
    assert len(contract._details_a) == 1

def test_add_existing_detail_same_permissions_merges_sources(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify adding an existing detail with same permissions merges sources."""
    detail1 = Detail(
        spell_index=mock_spell_index,
        spell_id="shared_spell",
        permissions=Permissions.read,
        contract_type=ContractTypes.received,
        sources={"root_x"}
    )
    detail2 = Detail(
        spell_index=mock_spell_index,
        spell_id="shared_spell",
        permissions=Permissions.read,
        contract_type=ContractTypes.received,
        sources={"root_y"}
    )
    
    contract._add(mock_conduit_ward_a, detail1)
    assert contract._add(mock_conduit_ward_a, detail2) is False # Should return False for merge
    assert "shared_spell" in contract._details_a
    assert contract._details_a["shared_spell"].sources == {"root_x", "root_y"}

def test_add_existing_detail_different_permissions_raises(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify adding an existing detail with different permissions raises RuntimeError."""
    detail1 = Detail(
        spell_index=mock_spell_index,
        spell_id="shared_spell",
        permissions=Permissions.read,
        contract_type=ContractTypes.received,
        sources={"root_x"}
    )
    detail2 = Detail(
        spell_index=mock_spell_index,
        spell_id="shared_spell",
        permissions=Permissions.create, # Different permission
        contract_type=ContractTypes.received,
        sources={"root_y"}
    )
    
    contract._add(mock_conduit_ward_a, detail1)
    with pytest.raises(RuntimeError, match="different permissions"):
        contract._add(mock_conduit_ward_a, detail2)

# ----------------------------------------------------------------------
# _remove Tests
# ----------------------------------------------------------------------

def test_remove_existing_detail(contract, mock_conduit_ward_a, sample_detail_a):
    """Verify removing an existing detail."""
    contract._details_a["spell_a_id"] = sample_detail_a
    contract._remove(mock_conduit_ward_a, "spell_a_id")
    assert "spell_a_id" not in contract._details_a
    assert len(contract._details_a) == 0

def test_remove_non_existent_detail(contract, mock_conduit_ward_a):
    """Verify removing a non-existent detail does nothing."""
    contract._remove(mock_conduit_ward_a, "non_existent_spell")
    assert len(contract._details_a) == 0 # No change

# ----------------------------------------------------------------------
# _remove_source Tests
# ----------------------------------------------------------------------

def test_remove_source_from_detail_not_last(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify removing a source that isn't the last one."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received,
        sources={"root_1", "root_2"}
    )
    contract._details_a["spell_id"] = detail
    
    assert contract._remove_source(mock_conduit_ward_a, "spell_id", "root_1") is False
    assert "root_1" not in detail.sources
    assert "root_2" in detail.sources
    assert "spell_id" in contract._details_a # Detail should still exist

def test_remove_source_from_detail_last_one(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify removing the last source removes the detail."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received,
        sources={"root_1"}
    )
    contract._details_a["spell_id"] = detail
    
    assert contract._remove_source(mock_conduit_ward_a, "spell_id", "root_1") is True
    assert "spell_id" not in contract._details_a # Detail should be gone
    assert detail.cleanup.called

def test_remove_source_none_removes_entire_detail(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify that if root_spell_id is None, the entire detail is removed."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received,
        sources={"root_1", "root_2"}
    )
    contract._details_a["spell_id"] = detail
    
    assert contract._remove_source(mock_conduit_ward_a, "spell_id", None) is True
    assert "spell_id" not in contract._details_a
    assert detail.cleanup.called

def test_remove_source_non_existent_spell(contract, mock_conduit_ward_a):
    """Verify removing source from non-existent spell returns False."""
    assert contract._remove_source(mock_conduit_ward_a, "non_existent", "root_1") is False
    assert len(contract._details_a) == 0

# ----------------------------------------------------------------------
# _clear_contract Tests
# ----------------------------------------------------------------------

def test_clear_contract_success(contract, sample_detail_a, sample_detail_b):
    """Verify _clear_contract removes all details and calls their cleanup."""
    contract._details_a["spell_a_id"] = sample_detail_a
    contract._details_b["spell_b_id"] = sample_detail_b
    
    contract._clear_contract()
    
    assert len(contract._details_a) == 0
    assert len(contract._details_b) == 0
    assert sample_detail_a.cleanup.called
    assert sample_detail_b.cleanup.called

def test_clear_contract_empty_contract(contract):
    """Verify _clear_contract on an empty contract does nothing and doesn't raise."""
    contract._clear_contract()
    assert len(contract._details_a) == 0
    assert len(contract._details_b) == 0

# ----------------------------------------------------------------------
# _check_if_exists_and_permissions Tests
# ----------------------------------------------------------------------

def test_check_if_exists_and_permissions_true(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify check returns True when spell exists with specified permissions."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_a["spell_id"] = detail
    assert contract._check_if_exists_and_permissions(mock_conduit_ward_a, "spell_id", Permissions.read) is True

def test_check_if_exists_and_permissions_false_permissions_mismatch(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify check returns False when spell exists but permissions differ."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_a["spell_id"] = detail
    assert contract._check_if_exists_and_permissions(mock_conduit_ward_a, "spell_id", Permissions.create) is False

def test_check_if_exists_and_permissions_false_not_exists(contract, mock_conduit_ward_a):
    """Verify check returns False when spell does not exist."""
    assert contract._check_if_exists_and_permissions(mock_conduit_ward_a, "non_existent", Permissions.read) is False

# ----------------------------------------------------------------------
# _check_if_exists Tests
# ----------------------------------------------------------------------

def test_check_if_exists_true(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify check returns True when spell exists."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_a["spell_id"] = detail
    assert contract._check_if_exists(mock_conduit_ward_a, "spell_id") is True

def test_check_if_exists_false(contract, mock_conduit_ward_a):
    """Verify check returns False when spell does not exist."""
    assert contract._check_if_exists(mock_conduit_ward_a, "non_existent") is False

# ----------------------------------------------------------------------
# _find_spell_in_ward Tests
# ----------------------------------------------------------------------

def test_find_spell_in_ward_found_in_a(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify finding a spell in ward A."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id_a",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_a["spell_id_a"] = detail
    assert contract._find_spell_in_ward("spell_id_a") == mock_conduit_ward_a

def test_find_spell_in_ward_found_in_b(contract, mock_conduit_ward_b, mock_spell_index):
    """Verify finding a spell in ward B."""
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id_b",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_b["spell_id_b"] = detail
    assert contract._find_spell_in_ward("spell_id_b") == mock_conduit_ward_b

def test_find_spell_in_ward_not_found(contract):
    """Verify not finding a spell."""
    assert contract._find_spell_in_ward("non_existent_spell") is None

# ----------------------------------------------------------------------
# _grant Tests
# ----------------------------------------------------------------------

def test_grant_spells_to_ward(contract, mock_conduit_ward_a, mock_spell_index):
    """Verify granting multiple spells to a ward."""
    # Patch Detail to avoid full initialization for this test's scope
    with patch('melder.aether.conduit.conduit_ward.contract.contract.Detail', autospec=True) as MockDetail:
        # Configure MockDetail to return a mock instance
        MockDetail.return_value = MagicMock(spec=Detail)
        
        spell_ids = ["spell_1", "spell_2"]
        permissions = Permissions.create
        
        contract._grant(mock_conduit_ward_a, spell_ids, permissions)
        
        assert len(contract._details_a) == 2
        
        # Verify Detail constructor was called correctly for each spell
        assert MockDetail.call_count == 2
        # Check calls for specific arguments
        MockDetail.assert_any_call("spell_1", permissions)
        MockDetail.assert_any_call("spell_2", permissions)
        
        # Ensure the mock details were added to the map
        assert "spell_1" in contract._details_a
        assert "spell_2" in contract._details_a

