import pytest
from unittest.mock import MagicMock, patch
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
    """
    Purpose:
        Provide a mock IConduitWard representing ward A.
    Contract:
        Returns a MagicMock with ward and conduit identifiers populated.
    Returns:
        MagicMock: Ward A mock instance.
    """
    ward = MagicMock(spec=IConduitWard)
    ward._id = "ward_a_id"
    ward._conduit = MagicMock(spec=IConduit)
    ward._conduit._id = "conduit_a_id"
    ward._conduit_ward = ward # Self-reference for _get_peer
    return ward

@pytest.fixture
def mock_conduit_ward_b():
    """
    Purpose:
        Provide a mock IConduitWard representing ward B.
    Contract:
        Returns a MagicMock with ward and conduit identifiers populated.
    Returns:
        MagicMock: Ward B mock instance.
    """
    ward = MagicMock(spec=IConduitWard)
    ward._id = "ward_b_id"
    ward._conduit = MagicMock(spec=IConduit)
    ward._conduit._id = "conduit_b_id"
    ward._conduit_ward = ward # Self-reference for _get_peer
    return ward

@pytest.fixture
def mock_spell_index():
    """
    Purpose:
        Provide a mock SpellIndex for contract detail tests.
    Contract:
        Returns a MagicMock with a version map populated.
    Returns:
        MagicMock: SpellIndex mock instance.
    """
    mock = MagicMock(spec=SpellIndex)
    mock._versions = {"sha123": "version_data"}
    return mock

@pytest.fixture
def sample_detail_a(mock_spell_index):
    """
    Purpose:
        Provide a sample Detail for ward A.
    Contract:
        Returns a MagicMock Detail with a spell_id and cleanup hook.
    Args:
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        MagicMock: Detail mock for ward A.
    """
    detail = MagicMock(spec=Detail)
    detail.spell_id = "spell_a_id"
    detail.cleanup = MagicMock()
    return detail

@pytest.fixture
def sample_detail_b(mock_spell_index):
    """
    Purpose:
        Provide a sample Detail for ward B.
    Contract:
        Returns a MagicMock Detail with a spell_id and cleanup hook.
    Args:
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        MagicMock: Detail mock for ward B.
    """
    detail = MagicMock(spec=Detail)
    detail.spell_id = "spell_b_id"
    detail.cleanup = MagicMock()
    return detail

@pytest.fixture
def contract(mock_conduit_ward_a, mock_conduit_ward_b):
    """
    Purpose:
        Construct a Contract instance for tests.
    Contract:
        Returns a Contract bound to the ward A/B fixtures.
    Args:
        mock_conduit_ward_a: Ward A mock fixture.
        mock_conduit_ward_b: Ward B mock fixture.
    Returns:
        Contract: Contract under test.
    """
    return Contract(mock_conduit_ward_a, mock_conduit_ward_b)

# ----------------------------------------------------------------------
# Initialization Tests
# ----------------------------------------------------------------------

def test_contract_init_success(mock_conduit_ward_a, mock_conduit_ward_b):
    """
    Purpose:
        Verify Contract initializes core fields.
    Contract:
        Stores ward references, empty detail maps, a lock, and a non-null id.
    Args:
        mock_conduit_ward_a: Ward A mock fixture.
        mock_conduit_ward_b: Ward B mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If initialization fields are incorrect.
    """
    c = Contract(mock_conduit_ward_a, mock_conduit_ward_b)
    assert c._ward_a == mock_conduit_ward_a
    assert c._ward_b == mock_conduit_ward_b
    assert c._details_a == {}
    assert c._details_b == {}
    assert isinstance(c._lock, type(RLock()))
    assert not c._cleaned
    assert c._id is not None

# ----------------------------------------------------------------------
# Cleanup Tests
# ----------------------------------------------------------------------

def test_contract_cleanup_success(contract, sample_detail_a, sample_detail_b):
    """
    Purpose:
        Ensure cleanup nulls references and cleans details.
    Contract:
        cleanup clears wards, detail maps, and invokes detail cleanup.
    Args:
        contract: Contract fixture under test.
        sample_detail_a: Detail fixture for ward A.
        sample_detail_b: Detail fixture for ward B.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not clear or clean expected fields.
    """
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
    """
    Purpose:
        Verify cleanup can be called multiple times safely.
    Contract:
        Repeated cleanup calls preserve cleaned state and do not raise.
    Args:
        contract: Contract fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent.
    """
    contract.cleanup()
    assert contract._cleaned
    contract.cleanup() # Second call should not raise or change state further
    assert contract._cleaned

# ----------------------------------------------------------------------
# _get_peer Tests
# ----------------------------------------------------------------------

def test_get_peer_returns_correct_ward(contract, mock_conduit_ward_a, mock_conduit_ward_b):
    """
    Purpose:
        Verify _get_peer returns the opposite ward participant.
    Contract:
        Passing ward A returns ward B and vice versa.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_conduit_ward_b: Ward B mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the peer lookup is incorrect.
    """
    assert contract._get_peer(mock_conduit_ward_a) == mock_conduit_ward_b
    assert contract._get_peer(mock_conduit_ward_b) == mock_conduit_ward_a

def test_get_peer_raises_for_invalid_ward(contract):
    """
    Purpose:
        Ensure _get_peer rejects wards outside the contract.
    Contract:
        _get_peer raises ValueError for unknown wards.
    Args:
        contract: Contract fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If the expected ValueError is not raised.
    """
    invalid_ward = MagicMock(spec=IConduitWard)
    with pytest.raises(ValueError, match="Ward is not a member of this contract."):
        contract._get_peer(invalid_ward)

# ----------------------------------------------------------------------
# _get_opposite_conduit Tests
# ----------------------------------------------------------------------

def test_get_opposite_conduit_found(contract, mock_conduit_ward_a, mock_conduit_ward_b):
    """
    Purpose:
        Verify _get_opposite_conduit resolves the peer conduit.
    Contract:
        Known conduit ids map to the opposite ward's conduit.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_conduit_ward_b: Ward B mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If conduit lookup returns the wrong peer.
    """
    assert contract._get_opposite_conduit(contract, "ward_a_id") == mock_conduit_ward_b._conduit
    assert contract._get_opposite_conduit(contract, "ward_b_id") == mock_conduit_ward_a._conduit

def test_get_opposite_conduit_not_found(contract):
    """
    Purpose:
        Ensure _get_opposite_conduit returns None for unknown ids.
    Contract:
        Unknown conduit ids yield a None result.
    Args:
        contract: Contract fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If a conduit is returned for an unknown id.
    """
    assert contract._get_opposite_conduit(contract, "non_existent_id") is None

# ----------------------------------------------------------------------
# _get_detail_map Tests
# ----------------------------------------------------------------------

def test_get_detail_map_returns_correct_map(contract, mock_conduit_ward_a, mock_conduit_ward_b):
    """
    Purpose:
        Verify _get_detail_map returns the map for each ward.
    Contract:
        Ward A maps to _details_a and ward B maps to _details_b.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_conduit_ward_b: Ward B mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the returned map is incorrect.
    """
    assert contract._get_detail_map(mock_conduit_ward_a) is contract._details_a
    assert contract._get_detail_map(mock_conduit_ward_b) is contract._details_b

def test_get_detail_map_raises_for_invalid_ward(contract):
    """
    Purpose:
        Ensure _get_detail_map rejects wards outside the contract.
    Contract:
        _get_detail_map raises ValueError for invalid wards.
    Args:
        contract: Contract fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If the expected ValueError is not raised.
    """
    invalid_ward = MagicMock(spec=IConduitWard)
    with pytest.raises(ValueError, match="Invalid ward for contract access."):
        contract._get_detail_map(invalid_ward)

# ----------------------------------------------------------------------
# _add Tests
# ----------------------------------------------------------------------

def test_add_new_detail(contract, mock_conduit_ward_a, sample_detail_a):
    """
    Purpose:
        Verify adding a new detail inserts it into the ward map.
    Contract:
        _add returns True and stores the detail under its spell_id.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        sample_detail_a: Detail fixture for ward A.
    Returns:
        None.
    Raises:
        AssertionError: If the detail is not added correctly.
    """
    assert contract._add(mock_conduit_ward_a, sample_detail_a) is True
    assert contract._details_a["spell_a_id"] == sample_detail_a
    assert len(contract._details_a) == 1

def test_add_existing_detail_same_permissions_merges_sources(contract, mock_conduit_ward_a, mock_spell_index):
    """
    Purpose:
        Ensure adding a duplicate detail with same permissions merges sources.
    Contract:
        _add returns False and unions sources in the existing detail.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If sources are not merged correctly.
    """
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
    """
    Purpose:
        Ensure permission mismatches raise when adding duplicate details.
    Contract:
        _add raises RuntimeError when permissions differ for the same spell_id.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If RuntimeError is not raised on mismatch.
    """
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
    """
    Purpose:
        Verify _remove deletes an existing detail entry.
    Contract:
        After removal, the spell_id no longer exists in the map.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        sample_detail_a: Detail fixture for ward A.
    Returns:
        None.
    Raises:
        AssertionError: If the detail is not removed.
    """
    contract._details_a["spell_a_id"] = sample_detail_a
    contract._remove(mock_conduit_ward_a, "spell_a_id")
    assert "spell_a_id" not in contract._details_a
    assert len(contract._details_a) == 0

def test_remove_non_existent_detail(contract, mock_conduit_ward_a):
    """
    Purpose:
        Ensure _remove is a no-op for missing details.
    Contract:
        Removing a missing spell_id leaves the map unchanged.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the map is modified unexpectedly.
    """
    contract._remove(mock_conduit_ward_a, "non_existent_spell")
    assert len(contract._details_a) == 0 # No change

# ----------------------------------------------------------------------
# _remove_source Tests
# ----------------------------------------------------------------------

def test_remove_source_from_detail_not_last(contract, mock_conduit_ward_a, mock_spell_index):
    """
    Purpose:
        Verify removing a non-last source keeps the detail.
    Contract:
        _remove_source returns False, removes only the specified source.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If sources or detail state are incorrect.
    """
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
    """
    Purpose:
        Ensure removing the last source deletes the detail.
    Contract:
        _remove_source returns True, removes the detail, and calls cleanup.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the detail is not removed or cleaned.
    """
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
    assert detail.cleaned is True

def test_remove_source_none_removes_entire_detail(contract, mock_conduit_ward_a, mock_spell_index):
    """
    Purpose:
        Verify passing None as root_spell_id removes the detail.
    Contract:
        _remove_source returns True, removes detail, and calls cleanup.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the detail is not removed or cleaned.
    """
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
    assert detail.cleaned is True

def test_remove_source_non_existent_spell(contract, mock_conduit_ward_a):
    """
    Purpose:
        Ensure removing a source from a missing detail is a no-op.
    Contract:
        _remove_source returns False and leaves the map unchanged.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the map is modified unexpectedly.
    """
    assert contract._remove_source(mock_conduit_ward_a, "non_existent", "root_1") is False
    assert len(contract._details_a) == 0

# ----------------------------------------------------------------------
# _clear_contract Tests
# ----------------------------------------------------------------------

def test_clear_contract_success(contract, sample_detail_a, sample_detail_b):
    """
    Purpose:
        Verify _clear_contract removes all details and cleans them.
    Contract:
        Both detail maps are cleared and cleanup is called on each detail.
    Args:
        contract: Contract fixture under test.
        sample_detail_a: Detail fixture for ward A.
        sample_detail_b: Detail fixture for ward B.
    Returns:
        None.
    Raises:
        AssertionError: If details are not cleared or cleaned.
    """
    contract._details_a["spell_a_id"] = sample_detail_a
    contract._details_b["spell_b_id"] = sample_detail_b
    
    contract._clear_contract()
    
    assert len(contract._details_a) == 0
    assert len(contract._details_b) == 0
    assert sample_detail_a.cleanup.called
    assert sample_detail_b.cleanup.called

def test_clear_contract_empty_contract(contract):
    """
    Purpose:
        Ensure _clear_contract is safe when maps are empty.
    Contract:
        Calling _clear_contract on an empty contract leaves maps empty.
    Args:
        contract: Contract fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If the maps are modified unexpectedly.
    """
    contract._clear_contract()
    assert len(contract._details_a) == 0
    assert len(contract._details_b) == 0

# ----------------------------------------------------------------------
# _check_if_exists_and_permissions Tests
# ----------------------------------------------------------------------

def test_check_if_exists_and_permissions_true(contract, mock_conduit_ward_a, mock_spell_index):
    """
    Purpose:
        Verify permission check returns True for matching permissions.
    Contract:
        _check_if_exists_and_permissions returns True for existing detail.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the permission check returns False.
    """
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_a["spell_id"] = detail
    assert contract._check_if_exists_and_permissions(mock_conduit_ward_a, "spell_id", Permissions.read) is True

def test_check_if_exists_and_permissions_false_permissions_mismatch(contract, mock_conduit_ward_a, mock_spell_index):
    """
    Purpose:
        Ensure permission check fails when permissions differ.
    Contract:
        _check_if_exists_and_permissions returns False on mismatch.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the permission check returns True.
    """
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_a["spell_id"] = detail
    assert contract._check_if_exists_and_permissions(mock_conduit_ward_a, "spell_id", Permissions.create) is False

def test_check_if_exists_and_permissions_false_not_exists(contract, mock_conduit_ward_a):
    """
    Purpose:
        Ensure permission check returns False for missing spells.
    Contract:
        _check_if_exists_and_permissions returns False when detail is absent.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the permission check returns True.
    """
    assert contract._check_if_exists_and_permissions(mock_conduit_ward_a, "non_existent", Permissions.read) is False

# ----------------------------------------------------------------------
# _check_if_exists Tests
# ----------------------------------------------------------------------

def test_check_if_exists_true(contract, mock_conduit_ward_a, mock_spell_index):
    """
    Purpose:
        Verify existence check returns True when detail exists.
    Contract:
        _check_if_exists returns True for an existing spell_id.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the existence check returns False.
    """
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_a["spell_id"] = detail
    assert contract._check_if_exists(mock_conduit_ward_a, "spell_id") is True

def test_check_if_exists_false(contract, mock_conduit_ward_a):
    """
    Purpose:
        Ensure existence check returns False when detail is missing.
    Contract:
        _check_if_exists returns False for unknown spell_id.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the existence check returns True.
    """
    assert contract._check_if_exists(mock_conduit_ward_a, "non_existent") is False

# ----------------------------------------------------------------------
# _find_spell_in_ward Tests
# ----------------------------------------------------------------------

def test_find_spell_in_ward_found_in_a(contract, mock_conduit_ward_a, mock_spell_index):
    """
    Purpose:
        Verify _find_spell_in_ward returns ward A for spells in A's map.
    Contract:
        When spell_id exists in _details_a, ward A is returned.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the wrong ward is returned.
    """
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id_a",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_a["spell_id_a"] = detail
    assert contract._find_spell_in_ward("spell_id_a") == mock_conduit_ward_a

def test_find_spell_in_ward_found_in_b(contract, mock_conduit_ward_b, mock_spell_index):
    """
    Purpose:
        Verify _find_spell_in_ward returns ward B for spells in B's map.
    Contract:
        When spell_id exists in _details_b, ward B is returned.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_b: Ward B mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If the wrong ward is returned.
    """
    detail = Detail(
        spell_index=mock_spell_index,
        spell_id="spell_id_b",
        permissions=Permissions.read,
        contract_type=ContractTypes.received
    )
    contract._details_b["spell_id_b"] = detail
    assert contract._find_spell_in_ward("spell_id_b") == mock_conduit_ward_b

def test_find_spell_in_ward_not_found(contract):
    """
    Purpose:
        Ensure _find_spell_in_ward returns None for unknown spell ids.
    Contract:
        Missing spell_ids yield a None result.
    Args:
        contract: Contract fixture under test.
    Returns:
        None.
    Raises:
        AssertionError: If a ward is returned unexpectedly.
    """
    assert contract._find_spell_in_ward("non_existent_spell") is None

# ----------------------------------------------------------------------
# _grant Tests
# ----------------------------------------------------------------------

def test_grant_spells_to_ward(contract, mock_conduit_ward_a, mock_spell_index):
    """
    Purpose:
        Verify _grant creates Detail entries for each spell id.
    Contract:
        _grant populates the ward map and calls Detail for each id.
    Args:
        contract: Contract fixture under test.
        mock_conduit_ward_a: Ward A mock fixture.
        mock_spell_index: SpellIndex mock fixture.
    Returns:
        None.
    Raises:
        AssertionError: If details are not created or stored correctly.
    """
    # Patch Detail to avoid full initialization for this test's scope
    with patch('melder.aether.conduit.conduit_ward.contract.contract.Detail') as MockDetail:
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
