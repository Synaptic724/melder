import pytest
from threading import RLock
from unittest.mock import MagicMock, call, patch
from melder.aether.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
from melder.aether.dev_ops.change_control_manager.orchestrator.staged_mutation import (
    ChangeControlStagedMutation,
)
from melder.aether.dev_ops.change_control_manager.transaction_request.transaction_request import (
    ChangeTransactionType,
)
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.utilities.interfaces.interfaces import ISpellIndex, ISpellSystemStates
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import RootResolutionBlueprint
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent

CONDUIT_ID = "conduit-1"

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def mock_sss():
    return MagicMock(spec=ISpellSystemStates)

@pytest.fixture
def manager(mock_sss):
    return ChangeControlManager(mock_sss)

@pytest.fixture
def mock_spell_index():
    index = MagicMock(spec=ISpellIndex)
    index.id = "spell-123"
    return index

# ----------------------------------------------------------------------
# 1. Initialization
# ----------------------------------------------------------------------

def test_init_success(manager, mock_sss):
    assert manager._spell_system_states is mock_sss
    assert isinstance(manager._pending_changes, dict)
    assert len(manager._pending_changes) == 0
    assert not manager._monitor_active_by_conduit

def test_init_validates_args():
    with pytest.raises(ValueError, match="spell_system_states cannot be None"):
        ChangeControlManager(None)

# ----------------------------------------------------------------------
# 2. Pending Changes Registry
# ----------------------------------------------------------------------

def test_register_pending_change_success(manager, mock_spell_index):
    manager.register_pending_change(mock_spell_index, "update", {"user": "alice"})
    
    change = manager.get_pending_change("spell-123")
    assert change is not None
    assert change["reason"] == "update"
    assert change["user"] == "alice"

def test_register_updates_existing(manager, mock_spell_index):
    manager.register_pending_change(mock_spell_index, "v1")
    manager.register_pending_change(mock_spell_index, "v2", {"note": "overwrite"})
    
    change = manager.get_pending_change("spell-123")
    assert change["reason"] == "v2"
    assert change["note"] == "overwrite"

def test_register_validates_inputs(manager):
    index = MagicMock(spec=ISpellIndex)
    index.id = "s1"
    
    with pytest.raises(ValueError, match="spell_index cannot be None"):
        manager.register_pending_change(None, "reason")
        
    with pytest.raises(ValueError, match="reason cannot be empty"):
        manager.register_pending_change(index, "")

def test_get_pending_change_returns_copy(manager, mock_spell_index):
    meta = {"data": "mutable"}
    manager.register_pending_change(mock_spell_index, "reason", meta)
    
    retrieved = manager.get_pending_change("spell-123")
    retrieved["data"] = "mutated"
    
    # Original should be untouched
    original = manager.get_pending_change("spell-123")
    assert original["data"] == "mutable"

def test_list_pending_changes(manager):
    idx1 = MagicMock(spec=ISpellIndex, id="s1")
    idx2 = MagicMock(spec=ISpellIndex, id="s2")
    
    manager.register_pending_change(idx1, "r1")
    manager.register_pending_change(idx2, "r2")
    
    all_changes = manager.list_pending_changes()
    assert len(all_changes) == 2
    assert "s1" in all_changes
    assert "s2" in all_changes

def test_clear_pending_change(manager, mock_spell_index):
    manager.register_pending_change(mock_spell_index, "r1")
    manager.clear_pending_change("spell-123")
    assert manager.get_pending_change("spell-123") is None

def test_clear_non_existent_is_safe(manager):
    manager.clear_pending_change("unknown")

# ----------------------------------------------------------------------
# 3. Dirty State & Component Tracking
# ----------------------------------------------------------------------

def test_rebuild_component_of(manager):
    """
    Verify `rebuild_component_of` correctly populates the dependency index.

    Contract:
    - Input blueprints are parsed to map node_ids -> root_ids.
    - A node belonging to a root's DAG must be mapped to that root.
    - Roots map to themselves.
    """
    # Setup: Root A depends on [A, B], Root C depends on [C]
    bp_a = MagicMock(spec=RootResolutionBlueprint)
    bp_a.dag.nodes.keys.return_value = ["A", "B"]
    
    bp_c = MagicMock(spec=RootResolutionBlueprint)
    bp_c.dag.nodes.keys.return_value = ["C"]
    
    blueprints = {"A": bp_a, "C": bp_c}
    
    manager.rebuild_component_of(CONDUIT_ID, blueprints)
    
    # Check mappings
    # "A" is component of A (root)
    # "B" is component of A (root)
    # "C" is component of C (root)
    
    # Implementation detail check or functional check via notification
    # Let's verify via dirty propagation
    manager.notify_spell_changed("B")
    assert manager.is_root_dirty(CONDUIT_ID, "A")
    assert not manager.is_root_dirty(CONDUIT_ID, "C")

def test_rebuild_clears_previous_state(manager):
    """
    Verify `rebuild_component_of` completely resets previous state.

    Contract:
    - Old mappings must be discarded.
    - Old dirty state (dirty spells/roots) must be cleared.
    - Monitoring state should be reset to inactive until new events occur.
    """
    # Initial state
    bp1 = MagicMock(spec=RootResolutionBlueprint)
    bp1.dag.nodes.keys.return_value = ["Old"]
    manager.rebuild_component_of(CONDUIT_ID, {"OldRoot": bp1})
    manager.notify_spell_changed("Old")
    assert manager.is_root_dirty(CONDUIT_ID, "OldRoot")
    
    # Rebuild
    bp2 = MagicMock(spec=RootResolutionBlueprint)
    bp2.dag.nodes.keys.return_value = ["New"]
    manager.rebuild_component_of(CONDUIT_ID, {"NewRoot": bp2})
    
    # Old state should be gone
    assert not manager.is_root_dirty(CONDUIT_ID, "OldRoot")
    assert not manager._dirty_spells_by_conduit[CONDUIT_ID]

def test_upsert_component_of_preserves_unrelated_roots(manager):
    """
    Verify upsert refreshes selected roots without clearing unrelated mappings.

    Contract:
    - Upsert only replaces mappings for supplied roots.
    - Unrelated roots remain tracked.
    - Replaced roots stop tracking removed nodes and track new nodes.
    """
    bp_a = MagicMock(spec=RootResolutionBlueprint)
    bp_a.dag.nodes.keys.return_value = ["A", "B"]
    bp_c = MagicMock(spec=RootResolutionBlueprint)
    bp_c.dag.nodes.keys.return_value = ["C"]
    manager.rebuild_component_of(CONDUIT_ID, {"RootA": bp_a, "RootC": bp_c})

    bp_a_new = MagicMock(spec=RootResolutionBlueprint)
    bp_a_new.dag.nodes.keys.return_value = ["A", "D"]
    manager.upsert_component_of(CONDUIT_ID, {"RootA": bp_a_new})

    manager.notify_spell_changed("B")
    assert not manager.is_root_dirty(CONDUIT_ID, "RootA")

    manager.notify_spell_changed("D")
    assert manager.is_root_dirty(CONDUIT_ID, "RootA")

    manager.notify_spell_changed("C")
    assert manager.is_root_dirty(CONDUIT_ID, "RootC")

def test_upsert_component_of_clears_dirty_roots_for_updated_scope(manager):
    """
    Verify upsert clears dirty flags for roots that were refreshed.

    Contract:
    - Dirty state for supplied roots is cleared.
    - Dirty state for other roots remains unchanged.
    """
    bp_a = MagicMock(spec=RootResolutionBlueprint)
    bp_a.dag.nodes.keys.return_value = ["A"]
    bp_c = MagicMock(spec=RootResolutionBlueprint)
    bp_c.dag.nodes.keys.return_value = ["C"]
    manager.rebuild_component_of(CONDUIT_ID, {"RootA": bp_a, "RootC": bp_c})

    manager.notify_spell_changed("A")
    manager.notify_spell_changed("C")
    assert manager.is_root_dirty(CONDUIT_ID, "RootA")
    assert manager.is_root_dirty(CONDUIT_ID, "RootC")

    bp_a_new = MagicMock(spec=RootResolutionBlueprint)
    bp_a_new.dag.nodes.keys.return_value = ["A"]
    manager.upsert_component_of(CONDUIT_ID, {"RootA": bp_a_new})

    assert not manager.is_root_dirty(CONDUIT_ID, "RootA")
    assert manager.is_root_dirty(CONDUIT_ID, "RootC")

def test_notify_activates_monitor(manager):
    """
    Verify `notify_spell_changed` activates the monitoring state.

    Contract:
    - When a spell maps to a root for the conduit, monitoring is activated.
    - The spell ID is recorded under the conduit-scoped dirty spell set.
    """
    bp = MagicMock(spec=RootResolutionBlueprint)
    bp.dag.nodes.keys.return_value = ["Root", "Leaf"]
    manager.rebuild_component_of(CONDUIT_ID, {"Root": bp})

    assert not manager._monitor_active_by_conduit.get(CONDUIT_ID, False)
    manager.notify_spell_changed("Leaf")

    assert manager._monitor_active_by_conduit[CONDUIT_ID]
    assert "Leaf" in manager._dirty_spells_by_conduit[CONDUIT_ID]

def test_revalidate_dirty_roots_success(manager):
    """
    Verify successful revalidation clears dirty state.

    Contract:
    - Calling `revalidate_dirty_roots` invokes the registered callback with current dirty roots.
    - If the callback succeeds (returns normally), the dirty roots are cleared.
    - Per-conduit monitor state is reset if no dirty roots remain.
    """
    # Setup dirty state
    bp = MagicMock(spec=RootResolutionBlueprint)
    bp.dag.nodes.keys.return_value = ["Leaf"]
    manager.rebuild_component_of(CONDUIT_ID, {"Root": bp})
    
    manager.notify_spell_changed("Leaf")
    assert manager.is_root_dirty(CONDUIT_ID, "Root")
    
    # Register revalidator
    validator = MagicMock(return_value={"Root"})
    manager.set_revalidator(CONDUIT_ID, validator)
    
    # Revalidate
    manager.revalidate_dirty_roots(CONDUIT_ID)
    
    # Check validator called with dirty roots
    validator.assert_called_once()
    args, _ = validator.call_args
    assert args[0] == {"Root"}
    
    # Check state cleared
    assert not manager.is_root_dirty(CONDUIT_ID, "Root")
    assert not manager._monitor_active_by_conduit[CONDUIT_ID]

def test_revalidate_dirty_roots_partial(manager):
    """
    Verify partial revalidation only clears validated roots.

    Contract:
    - The revalidator may return a subset of roots that were validated.
    - Only validated roots are cleared; remaining roots stay dirty.
    """
    bp_a = MagicMock(spec=RootResolutionBlueprint)
    bp_a.dag.nodes.keys.return_value = ["LeafA"]
    bp_b = MagicMock(spec=RootResolutionBlueprint)
    bp_b.dag.nodes.keys.return_value = ["LeafB"]
    manager.rebuild_component_of(CONDUIT_ID, {"RootA": bp_a, "RootB": bp_b})

    manager.notify_spell_changed("LeafA")
    manager.notify_spell_changed("LeafB")

    validator = MagicMock(return_value={"RootA"})
    manager.set_revalidator(CONDUIT_ID, validator)

    manager.revalidate_dirty_roots(CONDUIT_ID)

    args, _ = validator.call_args
    assert args[0] == {"RootA", "RootB"}
    assert not manager.is_root_dirty(CONDUIT_ID, "RootA")
    assert manager.is_root_dirty(CONDUIT_ID, "RootB")
    assert manager._monitor_active_by_conduit[CONDUIT_ID]

def test_component_of_isolated_by_conduit(manager):
    """
    Purpose:
        Verify component-of maps do not overwrite across conduits.
    Contract:
        - rebuild_component_of for one conduit does not alter other conduits.
        - Each conduit retains its own root mappings.
    Returns:
        None.
    Raises:
        AssertionError: If conduit isolation is violated.
    """
    bp_a = MagicMock(spec=RootResolutionBlueprint)
    bp_a.dag.nodes.keys.return_value = ["LeafA"]
    bp_b = MagicMock(spec=RootResolutionBlueprint)
    bp_b.dag.nodes.keys.return_value = ["LeafB"]

    manager.rebuild_component_of("conduit-a", {"RootA": bp_a})
    manager.rebuild_component_of("conduit-b", {"RootB": bp_b})

    assert manager._component_of_by_conduit["conduit-a"]["LeafA"] == {"RootA"}
    assert manager._component_of_by_conduit["conduit-b"]["LeafB"] == {"RootB"}
    assert "LeafB" not in manager._component_of_by_conduit["conduit-a"]
    assert "LeafA" not in manager._component_of_by_conduit["conduit-b"]


def test_notify_spell_changed_scoped_to_conduit(manager):
    """
    Purpose:
        Verify dirty tracking only activates for conduits that map the spell id.
    Contract:
        - notify_spell_changed only marks conduits whose component-of map includes the spell.
    Returns:
        None.
    Raises:
        AssertionError: If dirty tracking bleeds across conduits.
    """
    bp_a = MagicMock(spec=RootResolutionBlueprint)
    bp_a.dag.nodes.keys.return_value = ["LeafA"]
    bp_b = MagicMock(spec=RootResolutionBlueprint)
    bp_b.dag.nodes.keys.return_value = ["LeafB"]

    manager.rebuild_component_of("conduit-a", {"RootA": bp_a})
    manager.rebuild_component_of("conduit-b", {"RootB": bp_b})

    manager.notify_spell_changed("LeafA")

    assert manager.is_root_dirty("conduit-a", "RootA")
    assert not manager.is_root_dirty("conduit-b", "RootB")
    assert manager._monitor_active_by_conduit["conduit-a"] is True
    assert manager._monitor_active_by_conduit["conduit-b"] is False


def test_revalidate_dirty_roots_scoped_to_conduit(manager):
    """
    Purpose:
        Verify revalidation only clears dirty roots for the requested conduit.
    Contract:
        - revalidate_dirty_roots calls the revalidator for the supplied conduit.
        - Other conduits retain their dirty state and do not invoke their validators.
    Returns:
        None.
    Raises:
        AssertionError: If revalidation affects other conduits.
    """
    bp_a = MagicMock(spec=RootResolutionBlueprint)
    bp_a.dag.nodes.keys.return_value = ["LeafA"]
    bp_b = MagicMock(spec=RootResolutionBlueprint)
    bp_b.dag.nodes.keys.return_value = ["LeafB"]

    manager.rebuild_component_of("conduit-a", {"RootA": bp_a})
    manager.rebuild_component_of("conduit-b", {"RootB": bp_b})

    manager.notify_spell_changed("LeafA")
    manager.notify_spell_changed("LeafB")

    validator_a = MagicMock(return_value={"RootA"})
    validator_b = MagicMock(return_value={"RootB"})
    manager.set_revalidator("conduit-a", validator_a)
    manager.set_revalidator("conduit-b", validator_b)

    manager.revalidate_dirty_roots("conduit-a")

    validator_a.assert_called_once()
    validator_b.assert_not_called()
    assert not manager.is_root_dirty("conduit-a", "RootA")
    assert manager.is_root_dirty("conduit-b", "RootB")

def test_revalidate_handles_cancel(manager):
    """
    Verify revalidation respects cancellation events.

    Contract:
    - The `cancel_event` is passed through to the revalidator callback.
    - If the callback or check raises due to cancellation, the state remains dirty.
    """
    validator = MagicMock()
    manager.set_revalidator(CONDUIT_ID, validator)
    
    cancel = MagicMock(spec=CancellationEvent)
    cancel.is_set = True
    cancel.throw_if_set.side_effect = InterruptedError("Cancelled")
    
    with pytest.raises(InterruptedError):
        manager.revalidate_dirty_roots(CONDUIT_ID, cancel_event=cancel)
    
    validator.assert_not_called()

def test_revalidate_does_nothing_if_clean(manager):
    """
    Verify revalidation is a no-op if there are no dirty roots.

    Contract:
    - Optimization: Do not call the revalidator if no dirty roots exist.
    """
    validator = MagicMock()
    manager.set_revalidator(CONDUIT_ID, validator)
    
    manager.revalidate_dirty_roots(CONDUIT_ID)
    validator.assert_not_called()


def test_default_structural_validator_resolves_spellbook_from_conduit_ids(manager, mock_sss):
    """
    Verify the default structural validator resolves staged bind targets.

    Contract:
    - `spellbook:` initiator ids are skipped during conduit resolution.
    - Conduit ids are used to resolve the owning Spellbook.
    - Only unresolved Phase-4 spells are passed to the post-conjure structural run.
    """
    spell_index = MagicMock(spec=ISpellIndex)
    spell = MagicMock()
    spell.validation_result_phase4 = None

    spellbook = MagicMock()
    spellbook._id = "spellbook-1"
    spellbook._conjured = True
    spellbook._lock = RLock()
    spellbook._lookup_spells = {("frame-a", "binding-a"): spell_index}
    spellbook._spells = {spell_index: spell}
    spellbook.check_cleaned = MagicMock()
    spellbook._run_post_conjure_structural_phases = MagicMock()

    conduit = MagicMock()
    conduit._spellbook = spellbook

    frame = MagicMock()
    frame._lock = RLock()
    frame._conduits = {"conduit-1": conduit}
    mock_sss._frame = frame

    staged = ChangeControlStagedMutation.from_request(
        request_id="req-structural-default",
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="spellbook:spellbook-1",
        spellbook_id="spellbook-1",
        conduit_ids=("conduit-1",),
        scope_keys=(),
        binding_keys=(("frame-a", "binding-a"), ("frame-a", "binding-a")),
        contract_keys=(),
        metadata=None,
    )

    manager._default_structural_validator(staged)

    spellbook._run_post_conjure_structural_phases.assert_called_once_with([spell])


def test_default_dirty_marker_marks_collection_and_contract_dependents(manager, mock_sss):
    """
    Verify the default dirty marker propagates collection and contract invalidation.

    Contract:
    - Binding and contract frame keys are unioned for collection invalidation.
    - Contract invalidation only includes complete `(frame_key, binding_key)` pairs.
    - Contract invalidation uses `SpellStateChangeReason.contract_unvalidated`.
    """
    staged = ChangeControlStagedMutation.from_request(
        request_id="req-dirty-marker-default",
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=("conduit-1",),
        scope_keys=(),
        binding_keys=(("frame-a", "binding-a"), ("frame-b", "binding-b")),
        contract_keys=(
            ("frame-a", "binding-a", "provider-a"),
            ("", "binding-ignored", "provider-b"),
            ("frame-c", "", "provider-c"),
        ),
        metadata=None,
    )

    manager._default_dirty_marker(staged)

    mock_sss.mark_collection_dependents_dirty.assert_called_once_with(
        spellbook_id="spellbook-1",
        frame_keys={"frame-a", "frame-b", "frame-c"},
    )
    mock_sss.mark_contract_dependents_dirty.assert_called_once_with(
        spellbook_id="spellbook-1",
        contract_keys={("frame-a", "binding-a")},
        change_reason=SpellStateChangeReason.contract_unvalidated,
    )


# ----------------------------------------------------------------------
# 4. Change-Control Admission Facade
# ----------------------------------------------------------------------

def test_change_control_manager_admit_request_disabled_accepts(manager) -> None:
    """
    Purpose:
        Validate admission bypass when change control is disabled.
    Contract:
        - disable_change_control accepts requests without conflict checks.
        - Request is tracked as in-flight and removed on commit.
    Returns:
        None.
    Raises:
        AssertionError: If admission or cleanup behavior is incorrect.
    """
    manager.disable_change_control()
    request = manager.transaction_manager().build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope-disabled"],
    )
    admission = manager.admit_request(request)
    assert admission.admitted is True
    assert manager.transaction_manager().get_in_flight(request.request_id) is request

    manager.commit_request(request.request_id)
    assert manager.transaction_manager().get_in_flight(request.request_id) is None


def test_change_control_manager_admit_request_enabled_tracks_in_flight(manager) -> None:
    """
    Purpose:
        Validate admission path when change control is enabled.
    Contract:
        - Enabled admission registers the request as in-flight.
        - Commit clears the in-flight request.
    Returns:
        None.
    Raises:
        AssertionError: If admission or cleanup behavior is incorrect.
    """
    manager.enable_change_control()
    request = manager.transaction_manager().build_request(
        request_type=ChangeTransactionType.LINK,
        initiator_conduit_id="conduit-2",
        scope_keys=["scope-enabled"],
    )
    admission = manager.admit_request(request)
    assert admission.admitted is True
    assert manager.transaction_manager().get_in_flight(request.request_id) is request

    manager.commit_request(request.request_id)
    assert manager.transaction_manager().get_in_flight(request.request_id) is None


def test_change_control_manager_commit_hook_invoked(manager) -> None:
    """
    Purpose:
        Validate commit hooks are invoked through the manager facade.
    Contract:
        - Commit hook receives the staged mutation when committing a request.
    Returns:
        None.
    Raises:
        AssertionError: If commit hook is not called.
    """
    called: list[str] = []

    def _hook(staged) -> None:
        called.append(staged.request_id)

    manager.set_commit_hook(_hook)
    request = manager.transaction_manager().build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = manager.admit_request(request)
    assert admission.admitted is True

    manager.commit_request(request.request_id)
    assert called == [request.request_id]


def test_change_control_manager_commit_validator_failure_aborts(manager) -> None:
    """
    Purpose:
        Validate commit validator failures trigger abort hooks and cleanup.
    Contract:
        - Validator errors propagate and clear in-flight state.
        - Abort hook is invoked for the staged mutation.
    Returns:
        None.
    Raises:
        AssertionError: If abort hook or cleanup does not occur.
    """
    abort_called: list[str] = []

    def _validator(staged) -> None:
        raise RuntimeError("validation failed")

    def _abort_hook(staged) -> None:
        abort_called.append(staged.request_id)

    manager.set_commit_validator(_validator)
    manager.set_abort_hook(_abort_hook)
    request = manager.transaction_manager().build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = manager.admit_request(request)
    assert admission.admitted is True

    with pytest.raises(RuntimeError):
        manager.commit_request(request.request_id)
    assert manager.transaction_manager().get_in_flight(request.request_id) is None
    assert abort_called == [request.request_id]


def test_change_control_manager_structural_validator_precedes_commit_validator(manager) -> None:
    """
    Purpose:
        Validate structural validators run before commit validators.
    Contract:
        - Structural validator is invoked before commit validator.
    Returns:
        None.
    Raises:
        AssertionError: If validator ordering is incorrect.
    """
    events: list[str] = []

    def _structural(staged: ChangeControlStagedMutation) -> None:
        events.append("structural")

    def _validator(staged: ChangeControlStagedMutation) -> None:
        events.append("validator")

    manager.set_structural_validator(_structural)
    manager.set_commit_validator(_validator)

    staged = ChangeControlStagedMutation.from_request(
        request_id="req-structural",
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=(),
        scope_keys=(),
        binding_keys=(),
        contract_keys=(),
        metadata=None,
    )
    manager._dispatch_commit_validator(staged)

    assert events == ["structural", "validator"]


def test_change_control_manager_dirty_marker_precedes_commit_hook(manager) -> None:
    """
    Purpose:
        Validate dirty markers run before commit hooks.
    Contract:
        - Dirty marker is invoked before commit hook.
    Returns:
        None.
    Raises:
        AssertionError: If hook ordering is incorrect.
    """
    events: list[str] = []

    def _marker(staged: ChangeControlStagedMutation) -> None:
        events.append("marker")

    def _hook(staged: ChangeControlStagedMutation) -> None:
        events.append("hook")

    manager.set_dirty_marker(_marker)
    manager.set_commit_hook(_hook)

    staged = ChangeControlStagedMutation.from_request(
        request_id="req-marker",
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        conduit_ids=(),
        scope_keys=(),
        binding_keys=(),
        contract_keys=(),
        metadata=None,
    )
    manager._dispatch_commit_hook(staged)

    assert events == ["marker", "hook"]


def test_change_control_manager_update_staged_request_updates_metadata(manager) -> None:
    """
    Purpose:
        Validate staged metadata updates after admission.
    Contract:
        - update_staged_request returns True when the request is staged.
        - Updated binding keys and metadata are reflected in the staged record.
        - Metadata updates merge into existing staged metadata.
    Returns:
        None.
    Raises:
        AssertionError: If staged metadata is not updated.
    """
    request = manager.transaction_manager().build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
        metadata={"seed": "value"},
    )
    admission = manager.admit_request(request)
    assert admission.admitted is True

    updated = manager.update_staged_request(
        request.request_id,
        binding_keys=[("frame", "__default__")],
        metadata={"note": "test"},
    )
    assert updated is True

    staged = manager.orchestrator().get_staged(request.request_id)
    assert staged is not None
    assert staged.binding_keys == (("frame", "__default__"),)
    assert staged.metadata["seed"] == "value"
    assert staged.metadata["note"] == "test"


def test_change_control_manager_update_staged_request_extends_embargoes(manager) -> None:
    """
    Purpose:
        Validate staged updates extend implicit embargo scopes.
    Contract:
        - Updating binding keys adds the derived binding scope to embargoes.
    Returns:
        None.
    Raises:
        AssertionError: If embargo scopes do not update.
    """
    request = manager.transaction_manager().build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        spellbook_id="spellbook-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = manager.admit_request(request)
    assert admission.admitted is True

    embargo_manager = manager.embargo_manager()
    embargoed_before = set(embargo_manager.describe()["embargoed_scopes"])
    assert "binding:frame:__default__" not in embargoed_before

    updated = manager.update_staged_request(
        request.request_id,
        binding_keys=[("frame", "__default__")],
    )
    assert updated is True

    embargoed_after = set(embargo_manager.describe()["embargoed_scopes"])
    assert "binding:frame:__default__" in embargoed_after


def test_change_control_manager_update_staged_request_noops_when_disabled(manager) -> None:
    """
    Purpose:
        Validate staged updates are disabled when change control is disabled.
    Contract:
        - update_staged_request returns False when staging is not active.
    Returns:
        None.
    Raises:
        AssertionError: If update_staged_request returns True while disabled.
    """
    manager.disable_change_control()
    request = manager.transaction_manager().build_request(
        request_type=ChangeTransactionType.BIND,
        initiator_conduit_id="conduit-1",
        scope_keys=["scope:spellbook:spellbook-1"],
    )
    admission = manager.admit_request(request)
    assert admission.admitted is True

    updated = manager.update_staged_request(
        request.request_id,
        binding_keys=[("frame", "__default__")],
    )
    assert updated is False



def test_revalidate_keeps_dirty_on_failure(manager):
    """
    Verify dirty state is preserved if revalidation fails.

    Contract:
    - If the revalidator raises an exception, the dirty roots must NOT be cleared.
    - The exception propagates to the caller.
    """
    # Setup dirty
    bp = MagicMock(spec=RootResolutionBlueprint)
    bp.dag.nodes.keys.return_value = ["Leaf"]
    manager.rebuild_component_of(CONDUIT_ID, {"Root": bp})
    manager.notify_spell_changed("Leaf")
    
    # Validator fails
    validator = MagicMock(side_effect=ValueError("Fail"))
    manager.set_revalidator(CONDUIT_ID, validator)
    
    with pytest.raises(ValueError):
        manager.revalidate_dirty_roots(CONDUIT_ID)
        
    # Should still be dirty
    assert manager.is_root_dirty(CONDUIT_ID, "Root")

# ----------------------------------------------------------------------
# 4. Cleanup
# ----------------------------------------------------------------------

def test_cleanup_clears_state(manager):
    """
    Verify `cleanup` removes all internal state and references.

    Contract:
    - All internal collections (pending changes, component maps, dirty sets) must be nulled.
    - References to external objects (spell system states) must be dropped.
    - The `_cleaned` flag must be set.
    """
    manager.register_pending_change(MagicMock(id="s1"), "r")
    manager.notify_spell_changed("s1")
    
    manager.cleanup()
    
    assert manager._cleaned
    assert manager._pending_changes is None
    assert manager._component_of_by_conduit is None
    assert manager._spell_system_states is None
    assert manager._revalidate_fn_by_conduit is None

def test_methods_raise_after_cleanup(manager, mock_spell_index):
    """
    Verify public methods raise `RuntimeError` after cleanup.

    Contract:
    - Accessing any functional method on a cleaned manager is strictly forbidden.
    """
    manager.cleanup()
    
    with pytest.raises(RuntimeError):
        manager.register_pending_change(mock_spell_index, "r")
        
    with pytest.raises(RuntimeError):
        manager.get_pending_change("id")
        
    with pytest.raises(RuntimeError):
        manager.rebuild_component_of(CONDUIT_ID, {})

def test_cleanup_idempotent(manager):
    """
    Verify `cleanup` is safe to call multiple times.

    Contract:
    - Subsequent calls to `cleanup` must be no-ops and not raise exceptions.
    """
    manager.cleanup()
    manager.cleanup() # Should not raise

# ----------------------------------------------------------------------
# 5. Describe / Introspection
# ----------------------------------------------------------------------

def test_describe(manager, mock_spell_index):
    """
    Verify `describe` returns a complete diagnostic snapshot.

    Contract:
    - The returned dictionary must contain keys for all major state components
      (pending_changes, dirty_spells_by_conduit, dirty_roots_by_conduit,
      component_of_by_conduit, etc.).
    """
    manager.register_pending_change(mock_spell_index, "reason")
    bp = MagicMock(spec=RootResolutionBlueprint)
    bp.dag.nodes.keys.return_value = ["s1"]
    manager.rebuild_component_of(CONDUIT_ID, {"s1": bp})
    manager.notify_spell_changed("s1")
    
    info = manager.describe()
    assert "spell-123" in info["pending_changes"]
    assert "s1" in info["dirty_spells_by_conduit"][CONDUIT_ID]
    assert info["monitor_active_by_conduit"][CONDUIT_ID] is True

def test_rebuild_component_of_empty(manager):
    """Verify rebuilding with empty blueprints clears everything."""
    manager.rebuild_component_of(CONDUIT_ID, {})
    assert manager.describe()["component_of_by_conduit"][CONDUIT_ID] == {}
    assert not manager._dirty_roots_by_conduit[CONDUIT_ID]

def test_rebuild_component_of_disjoint_graphs(manager):
    """Verify handling of multiple disjoint DAGs."""
    bp1 = MagicMock(spec=RootResolutionBlueprint)
    bp1.dag.nodes.keys.return_value = ["A", "B"]
    
    bp2 = MagicMock(spec=RootResolutionBlueprint)
    bp2.dag.nodes.keys.return_value = ["C", "D"]
    
    manager.rebuild_component_of(CONDUIT_ID, {"R1": bp1, "R2": bp2})
    
    manager.notify_spell_changed("B")
    assert manager.is_root_dirty(CONDUIT_ID, "R1")
    assert not manager.is_root_dirty(CONDUIT_ID, "R2")
    
    manager.notify_spell_changed("D")
    assert manager.is_root_dirty(CONDUIT_ID, "R2")

def test_notify_spell_changed_unknown_spell(manager):
    """Verify notifying a spell not in the map does not add dirty state."""
    bp = MagicMock(spec=RootResolutionBlueprint)
    bp.dag.nodes.keys.return_value = ["Known"]
    manager.rebuild_component_of(CONDUIT_ID, {"Known": bp})

    manager.notify_spell_changed("GhostSpell")
    assert "GhostSpell" not in manager._dirty_spells_by_conduit[CONDUIT_ID]
    assert not manager._dirty_roots_by_conduit[CONDUIT_ID]

def test_notify_provider_changed_alias(manager):
    """Verify notify_provider_changed aliases notify_spell_changed (side effects)."""
    bp = MagicMock(spec=RootResolutionBlueprint)
    bp.dag.nodes.keys.return_value = ["spell-alias"]
    manager.rebuild_component_of(CONDUIT_ID, {"spell-alias": bp})

    manager.notify_provider_changed("spell-alias")
    assert "spell-alias" in manager._dirty_spells_by_conduit[CONDUIT_ID]
    assert manager._monitor_active_by_conduit[CONDUIT_ID]

def test_is_root_dirty_false_if_not_active(manager):
    """Verify returns False if monitor is not active, even if requested."""
    # Force dirty roots but inactive monitor (unlikely state, but possible via manual manipulation)
    with manager._lock:
        manager._dirty_roots_by_conduit.setdefault(CONDUIT_ID, set()).add("R1")
        manager._monitor_active_by_conduit[CONDUIT_ID] = False
        
    assert not manager.is_root_dirty(CONDUIT_ID, "R1")

def test_is_root_dirty_none_input(manager):
    """Verify `is_root_dirty` handles None/empty inputs gracefully (returns False)."""
    assert not manager.is_root_dirty("", "root")
    assert not manager.is_root_dirty(CONDUIT_ID, "")

def test_set_revalidator_none_check(manager):
    """Verify `set_revalidator` raises ValueError if callback is None."""
    with pytest.raises(ValueError, match="revalidator fn must not be None"):
        manager.set_revalidator(CONDUIT_ID, None)

def test_concurrency_register_change(manager, mock_spell_index):
    """Verify multiple threads registering changes works safely."""
    import threading
    
    def worker(i):
        manager.register_pending_change(mock_spell_index, f"reason-{i}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    # Last write wins, but dictionary should be intact
    assert manager.get_pending_change("spell-123") is not None

def test_describe_isolation(manager):
    """Verify describe returns a detached structure."""
    info = manager.describe()
    info["pending_changes"]["hacked"] = True
    assert "hacked" not in manager._pending_changes

def test_pending_changes_nested_isolation(manager, mock_spell_index):
    """Verify metadata is shallow-copied, but we rely on discipline for deep changes."""
    meta = {"nested": {"a": 1}}
    manager.register_pending_change(mock_spell_index, "r", meta)
    
    stored = manager.get_pending_change("spell-123")
    stored["nested"]["a"] = 2
    
    # get_pending_change returns a dict(entry), so 'nested' is shared reference
    # if the implementation uses simple dict(). 
    # Let's verify the implementation behavior.
    # The impl: `return dict(entry)`
    # So top level is new, values are shared.
    
    raw_again = manager.get_pending_change("spell-123")
    # If standard dict shallow copy:
    assert raw_again["nested"]["a"] == 2 


