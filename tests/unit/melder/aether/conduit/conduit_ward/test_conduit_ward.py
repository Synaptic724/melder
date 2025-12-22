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
    assert w.root_conduit is mock_conduit

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
    child._logger = MagicMock()
    child._conduit_state = ConduitState.lesser
    child._conduit_ward = ConduitWard(child, True, ConduitState.lesser, Policies.default)
    
    ward._link_lesser_conduit(child)
    
    assert "child-1" in ward._lesser_conduits
    assert child._parent_conduit == ward._conduit
    assert child._conduit_ward.root_conduit == ward._conduit


def test_link_lesser_conduit_requires_root_conduit() -> None:
    """
    Verify lesser lineage linking requires a root conduit.

    Contract:
        - Lesser wards must have a root conduit bound before linking children.
        - Missing root raises a RuntimeError.
    """
    parent = MagicMock(spec=IConduit)
    parent._id = "parent-1"
    parent._logger = MagicMock()
    parent._conduit_state = ConduitState.lesser
    parent_ward = ConduitWard(parent, True, ConduitState.lesser, Policies.default)
    parent._conduit_ward = parent_ward

    child = MagicMock(spec=IConduit)
    child._id = "child-1"

    with pytest.raises(RuntimeError, match="Root conduit is not set"):
        parent_ward._link_lesser_conduit(child)


def test_link_lesser_conduit_rejects_non_normal_root() -> None:
    """
    Verify lesser lineage linking rejects non-normal root conduits.

    Contract:
        - Root conduits must be normal.
        - Non-normal roots raise a RuntimeError.
    """
    parent = MagicMock(spec=IConduit)
    parent._id = "parent-2"
    parent._logger = MagicMock()
    parent._conduit_state = ConduitState.lesser
    parent_ward = ConduitWard(parent, True, ConduitState.lesser, Policies.default)
    parent._conduit_ward = parent_ward

    root = MagicMock(spec=IConduit)
    root._id = "root-1"
    root._conduit_state = ConduitState.lesser
    parent_ward._root_conduit = root

    child = MagicMock(spec=IConduit)
    child._id = "child-2"

    with pytest.raises(RuntimeError, match="Root conduit must be a normal conduit"):
        parent_ward._link_lesser_conduit(child)


def test_link_lesser_conduit_propagates_root_from_lesser_lineage() -> None:
    """
    Verify lesser lineage linking propagates the root conduit to children.

    Contract:
        - Child wards inherit the same root conduit used by the parent ward.
        - The parent-child linkage is recorded in the lineage map.
    """
    root = MagicMock(spec=IConduit)
    root._id = "root-1"
    root._logger = MagicMock()
    root._conduit_state = ConduitState.normal

    parent = MagicMock(spec=IConduit)
    parent._id = "parent-3"
    parent._logger = MagicMock()
    parent._conduit_state = ConduitState.lesser
    parent_ward = ConduitWard(parent, True, ConduitState.lesser, Policies.default)
    parent._conduit_ward = parent_ward
    parent_ward._root_conduit = root

    child = MagicMock(spec=IConduit)
    child._id = "child-3"
    child._logger = MagicMock()
    child._conduit_state = ConduitState.lesser
    child._conduit_ward = ConduitWard(child, True, ConduitState.lesser, Policies.default)

    parent_ward._link_lesser_conduit(child)

    assert child._parent_conduit == parent
    assert "child-3" in parent_ward._lesser_conduits
    assert child._conduit_ward.root_conduit == root

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


def test_convert_to_normal_sets_root_conduit() -> None:
    """
    Verify converting a lesser conduit to normal updates the root scope.
    """
    conduit, ward = _make_conduit_with_ward(
        "conduit-l1",
        dynamic=True,
        conduit_state=ConduitState.lesser,
    )
    ward._parent_conduit = MagicMock(spec=IConduit)

    ward._convert_to_normal_conduit()
    conduit._conduit_state = ConduitState.normal

    assert ward._conduit_type == ConduitState.normal
    assert ward.root_conduit is conduit

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
    # The contract registration should notify the local spellbook
    ward._conduit._spellbook._add_contracted_spell.assert_called_once_with(
        spell,
        target_conduit._id,
    )

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

    ward._link_lesser_conduit(child_conduit)
    child_ward._link_lesser_conduit(grandchild_conduit)

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
    root = MagicMock(spec=IConduit)
    root._conduit_state = ConduitState.normal
    lesser_ward._root_conduit = root
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

# ----------------------------------------------------------------------
# 12. Policy and Initialization Edges
# ----------------------------------------------------------------------

def test_init_rejects_invalid_policy_type():
    """
    Verify ConduitWard rejects non-Policies values during initialization.
    """
    conduit = MagicMock(spec=IConduit)
    conduit._id = "conduit-1"
    conduit._logger = MagicMock()
    conduit._conduit_state = ConduitState.normal

    with pytest.raises(TypeError, match="Expected Policies enum instance"):
        ConduitWard(conduit, True, ConduitState.normal, "invalid")

def test_set_new_policy_accepts_str(ward):
    """
    Verify _set_new_policy accepts string values convertible to Policies.
    """
    ward._set_new_policy("inbound_only")

    assert ward._policy == Policies.inbound_only

def test_set_policy_whitelist_all_with_contracts_fails(ward):
    """
    Verify whitelist_all cannot be set while contracts exist.
    """
    ward._contracts["c1"] = MagicMock()

    with pytest.raises(RuntimeError, match="Cannot set policy to 'block_all' or 'whitelist_all'"):
        ward._set_new_policy(Policies.whitelist_all)

# ----------------------------------------------------------------------
# 13. Link Queries and Contract Removal
# ----------------------------------------------------------------------

def test_get_links_includes_initiated_and_received(ward):
    """
    Verify _get_links returns both outbound and inbound peers.
    """
    target_b, _ = _make_conduit_with_ward("conduit-b")
    target_c, _ = _make_conduit_with_ward("conduit-c")

    ward._conduit._spellbook = MagicMock()
    target_b._spellbook = MagicMock()
    target_c._spellbook = MagicMock()

    ward._create_new_contract(target_b)
    target_c._conduit_ward._create_new_contract(ward._conduit)

    links = ward._get_links()

    link_ids = {conduit._id for conduit in links}
    assert link_ids == {"conduit-b", "conduit-c"}

def test_get_initiated_conduits_returns_outbound_only(ward):
    """
    Verify _get_initiated_conduits returns only initiated links.
    """
    target_b, _ = _make_conduit_with_ward("conduit-b")
    target_c, _ = _make_conduit_with_ward("conduit-c")

    ward._conduit._spellbook = MagicMock()
    target_b._spellbook = MagicMock()
    target_c._spellbook = MagicMock()

    ward._create_new_contract(target_b)
    target_c._conduit_ward._create_new_contract(ward._conduit)

    initiated = ward._get_initiated_conduits()

    initiated_ids = {conduit._id for conduit in initiated}
    assert initiated_ids == {"conduit-b"}

def test_get_provider_conduits_returns_inbound_only(ward):
    """
    Verify _get_provider_conduits returns only inbound links.
    """
    target_b, _ = _make_conduit_with_ward("conduit-b")
    target_c, _ = _make_conduit_with_ward("conduit-c")

    ward._conduit._spellbook = MagicMock()
    target_b._spellbook = MagicMock()
    target_c._spellbook = MagicMock()

    ward._create_new_contract(target_b)
    target_c._conduit_ward._create_new_contract(ward._conduit)

    providers = ward._get_provider_conduits()

    provider_ids = {conduit._id for conduit in providers}
    assert provider_ids == {"conduit-c"}

def test_sever_link_raises_when_no_contract(ward):
    """
    Verify _sever_link raises when no contract exists.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")

    with pytest.raises(RuntimeError, match="No contract found to sever"):
        ward._sever_link(target_conduit)

def test_remove_contract_returns_false_when_missing(ward):
    """
    Verify _remove_contract returns False when no contract exists.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")

    result = ward._remove_contract(target_conduit)

    assert result is False

def test_remove_contract_clears_indices_when_initiated(ward):
    """
    Verify _remove_contract clears initiated/received indexes for outbound links.
    """
    target_conduit, target_ward = _make_conduit_with_ward("conduit-2")

    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)

    result = ward._remove_contract(target_conduit)

    assert result is True
    assert ward._contracts == {}
    assert target_ward._contracts == {}
    assert "conduit-2" not in ward._initiated_index
    assert "conduit-1" not in target_ward._received_index

def test_remove_contract_clears_indices_when_received(ward):
    """
    Verify _remove_contract clears indexes for inbound links.
    """
    target_conduit, target_ward = _make_conduit_with_ward("conduit-2")

    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    target_ward._create_new_contract(ward._conduit)

    result = ward._remove_contract(target_conduit)

    assert result is True
    assert ward._contracts == {}
    assert target_ward._contracts == {}
    assert "conduit-2" not in ward._received_index
    assert "conduit-1" not in target_ward._initiated_index

# ----------------------------------------------------------------------
# 14. Validation Helpers (Additional Paths)
# ----------------------------------------------------------------------

def test_check_spell_id_and_spell_rejects_non_ispell(ward):
    """
    Verify _check_spell_id_and_spell rejects non-ISpell objects.
    """
    with pytest.raises(TypeError, match="Expected ISpell instance"):
        ward._check_spell_id_and_spell(spell=object())

def test_check_spell_id_and_spell_raises_when_spell_id_missing(ward):
    """
    Verify _check_spell_id_and_spell errors when spell has no inspectable ID.
    """
    spell = MagicMock(spec=ISpell)
    ward._conduit.inspect_spell = MagicMock(return_value=None)

    with pytest.raises(RuntimeError, match="Could not determine spell_id from spell"):
        ward._check_spell_id_and_spell(spell=spell)

def test_check_spell_id_and_spell_with_spell_and_id_success(ward):
    """
    Verify _check_spell_id_and_spell succeeds when spell and id match.
    """
    spell = MagicMock(spec=ISpell)
    ward._conduit.inspect_spell = MagicMock(return_value="sha-1")

    spell_id, resolved_spell = ward._check_spell_id_and_spell(spell=spell, spell_id="sha-1")

    assert spell_id == "sha-1"
    assert resolved_spell is spell

def test_check_spell_id_and_spell_with_spell_and_id_mismatch(ward):
    """
    Verify _check_spell_id_and_spell rejects mismatched spell_id with spell.
    """
    spell = MagicMock(spec=ISpell)
    ward._conduit.inspect_spell = MagicMock(return_value="sha-2")

    with pytest.raises(RuntimeError, match="does not match inspected ID"):
        ward._check_spell_id_and_spell(spell=spell, spell_id="sha-1")

def test_check_conduit_id_and_conduit_rejects_non_iconduit(ward):
    """
    Verify _check_conduit_id_and_conduit rejects non-IConduit objects.
    """
    with pytest.raises(TypeError, match="Expected IConduit instance"):
        ward._check_conduit_id_and_conduit(conduit=object())

def test_check_conduit_id_and_conduit_raises_when_conduit_id_missing(ward):
    """
    Verify _check_conduit_id_and_conduit errors when conduit has no ID.
    """
    target = MagicMock(spec=IConduit)
    target._id = None

    with pytest.raises(RuntimeError, match="Could not determine conduit_id from conduit"):
        ward._check_conduit_id_and_conduit(conduit=target)

def test_check_conduit_id_and_conduit_with_conduit_and_id_mismatch(ward):
    """
    Verify _check_conduit_id_and_conduit rejects mismatched explicit IDs.
    """
    target = MagicMock(spec=IConduit)
    target._id = "conduit-2"

    with pytest.raises(RuntimeError, match="does not match conduit internal ID"):
        ward._check_conduit_id_and_conduit(conduit=target, conduit_id="conduit-3")

# ----------------------------------------------------------------------
# 15. Spell Eligibility Policies
# ----------------------------------------------------------------------

def test_check_spell_eligible_rejects_block_all_policy(ward):
    """
    Verify block_all policy prevents contracting any spells.
    """
    ward._policy = Policies.block_all
    spell = MagicMock(spec=ISpell)
    spell._owner_conduit_id = ward._id
    spell.permissions = Permissions.read
    spell.__name__ = "ReadSpell"

    with pytest.raises(RuntimeError, match="block_all"):
        ward._check_spell_if_eligible(spell, ward._conduit, Permissions.read)

def test_check_spell_eligible_rejects_block_permissions_without_whitelist(ward):
    """
    Verify block-permission spells are rejected unless policy is whitelist_all.
    """
    ward._policy = Policies.default
    spell = MagicMock(spec=ISpell)
    spell._owner_conduit_id = ward._id
    spell.permissions = Permissions.block
    spell.__name__ = "BlockedSpell"

    with pytest.raises(RuntimeError, match="block permissions"):
        ward._check_spell_if_eligible(spell, ward._conduit, Permissions.block)

def test_check_spell_eligible_allows_block_permissions_with_whitelist(ward):
    """
    Verify block-permission spells are allowed when policy is whitelist_all.
    """
    ward._policy = Policies.whitelist_all
    spell = MagicMock(spec=ISpell)
    spell._owner_conduit_id = ward._id
    spell.permissions = Permissions.block
    spell.__name__ = "BlockedSpell"

    ward._check_spell_if_eligible(spell, ward._conduit, Permissions.block)

def test_check_spell_eligible_rejects_read_permission_mismatch(ward):
    """
    Verify read requests fail when the spell lacks read/create permissions.
    """
    ward._policy = Policies.default
    spell = MagicMock(spec=ISpell)
    spell._owner_conduit_id = ward._id
    spell.permissions = Permissions.block
    spell.__name__ = "BlockedSpell"

    with pytest.raises(RuntimeError, match="does not have read permissions"):
        ward._check_spell_if_eligible(spell, ward._conduit, Permissions.read)

# ----------------------------------------------------------------------
# 16. Local Spell Version Checks
# ----------------------------------------------------------------------

def test_has_local_spell_version_returns_true_when_present(ward):
    """
    Verify _has_local_spell_version returns True for known versions.
    """
    spell_id = "sha-1"
    spellbook = MagicMock()
    spellbook._lock = threading.RLock()
    spellbook._spells = {SpellIndex(spell_id): MagicMock()}
    ward._conduit._spellbook = spellbook

    assert ward._has_local_spell_version(spell_id) is True

def test_has_local_spell_version_returns_false_when_missing(ward):
    """
    Verify _has_local_spell_version returns False for unknown versions.
    """
    spellbook = MagicMock()
    spellbook._lock = threading.RLock()
    spellbook._spells = {SpellIndex("sha-2"): MagicMock()}
    ward._conduit._spellbook = spellbook

    assert ward._has_local_spell_version("sha-1") is False

def test_has_local_spell_version_returns_false_without_spellbook(ward):
    """
    Verify _has_local_spell_version returns False when no spellbook is present.
    """
    ward._conduit._spellbook = None

    assert ward._has_local_spell_version("sha-1") is False

# ----------------------------------------------------------------------
# 17. Validation Helpers (Spell/Conduit-Only Inputs)
# ----------------------------------------------------------------------

def test_check_spell_id_and_spell_success_with_spell_only(ward):
    """
    Verify _check_spell_id_and_spell resolves ID via inspect when spell only is provided.
    """
    spell = MagicMock(spec=ISpell)
    ward._conduit.inspect_spell = MagicMock(return_value="sha-1")

    resolved_id, resolved_spell = ward._check_spell_id_and_spell(spell=spell)

    assert resolved_id == "sha-1"
    assert resolved_spell is spell

def test_check_conduit_id_and_conduit_success_with_conduit_only(ward):
    """
    Verify _check_conduit_id_and_conduit resolves ID from the conduit object.
    """
    target = MagicMock(spec=IConduit)
    target._id = "conduit-2"

    resolved_id, resolved_conduit = ward._check_conduit_id_and_conduit(conduit=target)

    assert resolved_id == "conduit-2"
    assert resolved_conduit is target

# ----------------------------------------------------------------------
# 18. Lesser Conduit Guardrails
# ----------------------------------------------------------------------

def test_link_lesser_conduit_rejects_cleaned_ward(ward):
    """
    Verify _link_lesser_conduit rejects operations after cleanup.
    """
    ward.cleanup()
    child = MagicMock(spec=IConduit)
    child._id = "child-1"

    with pytest.raises(RuntimeError, match="cleaned"):
        ward._link_lesser_conduit(child)

# ----------------------------------------------------------------------
# 19. Contract Lookup Helpers
# ----------------------------------------------------------------------

def test_find_contract_id_returns_id_for_initiated(ward):
    """
    Verify _find_contract_id returns the contract id for initiated links.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)

    contract_id = ward._find_contract_id(target_conduit)

    assert contract_id in ward._contracts

def test_find_contract_id_returns_id_for_received(ward):
    """
    Verify _find_contract_id returns the contract id for received links.
    """
    target_conduit, target_ward = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    target_ward._create_new_contract(ward._conduit)

    contract_id = ward._find_contract_id(target_conduit)

    assert contract_id in ward._contracts

def test_find_contract_id_rejects_invalid_target(ward):
    """
    Verify _find_contract_id rejects non-IConduit targets.
    """
    with pytest.raises(TypeError, match="Expected IConduit instance"):
        ward._find_contract_id(object())

def test_find_contract_returns_contract_for_initiated(ward):
    """
    Verify _find_contract returns the contract for initiated links.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)

    contract = ward._find_contract(target_conduit)

    assert contract is ward._contracts[contract._id]

def test_find_contract_returns_none_when_missing(ward):
    """
    Verify _find_contract returns None when no contract exists.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")

    assert ward._find_contract(target_conduit) is None

def test_find_contract_rejects_invalid_target(ward):
    """
    Verify _find_contract rejects non-IConduit targets.
    """
    with pytest.raises(TypeError, match="Expected IConduit instance"):
        ward._find_contract(object())

# ----------------------------------------------------------------------
# 20. Detail Factory and Permissions Helpers
# ----------------------------------------------------------------------

def test_create_detail_sets_sources_and_fields(ward):
    """
    Verify _create_detail populates core fields and sources.
    """
    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")

    detail = ward._create_detail(
        spell,
        Permissions.read,
        ContractTypes.initiated,
        reason=DetailReason.manual,
        root_spell_id="root-1",
    )

    assert detail.spell_id == "sha-1"
    assert detail.spell_index is spell.spell_index
    assert detail.permissions == Permissions.read
    assert detail.contract_type == ContractTypes.initiated
    assert detail.reason == DetailReason.manual
    assert "root-1" in detail.sources

def test_create_detail_rejects_invalid_permissions(ward):
    """
    Verify _create_detail rejects invalid permission types.
    """
    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")

    with pytest.raises(TypeError, match="Expected Permissions enum"):
        ward._create_detail(spell, "read", ContractTypes.received)

def test_create_detail_rejects_invalid_contract_type(ward):
    """
    Verify _create_detail rejects invalid contract type values.
    """
    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")

    with pytest.raises(TypeError, match="Expected ContractTypes enum"):
        ward._create_detail(spell, Permissions.read, "received")

def test_create_detail_rejects_invalid_reason(ward):
    """
    Verify _create_detail rejects invalid reason values.
    """
    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")

    with pytest.raises(TypeError, match="Expected DetailReason enum"):
        ward._create_detail(spell, Permissions.read, ContractTypes.received, reason="manual")

def test_get_spell_permissions_reads_permissions_attr(ward):
    """
    Verify _get_spell_permissions reads and normalizes spell.permissions.
    """
    spell = MagicMock(spec=ISpell)
    spell.permissions = "create"
    spell._permissions = None

    assert ward._get_spell_permissions(spell) == Permissions.create

def test_get_spell_permissions_raises_when_missing(ward):
    """
    Verify _get_spell_permissions raises when no permissions are defined.
    """
    spell = MagicMock(spec=ISpell)
    spell.permissions = None
    spell._permissions = None

    with pytest.raises(RuntimeError, match="Spell permissions are undefined"):
        ward._get_spell_permissions(spell)

# ----------------------------------------------------------------------
# 21. Contract Emptiness and Context Manager
# ----------------------------------------------------------------------

def test_is_contract_empty_true_when_no_details(ward):
    """
    Verify _is_contract_empty returns True for a new contract.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)
    contract = ward._find_contract(target_conduit)

    assert ward._is_contract_empty(contract) is True

def test_is_contract_empty_false_after_detail_added(ward):
    """
    Verify _is_contract_empty returns False after details are added.
    """
    target_conduit, target_ward = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)
    contract = ward._find_contract(target_conduit)

    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")
    detail = ward._create_detail(
        spell,
        Permissions.read,
        ContractTypes.received,
        reason=DetailReason.manual,
    )
    contract._add(target_ward, detail)

    assert ward._is_contract_empty(contract) is False

def test_context_manager_acquires_and_releases_lock(ward):
    """
    Verify __enter__ and __exit__ acquire and release the lock.
    """
    lock = MagicMock()
    ward._lock = lock

    with ward:
        pass

    lock.acquire.assert_called_once()
    lock.release.assert_called_once()

# ----------------------------------------------------------------------
# 22. Contract Lookup by Conduit Id
# ----------------------------------------------------------------------

def test_find_contract_by_id_returns_contract_for_initiated(ward):
    """
    Verify _find_contract_by_id returns the contract for initiated links.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)

    contract = ward._find_contract_by_id(target_conduit._id)

    assert contract is not None
    assert contract._get_peer(ward)._conduit is target_conduit

def test_find_contract_by_id_returns_contract_for_received(ward):
    """
    Verify _find_contract_by_id returns the contract for received links.
    """
    target_conduit, target_ward = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    target_ward._create_new_contract(ward._conduit)

    contract = ward._find_contract_by_id(target_conduit._id)

    assert contract is not None
    assert contract._get_peer(ward)._conduit is target_conduit

def test_find_contract_by_id_returns_none_when_missing(ward):
    """
    Verify _find_contract_by_id returns None when no matching contract exists.
    """
    assert ward._find_contract_by_id("missing") is None

# ----------------------------------------------------------------------
# 23. Direct Conduit Lookup
# ----------------------------------------------------------------------

def test_get_initiated_conduit_returns_target(ward):
    """
    Verify _get_initiated_conduit returns the linked outbound conduit.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)

    result = ward._get_initiated_conduit(target_conduit._id)

    assert result is target_conduit

def test_get_provider_conduit_returns_target(ward):
    """
    Verify _get_provider_conduit returns the inbound provider conduit.
    """
    target_conduit, target_ward = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    target_ward._create_new_contract(ward._conduit)

    result = ward._get_provider_conduit(target_conduit._id)

    assert result is target_conduit

def test_get_initiated_conduit_returns_none_when_missing(ward):
    """
    Verify _get_initiated_conduit returns None for unknown conduits.
    """
    assert ward._get_initiated_conduit("missing") is None

def test_get_provider_conduit_returns_none_when_missing(ward):
    """
    Verify _get_provider_conduit returns None for unknown conduits.
    """
    assert ward._get_provider_conduit("missing") is None

# ----------------------------------------------------------------------
# 24. Contract Creation Guardrails
# ----------------------------------------------------------------------

def test_create_new_contract_returns_true_when_existing(ward):
    """
    Verify _create_new_contract is idempotent when the contract exists.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)

    result = ward._create_new_contract(target_conduit)

    assert result is True
    assert len(ward._contracts) == 1

def test_create_new_contract_raises_when_spellbook_create_fails(ward):
    """
    Verify _create_new_contract surfaces errors from spellbook linkage.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    ward._conduit._spellbook._create_link_contract = MagicMock(side_effect=RuntimeError("boom"))
    target_conduit._spellbook = MagicMock()

    with pytest.raises(RuntimeError, match="boom"):
        ward._create_new_contract(target_conduit)

def test_sever_all_linked_conduits_continues_on_error(ward):
    """
    Verify _sever_all_linked_conduits continues after per-peer failures.
    """
    target_a, _ = _make_conduit_with_ward("conduit-a")
    target_b, _ = _make_conduit_with_ward("conduit-b")
    ward._conduit._spellbook = MagicMock()
    target_a._spellbook = MagicMock()
    target_b._spellbook = MagicMock()

    ward._create_new_contract(target_a)
    ward._create_new_contract(target_b)

    def remove_side_effect(peer):
        if peer._id == "conduit-a":
            raise RuntimeError("boom")
        return True

    with patch.object(ward, "_remove_contract", side_effect=remove_side_effect) as mock_remove:
        ward._sever_all_linked_conduits()

    assert mock_remove.call_count == 2

# ----------------------------------------------------------------------
# 25. Ownership Transfer Integration
# ----------------------------------------------------------------------

def test_transfer_spell_ownership_raises_when_non_dynamic():
    """
    Verify _transfer_spell_ownership rejects non-dynamic wards.
    """
    _, local_ward = _make_conduit_with_ward("conduit-1", dynamic=False)
    target_conduit, _ = _make_conduit_with_ward("conduit-2")

    with pytest.raises(RuntimeError, match="dynamic mode"):
        local_ward._transfer_spell_ownership(spell="spell-1", target_conduit=target_conduit)

def test_transfer_spell_ownership_calls_transfer_flow(ward):
    """
    Verify _transfer_spell_ownership performs preflight and execute via TransferOfOwnership.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    summary = {"ok": True}

    with patch(
        "melder.aether.conduit.conduit_ward.transfer.transfer_of_ownership.TransferOfOwnership"
    ) as mock_transfer:
        transfer_instance = MagicMock()
        transfer_instance.preflight.return_value = summary
        mock_transfer.return_value = transfer_instance

        result = ward._transfer_spell_ownership(
            spell="spell-1",
            target_conduit=target_conduit,
            move_creations=True,
            include_dependencies=True,
            force_unshare=False,
            invalidate_after_transfer=False,
            mark_dependencies_dirty=True,
        )

    mock_transfer.assert_called_once_with(
        source_conduit=ward._conduit,
        target_conduit=target_conduit,
        spell="spell-1",
        move_creations=True,
        include_dependencies=True,
        force_unshare=False,
        invalidate_after_transfer=False,
        mark_dependencies_dirty=True,
    )
    transfer_instance.preflight.assert_called_once()
    transfer_instance.execute.assert_called_once()
    assert result == summary

# ----------------------------------------------------------------------
# 26. Initial Policy and Validation Pass/Fail
# ----------------------------------------------------------------------

def test_set_initial_policy_returns_default_when_none(ward):
    """
    Verify _set_initial_policy defaults to Policies.default when no policy is provided.
    """
    policy = ward._set_initial_policy(None)

    assert policy == Policies.default

def test_set_initial_policy_sets_flag_and_returns_value(ward):
    """
    Verify _set_initial_policy marks policy_set and returns the provided policy.
    """
    policy = ward._set_initial_policy(Policies.inbound_only)

    assert policy == Policies.inbound_only
    assert ward._policy_set is True

def test_set_initial_policy_rejects_invalid_type(ward):
    """
    Verify _set_initial_policy rejects non-Policies values.
    """
    with pytest.raises(TypeError, match="Expected Policies enum instance"):
        ward._set_initial_policy("invalid")

def test_validate_contracts_and_define_returns_false_when_missing_spells(ward):
    """
    Verify _validate_contracts_and_define returns False when contracted spells are missing.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)
    contract = ward._find_contract(target_conduit)

    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")
    detail = ward._create_detail(
        spell,
        Permissions.read,
        ContractTypes.received,
        reason=DetailReason.manual,
    )
    contract._add(ward, detail)

    target_conduit._spellbook._find_contracted_spell = MagicMock(return_value=None)
    ward._conduit._spellbook._find_contracted_spell = MagicMock(return_value=spell)

    results = ward._validate_contracts_and_define()

    assert results[contract._id] is False

def test_check_conduit_id_and_conduit_with_conduit_and_id_success(ward):
    """
    Verify _check_conduit_id_and_conduit succeeds when both inputs match.
    """
    target = MagicMock(spec=IConduit)
    target._id = "conduit-2"

    resolved_id, resolved_conduit = ward._check_conduit_id_and_conduit(
        conduit=target,
        conduit_id="conduit-2",
    )

    assert resolved_id == "conduit-2"
    assert resolved_conduit is target

def test_validate_contracts_and_define_returns_true_when_all_present(ward):
    """
    Verify _validate_contracts_and_define returns True when all spells are present.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)
    contract = ward._find_contract(target_conduit)

    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")
    detail = ward._create_detail(
        spell,
        Permissions.read,
        ContractTypes.received,
        reason=DetailReason.manual,
    )
    contract._add(target_conduit._conduit_ward, detail)

    target_conduit._spellbook._find_contracted_spell = MagicMock(return_value=spell)
    ward._conduit._spellbook._find_contracted_spell = MagicMock(return_value=spell)

    results = ward._validate_contracts_and_define()

    assert results[contract._id] is True

def test_validate_received_contracts_returns_false_when_none(ward):
    """
    Verify _validate_received_contracts returns False when no contracts exist.
    """
    assert ward._validate_received_contracts() is False

def test_validate_received_contracts_returns_true_when_valid(ward):
    """
    Verify _validate_received_contracts returns True when all contracts validate.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)
    contract = ward._find_contract(target_conduit)

    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")
    detail = ward._create_detail(
        spell,
        Permissions.read,
        ContractTypes.received,
        reason=DetailReason.manual,
    )
    contract._add(target_conduit._conduit_ward, detail)

    target_conduit._spellbook._find_contracted_spell = MagicMock(return_value=spell)
    ward._conduit._spellbook._find_contracted_spell = MagicMock(return_value=spell)

    assert ward._validate_received_contracts() is True

# ----------------------------------------------------------------------
# 27. Aetheric Frame Propagation
# ----------------------------------------------------------------------

def test_check_spell_id_and_spell_passes_aetheric_frame(ward):
    """
    Verify _check_spell_id_and_spell forwards aetheric_frame to spell resolvers.
    """
    spell = MagicMock(spec=ISpell)
    ward._conduit.get_spell_by_id = MagicMock(return_value=spell)
    ward._conduit.inspect_spell = MagicMock(return_value="sha-1")

    ward._check_spell_id_and_spell(spell_id="sha-1", aetheric_frame="frame-1")

    assert ward._conduit.get_spell_by_id.call_args == (("sha-1", "frame-1"),)
    assert ward._conduit.inspect_spell.call_args == ((spell, "frame-1"),)

def test_check_conduit_id_and_conduit_passes_aetheric_frame(ward):
    """
    Verify _check_conduit_id_and_conduit forwards aetheric_frame to conduit resolvers.
    """
    target = MagicMock(spec=IConduit)
    target._id = "conduit-2"
    ward._conduit.get_conduit_by_id = MagicMock(return_value=target)

    ward._check_conduit_id_and_conduit(conduit_id="conduit-2", aetheric_frame="frame-1")

    assert ward._conduit.get_conduit_by_id.call_args == (("conduit-2", "frame-1"),)

# ----------------------------------------------------------------------
# 28. Contract Description
# ----------------------------------------------------------------------

def test_describe_contract_returns_spell_metadata(ward):
    """
    Verify _describe_contract reports peer name, spell count, and permissions.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    target_conduit._name = "PeerName"
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)
    contract = ward._find_contract(target_conduit)

    spell = MagicMock(spec=ISpell)
    spell.spell_id = "sha-1"
    spell.spell_index = SpellIndex("sha-1")
    detail = ward._create_detail(
        spell,
        Permissions.read,
        ContractTypes.initiated,
        reason=DetailReason.manual,
    )
    contract._add(ward, detail)

    result = ward._describe_contract(target_conduit._id)

    assert result["contract_id"] == contract._id
    assert result["peer_conduit_name"] == "PeerName"
    assert result["spell_count"] == 1
    assert result["spells"] == [{"spell_id": "sha-1", "permissions": "read"}]

# ----------------------------------------------------------------------
# 29. Validation Error Handling
# ----------------------------------------------------------------------

def test_validate_contracts_and_define_returns_false_on_exception(ward):
    """
    Verify _validate_contracts_and_define marks contracts invalid on errors.
    """
    target_conduit, _ = _make_conduit_with_ward("conduit-2")
    ward._conduit._spellbook = MagicMock()
    target_conduit._spellbook = MagicMock()

    ward._create_new_contract(target_conduit)
    contract = ward._find_contract(target_conduit)

    with patch.object(contract, "_get_peer", side_effect=RuntimeError("boom")):
        results = ward._validate_contracts_and_define()

    assert results[contract._id] is False
