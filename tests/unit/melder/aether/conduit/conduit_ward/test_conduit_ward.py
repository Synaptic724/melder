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
from melder.spellbook.bind.spell_index import SpellIndex

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

def _make_conduit_with_ward(
    conduit_id: str,
    *,
    dynamic: bool = True,
    conduit_state: ConduitState = ConduitState.normal,
) -> tuple[MagicMock, ConduitWard]:
    """
    Build a conduit mock and its ConduitWard for lifecycle tests.

    Args:
        conduit_id (str): Identifier to assign to the conduit.
        dynamic (bool): Whether the ward should run in dynamic mode.
        conduit_state (ConduitState): The conduit state to set.

    Returns:
        tuple[MagicMock, ConduitWard]: (conduit, ward) wired together.
    """
    conduit = MagicMock(spec=IConduit)
    conduit._id = conduit_id
    conduit._logger = MagicMock()
    conduit._conduit_state = conduit_state
    conduit._spellbook = MagicMock()
    ward = ConduitWard(conduit, dynamic, conduit_state, Policies.default)
    conduit._conduit_ward = ward
    return conduit, ward


@pytest.fixture
def mock_conduit():
    c = MagicMock(spec=IConduit)
    c._id = "conduit-1"
    c._logger = MagicMock()
    c._conduit_state = ConduitState.normal
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
    target_conduit._logger = MagicMock()
    
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
    target_conduit._logger = MagicMock()
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
    spell.__name__ = "ForeignSpell"
    
    with pytest.raises(RuntimeError, match="not owned"):
        ward._check_spell_if_eligible(spell, ward._conduit, Permissions.create)

def test_check_spell_eligible_permission_mismatch(ward):
    """
    Verify failure if requested permission exceeds spell permission.
    """
    spell = MagicMock(spec=ISpell)
    spell._owner_conduit_id = ward._id
    spell.permissions = Permissions.read # Only read allowed
    spell.__name__ = "ReadOnlySpell"
    
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
    target_conduit._logger = MagicMock()
    target_ward = ConduitWard(target_conduit, True, ConduitState.normal, Policies.default)
    target_conduit._conduit_ward = target_ward
    
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()
    
    ward._create_new_contract(target_conduit)
    
    # Setup Spell
    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")
    spell._owner_conduit_id = target_conduit._id
    spell.permissions = Permissions.create
    spell.__name__ = "TestSpell"
    
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

# ----------------------------------------------------------------------
# 8. Link Policy Constraints
# ----------------------------------------------------------------------

def test_link_fails_when_inbound_only_policy(ward):
    """
    Verify inbound_only policy blocks outbound link requests.
    """
    ward._policy = Policies.inbound_only
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    target_conduit._conduit_state = ConduitState.normal

    with pytest.raises(RuntimeError, match="inbound_only"):
        ward._link(target_conduit)

def test_link_fails_when_target_outbound_only_policy(ward):
    """
    Verify outbound_only targets reject inbound link requests.
    """
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    target_conduit._conduit_state = ConduitState.normal
    target_conduit._logger = MagicMock()

    target_ward = ConduitWard(target_conduit, True, ConduitState.normal, Policies.default)
    target_ward._policy = Policies.outbound_only
    target_conduit._conduit_ward = target_ward

    with pytest.raises(RuntimeError, match="outbound_only"):
        ward._link(target_conduit)

def test_link_fails_when_non_dynamic():
    """
    Verify _link rejects when dynamic mode is disabled.
    """
    _, local_ward = _make_conduit_with_ward("conduit-1", dynamic=False)
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    target_conduit._conduit_state = ConduitState.normal

    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        local_ward._link(target_conduit)

def test_link_returns_true_when_contract_already_exists(ward):
    """
    Verify _link short-circuits when a contract already exists.
    """
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    target_conduit._conduit_state = ConduitState.normal
    target_conduit._logger = MagicMock()
    target_ward = ConduitWard(target_conduit, True, ConduitState.normal, Policies.default)
    target_conduit._conduit_ward = target_ward

    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)

    result = ward._link(target_conduit)

    assert result is True
    assert len(ward._contracts) == 1

def test_link_returns_false_when_target_not_normal(ward):
    """
    Verify _link returns False for non-normal, non-lesser targets.
    """
    target_conduit = MagicMock(spec=IConduit)
    target_conduit._id = "conduit-2"
    target_conduit._conduit_state = ConduitState.cleaned

    result = ward._link(target_conduit)

    assert result is False
    assert ward._contracts == {}

# ----------------------------------------------------------------------
# 9. Cleanup and Lesser Conduits
# ----------------------------------------------------------------------

def test_cleanup_all_lesser_conduits_clears_and_calls_cleanup(ward):
    """
    Verify cleanup_all_lesser_conduits cleans children and clears the map.
    """
    child = MagicMock(spec=IConduit)
    child._id = "child-1"
    child.cleanup = MagicMock()

    ward._link_lesser_conduit(child)
    ward.cleanup_all_lesser_conduits()

    child.cleanup.assert_called_once()
    assert ward._lesser_conduits == {}

def test_cleanup_all_lesser_conduits_raises_when_cleaned(ward):
    """
    Verify cleanup_all_lesser_conduits rejects cleaned wards.
    """
    ward.cleanup()

    with pytest.raises(RuntimeError, match="cleaned"):
        ward.cleanup_all_lesser_conduits()

def test_clean_up_lesser_conduits_links_continues_on_error(ward):
    """
    Verify _clean_up_lesser_conduits_links continues after child cleanup errors.
    """
    child_ok = MagicMock(spec=IConduit)
    child_ok._id = "child-ok"
    child_ok.cleanup = MagicMock()
    child_bad = MagicMock(spec=IConduit)
    child_bad._id = "child-bad"
    child_bad.cleanup = MagicMock(side_effect=RuntimeError("boom"))

    ward._link_lesser_conduit(child_ok)
    ward._link_lesser_conduit(child_bad)

    ward._clean_up_lesser_conduits_links()

    child_ok.cleanup.assert_called_once()
    child_bad.cleanup.assert_called_once()
    assert ward._lesser_conduits == {}

def test_get_lesser_conduit_returns_nested_child(ward):
    """
    Verify _get_lesser_conduit resolves nested lesser conduits.
    """
    child_conduit, child_ward = _make_conduit_with_ward(
        "child-1",
        conduit_state=ConduitState.lesser,
    )
    grandchild_conduit, _ = _make_conduit_with_ward(
        "grandchild-1",
        conduit_state=ConduitState.lesser,
    )

    child_ward._link_lesser_conduit(grandchild_conduit)
    ward._link_lesser_conduit(child_conduit)

    result = ward._get_lesser_conduit("grandchild-1")

    assert result is grandchild_conduit

def test_clean_up_links_delegates_to_sever(ward):
    """
    Verify _clean_up_links delegates to _sever_all_linked_conduits.
    """
    with patch.object(ward, "_sever_all_linked_conduits") as mock_sever:
        ward._clean_up_links()

    mock_sever.assert_called_once()

def test_sever_all_linked_conduits_calls_remove_contract_for_each_peer(ward):
    """
    Verify _sever_all_linked_conduits calls _remove_contract for every peer.
    """
    target_a, _ = _make_conduit_with_ward("conduit-a")
    target_b, _ = _make_conduit_with_ward("conduit-b")
    ward._conduit._spellbook = MagicMock()
    target_a._spellbook = MagicMock()
    target_b._spellbook = MagicMock()

    ward._create_new_contract(target_a)
    ward._create_new_contract(target_b)

    with patch.object(ward, "_remove_contract") as mock_remove:
        ward._sever_all_linked_conduits()

    assert mock_remove.call_count == 2
    called_ids = {call.args[0]._id for call in mock_remove.call_args_list}
    assert called_ids == {"conduit-a", "conduit-b"}

# ----------------------------------------------------------------------
# 10. Lineage Transitions
# ----------------------------------------------------------------------

def test_convert_to_normal_conduit_rejects_when_not_lesser(ward):
    """
    Verify _convert_to_normal_conduit rejects non-lesser wards.
    """
    with pytest.raises(RuntimeError, match="not a lesser conduit"):
        ward._convert_to_normal_conduit()

def test_convert_to_normal_conduit_rejects_non_dynamic():
    """
    Verify conversion fails when dynamic mode is disabled.
    """
    _, lesser_ward = _make_conduit_with_ward(
        "conduit-1",
        dynamic=False,
        conduit_state=ConduitState.lesser,
    )
    lesser_ward._parent_conduit = MagicMock(spec=IConduit)

    with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
        lesser_ward._convert_to_normal_conduit()

def test_convert_to_normal_conduit_rejects_missing_parent():
    """
    Verify conversion fails when parent link is missing.
    """
    _, lesser_ward = _make_conduit_with_ward(
        "conduit-1",
        conduit_state=ConduitState.lesser,
    )

    with pytest.raises(RuntimeError, match="No parent conduit link found"):
        lesser_ward._convert_to_normal_conduit()

def test_convert_to_normal_conduit_rejects_when_children_present():
    """
    Verify conversion fails when lesser conduits remain linked.
    """
    _, lesser_ward = _make_conduit_with_ward(
        "conduit-1",
        conduit_state=ConduitState.lesser,
    )
    lesser_ward._parent_conduit = MagicMock(spec=IConduit)
    child = MagicMock(spec=IConduit)
    child._id = "child-1"
    lesser_ward._link_lesser_conduit(child)

    with pytest.raises(RuntimeError, match="Cannot convert to normal conduit"):
        lesser_ward._convert_to_normal_conduit()

def test_convert_to_normal_conduit_success_resets_state():
    """
    Verify successful conversion clears parent link and resets policy.
    """
    _, lesser_ward = _make_conduit_with_ward(
        "conduit-1",
        conduit_state=ConduitState.lesser,
    )
    lesser_ward._parent_conduit = MagicMock(spec=IConduit)
    lesser_ward._policy = Policies.whitelist_all

    lesser_ward._convert_to_normal_conduit()

    assert lesser_ward._parent_conduit is None
    assert lesser_ward._conduit_type == ConduitState.normal
    assert lesser_ward._policy == Policies.default

# ----------------------------------------------------------------------
# 11. Validation Helpers
# ----------------------------------------------------------------------

def test_check_spell_id_and_spell_requires_input(ward):
    """
    Verify _check_spell_id_and_spell rejects missing inputs.
    """
    with pytest.raises(ValueError, match="Either spell or spell_id"):
        ward._check_spell_id_and_spell()

def test_check_spell_id_and_spell_rejects_non_str_id(ward):
    """
    Verify _check_spell_id_and_spell rejects non-string spell_id.
    """
    with pytest.raises(TypeError, match="Expected spell_id as str"):
        ward._check_spell_id_and_spell(spell_id=123)

def test_check_spell_id_and_spell_raises_when_unresolved(ward):
    """
    Verify _check_spell_id_and_spell errors when spell_id cannot be resolved.
    """
    ward._conduit.get_spell_by_id = MagicMock(return_value=None)

    with pytest.raises(RuntimeError, match="Could not resolve spell"):
        ward._check_spell_id_and_spell(spell_id="missing")

def test_check_spell_id_and_spell_raises_on_id_mismatch(ward):
    """
    Verify _check_spell_id_and_spell rejects mismatched inspected IDs.
    """
    spell = MagicMock(spec=ISpell)
    ward._conduit.get_spell_by_id = MagicMock(return_value=spell)
    ward._conduit.inspect_spell = MagicMock(return_value="sha-2")

    with pytest.raises(RuntimeError, match="does not match inspected ID"):
        ward._check_spell_id_and_spell(spell_id="sha-1")

def test_check_spell_id_and_spell_success(ward):
    """
    Verify _check_spell_id_and_spell resolves and returns the spell.
    """
    spell = MagicMock(spec=ISpell)
    ward._conduit.get_spell_by_id = MagicMock(return_value=spell)
    ward._conduit.inspect_spell = MagicMock(return_value="sha-1")

    resolved_id, resolved_spell = ward._check_spell_id_and_spell(spell_id="sha-1")

    assert resolved_id == "sha-1"
    assert resolved_spell is spell

def test_check_conduit_id_and_conduit_requires_input(ward):
    """
    Verify _check_conduit_id_and_conduit rejects missing inputs.
    """
    with pytest.raises(ValueError, match="Either conduit or conduit_id"):
        ward._check_conduit_id_and_conduit()

def test_check_conduit_id_and_conduit_rejects_non_str_id(ward):
    """
    Verify _check_conduit_id_and_conduit rejects non-string conduit_id.
    """
    with pytest.raises(TypeError, match="Expected conduit_id as str"):
        ward._check_conduit_id_and_conduit(conduit_id=123)

def test_check_conduit_id_and_conduit_raises_when_unresolved(ward):
    """
    Verify _check_conduit_id_and_conduit errors when conduit_id cannot be resolved.
    """
    ward._conduit.get_conduit_by_id = MagicMock(return_value=None)

    with pytest.raises(RuntimeError, match="Could not resolve conduit"):
        ward._check_conduit_id_and_conduit(conduit_id="missing")

def test_check_conduit_id_and_conduit_raises_on_id_mismatch(ward):
    """
    Verify _check_conduit_id_and_conduit rejects mismatched IDs.
    """
    target = MagicMock(spec=IConduit)
    target._id = "other"
    ward._conduit.get_conduit_by_id = MagicMock(return_value=target)

    with pytest.raises(RuntimeError, match="does not match conduit internal ID"):
        ward._check_conduit_id_and_conduit(conduit_id="conduit-2")

def test_check_conduit_id_and_conduit_success(ward):
    """
    Verify _check_conduit_id_and_conduit resolves and returns the conduit.
    """
    target = MagicMock(spec=IConduit)
    target._id = "conduit-2"
    ward._conduit.get_conduit_by_id = MagicMock(return_value=target)

    resolved_id, resolved_conduit = ward._check_conduit_id_and_conduit(conduit_id="conduit-2")

    assert resolved_id == "conduit-2"
    assert resolved_conduit is target
