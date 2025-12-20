import pytest
import threading
from unittest.mock import MagicMock, patch, ANY
from melder.aether.conduit.conduit_ward.conduit_ward import ConduitWard
from melder.aether.conduit.conduit_state.conduit_state import ConduitState
from melder.aether.conduit.conduit_ward.policies.policies import Policies
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.interfaces.interfaces import IConduit, ISpell
from melder.aether.conduit.conduit_ward.contract.contract_types.contract_types import ContractTypes
from melder.aether.conduit.conduit_ward.contract.detail_reason import DetailReason

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_conduit():
    c = MagicMock(spec=IConduit)
    c._id = "conduit-1"
    c._logger = MagicMock()
    # Circular ref often needed
    return c

@pytest.fixture
def ward(mock_conduit):
    # dynamic=True, type=normal, policy=default
    w = ConduitWard(mock_conduit, True, ConduitState.normal, Policies.default)
    # Link back
    mock_conduit._conduit_ward = w
    return w

# ----------------------------------------------------------------------
# 1. Initialization
# ----------------------------------------------------------------------

def test_init_success(mock_conduit):
    """
    Verify successful initialization.

    Contract:
    - ID matches conduit ID.
    - Policy is set.
    - Indices are empty.
    """
    w = ConduitWard(mock_conduit, True, ConduitState.normal, Policies.default)
    assert w._id == "conduit-1"
    assert w._policy == Policies.default
    assert w._conduit_type == ConduitState.normal
    assert w._dynamic is True
    assert w._initiated_index == {}

def test_init_sets_default_policy_if_none(mock_conduit):
    """Verify None policy defaults to Policies.default."""
    w = ConduitWard(mock_conduit, True, ConduitState.normal, None)
    assert w._policy == Policies.default

# ----------------------------------------------------------------------
# 2. Cleanup
# ----------------------------------------------------------------------

def test_cleanup_idempotent(ward):
    """
    Verify cleanup is safe to call multiple times.
    """
    ward.cleanup()
    ward.cleanup()
    assert ward._cleaned

def test_cleanup_clears_state(ward):
    """
    Verify cleanup wipes internal state.
    """
    ward._initiated_index["target"] = "contract"
    ward.cleanup()
    
    assert ward._cleaned
    assert ward._initiated_index == {}
    assert ward._contracts == {}
    assert ward._conduit is None

# ----------------------------------------------------------------------
# 3. Policy Configuration
# ----------------------------------------------------------------------

def test_set_new_policy_success(ward):
    """
    Verify changing policy on a normal dynamic conduit.
    """
    ward._set_new_policy(Policies.whitelist_all)
    assert ward._policy == Policies.whitelist_all

def test_set_new_policy_fails_non_dynamic(mock_conduit):
    """
    Verify policy change fails if not dynamic environment.
    """
    w = ConduitWard(mock_conduit, False, ConduitState.normal, Policies.default)
    with pytest.raises(RuntimeError, match="not enabled"):
        w._set_new_policy(Policies.whitelist_all)

def test_set_new_policy_fails_lesser(mock_conduit):
    """
    Verify lesser conduits cannot change policy.
    """
    w = ConduitWard(mock_conduit, True, ConduitState.lesser, Policies.default)
    with pytest.raises(RuntimeError, match="lesser Conduit"):
        w._set_new_policy(Policies.whitelist_all)

def test_set_policy_block_all_with_contracts_fails(ward):
    """
    Verify cannot set block_all if contracts exist.
    """
    ward._contracts["c1"] = MagicMock()
    with pytest.raises(RuntimeError, match="existing contracts"):
        ward._set_new_policy(Policies.block_all)

# ----------------------------------------------------------------------
# 4. Link Management (Contracts)
# ----------------------------------------------------------------------

def test_link_self_fails(ward):
    """Verify self-linking is forbidden."""
    with pytest.raises(RuntimeError, match="itself"):
        ward._link(ward._conduit)

def test_link_lesser_fails(ward):
    """Verify linking to lesser conduit via _link is forbidden."""
    target = MagicMock(spec=IConduit)
    target._conduit_state = ConduitState.lesser
    
    with pytest.raises(RuntimeError, match="lesser conduit"):
        ward._link(target)

def test_create_new_contract_success(ward):
    """
    Verify creating a contract between two normal wards.
    """
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    target_conduit._conduit_state = ConduitState.normal
    
    target_ward = ConduitWard(target_conduit, True, ConduitState.normal, Policies.default)
    target_conduit._conduit_ward = target_ward
    
    # Mock spellbooks
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()
    
    success = ward._create_new_contract(target_conduit)
    
    assert success is True
    assert len(ward._contracts) == 1
    assert len(target_ward._contracts) == 1
    
    # Verify indices
    contract_id = list(ward._contracts.keys())[0]
    assert ward._initiated_index["conduit-2"] == contract_id
    assert target_ward._received_index["conduit-1"] == contract_id

def test_sever_link_success(ward):
    """
    Verify severing an existing link.
    """
    # Setup link
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    target_ward = ConduitWard(target_conduit, True, ConduitState.normal, Policies.default)
    target_conduit._conduit_ward = target_ward
    
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()
    
    ward._create_new_contract(target_conduit)
    assert len(ward._contracts) == 1
    
    # Sever
    ward._sever_link(target_conduit)
    
    assert len(ward._contracts) == 0
    assert len(target_ward._contracts) == 0
    assert "conduit-2" not in ward._initiated_index

# ----------------------------------------------------------------------
# 5. Lesser Conduits
# ----------------------------------------------------------------------

def test_link_lesser_conduit(ward):
    """
    Verify attaching a lesser conduit.
    """
    child = MagicMock(spec=IConduit)
    child._id = "child-1"
    
    ward._link_lesser_conduit(child)
    
    assert "child-1" in ward._lesser_conduits
    assert child._parent_conduit == ward._conduit

def test_get_lesser_conduit_recursive(ward):
    """
    Verify finding a nested lesser conduit.
    """
    child = MagicMock(spec=IConduit)
    child._id = "child-1"
    child._conduit_ward = None # Leaf
    
    ward._link_lesser_conduit(child)
    
    assert ward._get_lesser_conduit("child-1") is child
    assert ward._get_lesser_conduit("missing") is None

# ----------------------------------------------------------------------
# 6. Spell Eligibility & Contracting
# ----------------------------------------------------------------------

def test_check_spell_eligible_success(ward):
    """
    Verify spell check passes for owned spell with correct permissions.
    """
    spell = MagicMock(spec=ISpell)
    spell._owner_conduit_id = ward._id
    spell.permissions = Permissions.create
    spell.__name__ = "TestSpell"
    
    # Should not raise
    ward._check_spell_if_eligible(spell, ward._conduit, Permissions.create)

def test_check_spell_eligible_not_owner(ward):
    """
    Verify failure if spell not owned by conduit.
    """
    spell = MagicMock(spec=ISpell)
    spell._owner_conduit_id = "other-owner"
    spell.permissions = Permissions.create
    
    with pytest.raises(RuntimeError, match="not owned"):
        ward._check_spell_if_eligible(spell, ward._conduit, Permissions.create)

def test_check_spell_eligible_permission_mismatch(ward):
    """
    Verify failure if requested permission exceeds spell permission.
    """
    spell = MagicMock(spec=ISpell)
    spell._owner_conduit_id = ward._id
    spell.permissions = Permissions.read # Only read allowed
    
    with pytest.raises(RuntimeError, match="does not have create permissions"):
        ward._check_spell_if_eligible(spell, ward._conduit, Permissions.create)

# ----------------------------------------------------------------------
# 7. Add/Remove Spell from Contract
# ----------------------------------------------------------------------

def test_add_spell_to_contract_flow(ward):
    """
    Verify adding a spell to an existing contract.
    """
    # Setup Contract
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    target_ward = ConduitWard(target_conduit, True, ConduitState.normal, Policies.default)
    target_conduit._conduit_ward = target_ward
    
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()
    
    ward._create_new_contract(target_conduit)
    
    # Setup Spell
    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = "idx-1"
    spell._owner_conduit_id = ward._id
    spell.permissions = Permissions.create
    
    # Mock retrieval
    ward._conduit.get_spell_by_id = MagicMock(return_value=spell)
    ward._conduit.inspect_spell = MagicMock(return_value="sha-1")
    ward._conduit.get_conduit_by_id = MagicMock(return_value=target_conduit)
    
    # Act
    ward._add_spell_to_contract(
        spell_id="sha-1",
        conduit_id="conduit-2",
        permissions="create"
    )
    
    # Verify contract updated (white-box check of indices or mock verification)
    # The peer spellbook should have been notified
    target_conduit._spellbook._add_contracted_spell.assert_called()

def test_add_spell_no_contract_raises(ward):
    """
    Verify error if no contract exists.
    """
    # Mock retrieval
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    ward._conduit.get_conduit_by_id = MagicMock(return_value=target_conduit)
    spell = MagicMock(spec=ISpell)
    ward._conduit.get_spell_by_id = MagicMock(return_value=spell)
    ward._conduit.inspect_spell = MagicMock(return_value="sha-1")
    
    with pytest.raises(RuntimeError, match="No contract found"):
        ward._add_spell_to_contract(spell_id="sha-1", conduit_id="conduit-2")
