import pytest

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import (
    ChangeControlManager,
    ChangeTransactionType,
)
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_crafter.system.spell_system_adjacency_builder import (
    SpellSystemAdjacencyBuilder,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import (
    SpellSystemRootBlueprintBuilder,
)
from melder.utilities.custom_exceptions.operation_cancelled_error import (
    OperationCancelledError,
)
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEventSignal,
)

CONDUIT_ID = "conduit-1"


def _register_index(states, spell_id: str) -> SpellIndex:
    """
    Purpose:
        Register a SpellIndex lineage in SpellSystemStates for component tests.
    Contract:
        - Returns a SpellIndex whose current id matches spell_id.
        - Registers a state entry for the lineage.
    Args:
        states: SpellSystemStates registry.
        spell_id: Version id to register as current.
    Returns:
        SpellIndex: The created spell index instance.
    """
    index = SpellIndex(spell_id)
    states.register_index(index, object())
    return index


def _build_root_blueprints(states) -> dict[str, object]:
    """
    Purpose:
        Build root blueprints from the current SpellSystemStates snapshot.
    Contract:
        - Returns a mapping keyed by root spell id.
    Args:
        states: SpellSystemStates registry to snapshot.
    Returns:
        dict[str, RootResolutionBlueprint]: Root blueprint mapping.
    """
    snapshot = SpellSystemAdjacencyBuilder.build(states)
    return SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)


def _cleanup_blueprints(blueprints: dict[str, object]) -> None:
    """
    Purpose:
        Deterministically clean RootResolutionBlueprint objects.
    Contract:
        - Invokes cleanup on each blueprint in the mapping.
    Args:
        blueprints: Mapping of root ids to RootResolutionBlueprint objects.
    Returns:
        None.
    """
    for blueprint in blueprints.values():
        blueprint.cleanup()


def test_component_change_control_rebuild_component_of_maps_root_and_dependency() -> None:
    """
    Purpose:
        Validate component-of mapping from real root blueprints.
    Contract:
        - Root spell ids map to themselves.
        - Dependency spell ids map back to the root.
    Returns:
        None.
    Raises:
        AssertionError: If component-of mappings are missing.
    """
    frame = AethericFrame(Aether(), "component-ccm-mapping")
    states = frame.spell_system_states
    root_id = "root-ccm"
    dep_id = "dep-ccm"
    root_index = _register_index(states, root_id)
    _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = ChangeControlManager(states)
    blueprints: dict[str, object] = {}
    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(CONDUIT_ID, blueprints)
        info = manager.describe()
        component_of = info["component_of_by_conduit"][CONDUIT_ID]
        assert component_of[root_id] == {root_id}
        assert component_of[dep_id] == {root_id}
    finally:
        _cleanup_blueprints(blueprints)
        manager.cleanup()
        frame.cleanup()


def test_component_change_control_includes_deep_dependencies() -> None:
    """
    Purpose:
        Validate deep dependencies are attributed to the root.
    Contract:
        - Leaf nodes map to the root spell id in component_of.
    Returns:
        None.
    Raises:
        AssertionError: If deep dependencies are not mapped.
    """
    frame = AethericFrame(Aether(), "component-ccm-deep")
    states = frame.spell_system_states
    root_id = "root-deep"
    mid_id = "mid-deep"
    leaf_id = "leaf-deep"
    root_index = _register_index(states, root_id)
    mid_index = _register_index(states, mid_id)
    _register_index(states, leaf_id)
    states.update_dependencies(root_index, [mid_id])
    states.update_dependencies(mid_index, [leaf_id])

    manager = ChangeControlManager(states)
    blueprints: dict[str, object] = {}
    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(CONDUIT_ID, blueprints)
        component_of = manager.describe()["component_of_by_conduit"][CONDUIT_ID]
        assert component_of[root_id] == {root_id}
        assert component_of[mid_id] == {root_id}
        assert component_of[leaf_id] == {root_id}
    finally:
        _cleanup_blueprints(blueprints)
        manager.cleanup()
        frame.cleanup()


def test_component_change_control_revalidate_dirty_roots_uses_blueprint_roots() -> None:
    """
    Purpose:
        Validate revalidation clears dirty roots derived from blueprints.
    Contract:
        - notify_spell_changed marks the root dirty.
        - revalidate_dirty_roots invokes the registered revalidator.
        - Dirty roots are cleared after revalidation.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are not cleared.
    """
    frame = AethericFrame(Aether(), "component-ccm-revalidate")
    states = frame.spell_system_states
    root_id = "root-revalidate"
    dep_id = "dep-revalidate"
    root_index = _register_index(states, root_id)
    _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = ChangeControlManager(states)
    calls: list[set[str]] = []
    blueprints: dict[str, object] = {}

    def _revalidate(dirty_roots: set[str], _cancel_event) -> None:
        """
        Purpose:
            Capture dirty root ids passed by ChangeControlManager.
        Contract:
            - Appends the dirty_roots set for assertions.
        Args:
            dirty_roots: Root ids marked dirty by change control.
            _cancel_event: Optional cancellation event (unused).
        Returns:
            None.
        """
        calls.append(set(dirty_roots))

    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(CONDUIT_ID, blueprints)
        manager.set_revalidator(CONDUIT_ID, _revalidate)

        manager.notify_spell_changed(dep_id)
        assert manager.is_root_dirty(CONDUIT_ID, root_id) is True

        manager.revalidate_dirty_roots(CONDUIT_ID)
        assert calls == [{root_id}]
        info = manager.describe()
        assert info["dirty_roots_by_conduit"][CONDUIT_ID] == set()
        assert info["monitor_active_by_conduit"][CONDUIT_ID] is False
    finally:
        _cleanup_blueprints(blueprints)
        manager.cleanup()
        frame.cleanup()


def test_component_change_control_pending_change_round_trip() -> None:
    """
    Purpose:
        Validate pending-change metadata round-trips through real components.
    Contract:
        - register_pending_change stores the reason and metadata.
        - get_pending_change returns a snapshot copy.
        - list_pending_changes includes the entry.
        - clear_pending_change removes it.
    Returns:
        None.
    Raises:
        AssertionError: If pending-change tracking is incorrect.
    """
    frame = AethericFrame(Aether(), "component-ccm-pending")
    states = frame.spell_system_states
    manager = frame.dev_ops_manager.change_control_manager
    index = SpellIndex("spell-pending-change")
    states.register_index(index, object())
    try:
        manager.register_pending_change(
            index,
            reason="rebinding",
            metadata={"ticket": "T-100"},
        )
        entry = manager.get_pending_change(index.id)
        assert entry is not None
        assert entry["reason"] == "rebinding"
        assert entry["ticket"] == "T-100"
        snapshot = manager.list_pending_changes()
        assert index.id in snapshot

        entry["ticket"] = "mutated"
        fresh = manager.get_pending_change(index.id)
        assert fresh is not None
        assert fresh["ticket"] == "T-100"

        manager.clear_pending_change(index.id)
        assert manager.get_pending_change(index.id) is None
    finally:
        frame.cleanup()


def test_component_change_control_admit_request_disabled_tracks_in_flight() -> None:
    """
    Purpose:
        Validate admission bypass when change-control is disabled.
    Contract:
        - admit_request returns admitted when disabled.
        - Request is tracked as in-flight.
        - No staged mutation is recorded.
    Returns:
        None.
    Raises:
        AssertionError: If in-flight or staging state is incorrect.
    """
    frame = AethericFrame(Aether(), "component-ccm-disabled-admit")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        manager.disable_change_control()
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:spellbook:spellbook-1"],
        )
        admission = manager.admit_request(request)
        assert admission.admitted is True
        assert manager.transaction_manager().get_in_flight(request.request_id) is request
        assert manager.orchestrator().get_staged(request.request_id) is None
    finally:
        frame.cleanup()


def test_component_change_control_update_staged_request_disabled_returns_false() -> None:
    """
    Purpose:
        Validate staged updates are ignored when change-control is disabled.
    Contract:
        - update_staged_request returns False when disabled.
    Returns:
        None.
    Raises:
        AssertionError: If disabled updates return True.
    """
    frame = AethericFrame(Aether(), "component-ccm-update-disabled")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        manager.disable_change_control()
        assert manager.update_staged_request("missing") is False
    finally:
        frame.cleanup()


def test_component_change_control_commit_request_disabled_removes_in_flight() -> None:
    """
    Purpose:
        Validate commit removes in-flight state when disabled.
    Contract:
        - commit_request clears the in-flight entry when change-control is disabled.
    Returns:
        None.
    Raises:
        AssertionError: If in-flight state remains after commit.
    """
    frame = AethericFrame(Aether(), "component-ccm-commit-disabled")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        manager.disable_change_control()
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:spellbook:spellbook-1"],
        )
        manager.admit_request(request)
        manager.commit_request(request.request_id)
        assert manager.transaction_manager().get_in_flight(request.request_id) is None
    finally:
        frame.cleanup()


def test_component_change_control_abort_request_disabled_removes_in_flight() -> None:
    """
    Purpose:
        Validate abort removes in-flight state when disabled.
    Contract:
        - abort_request clears the in-flight entry when change-control is disabled.
    Returns:
        None.
    Raises:
        AssertionError: If in-flight state remains after abort.
    """
    frame = AethericFrame(Aether(), "component-ccm-abort-disabled")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        manager.disable_change_control()
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.LINK,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:conduit:conduit-1"],
        )
        manager.admit_request(request)
        manager.abort_request(request.request_id)
        assert manager.transaction_manager().get_in_flight(request.request_id) is None
    finally:
        frame.cleanup()


def test_component_change_control_update_staged_request_extends_embargoes() -> None:
    """
    Purpose:
        Validate staged updates extend implicit embargo scopes.
    Contract:
        - update_staged_request adds embargoes derived from new binding keys.
    Returns:
        None.
    Raises:
        AssertionError: If embargo scopes are not extended.
    """
    frame = AethericFrame(Aether(), "component-ccm-update-embargo")
    manager = frame.dev_ops_manager.change_control_manager
    try:
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
        assert updated is True

        binding_scope = manager.transaction_manager().make_scope_key_binding(
            "frame",
            "__default__",
        )
        embargoes = manager.embargo_manager().find_embargoes([binding_scope])
        assert embargoes == (binding_scope,)
    finally:
        frame.cleanup()


def test_component_change_control_commit_hook_runs_after_dirty_marker() -> None:
    """
    Purpose:
        Validate commit hook dispatch order for staged mutations.
    Contract:
        - Dirty marker runs before the commit hook.
    Returns:
        None.
    Raises:
        AssertionError: If hook order is incorrect.
    """
    frame = AethericFrame(Aether(), "component-ccm-commit-hook-order")
    manager = frame.dev_ops_manager.change_control_manager
    calls: list[str] = []

    def _marker(_staged) -> None:
        calls.append("marker")

    def _hook(_staged) -> None:
        calls.append("hook")

    try:
        manager.set_dirty_marker(_marker)
        manager.set_commit_hook(_hook)
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:spellbook:spellbook-1"],
        )
        admission = manager.admit_request(request)
        assert admission.admitted is True

        manager.commit_request(request.request_id)
        assert calls == ["marker", "hook"]
    finally:
        frame.cleanup()


def test_component_change_control_commit_validator_runs_structural_first() -> None:
    """
    Purpose:
        Validate structural validation runs before commit validators.
    Contract:
        - Structural validator executes before commit validator.
    Returns:
        None.
    Raises:
        AssertionError: If validator order is incorrect.
    """
    frame = AethericFrame(Aether(), "component-ccm-commit-validator-order")
    manager = frame.dev_ops_manager.change_control_manager
    calls: list[str] = []

    def _structural(_staged) -> None:
        calls.append("structural")

    def _validator(_staged) -> None:
        calls.append("validator")

    try:
        manager.set_structural_validator(_structural)
        manager.set_commit_validator(_validator)
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:spellbook:spellbook-1"],
        )
        admission = manager.admit_request(request)
        assert admission.admitted is True

        manager.commit_request(request.request_id)
        assert calls == ["structural", "validator"]
    finally:
        frame.cleanup()


def test_component_change_control_describe_includes_manager_snapshots() -> None:
    """
    Purpose:
        Validate describe returns manager snapshot metadata.
    Contract:
        - transaction_manager and embargo_manager snapshots are present.
        - Embargo count reflects admitted requests.
    Returns:
        None.
    Raises:
        AssertionError: If describe omits manager snapshots.
    """
    frame = AethericFrame(Aether(), "component-ccm-describe")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:spellbook:spellbook-1"],
        )
        manager.admit_request(request)
        info = manager.describe()
        assert info["transaction_manager"] is not None
        assert info["embargo_manager"] is not None
        assert info["embargo_manager"]["embargo_count"] == 1
    finally:
        frame.cleanup()


def test_component_change_control_admit_request_scope_hash_conflict() -> None:
    """
    Purpose:
        Validate scope-hash conflicts are detected in admission.
    Contract:
        - Request with overlapping hash is denied.
        - Conflict evidence contains the first request id.
    Returns:
        None.
    Raises:
        AssertionError: If hash conflicts are not enforced.
    """
    frame = AethericFrame(Aether(), "component-ccm-hash-conflict")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        request_a = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-a",
            scope_keys=["scope:shared"],
        )
        request_b = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-b",
            scope_hashes=request_a.scope_hashes,
        )
        assert manager.admit_request(request_a).admitted is True
        admission_b = manager.admit_request(request_b)
        assert admission_b.admitted is False
        assert admission_b.conflicts == (request_a.request_id,)
    finally:
        frame.cleanup()


def test_component_change_control_commit_clears_staged_record() -> None:
    """
    Purpose:
        Validate commit removes staged mutation entries.
    Contract:
        - Staged entry exists after admission.
        - commit_request clears the staged record.
    Returns:
        None.
    Raises:
        AssertionError: If staged entries persist after commit.
    """
    frame = AethericFrame(Aether(), "component-ccm-commit-staged")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:spellbook:spellbook-1"],
        )
        manager.admit_request(request)
        assert manager.orchestrator().get_staged(request.request_id) is not None
        manager.commit_request(request.request_id)
        assert manager.orchestrator().get_staged(request.request_id) is None
    finally:
        frame.cleanup()


def test_component_change_control_abort_clears_staged_record() -> None:
    """
    Purpose:
        Validate abort removes staged mutation entries.
    Contract:
        - Staged entry exists after admission.
        - abort_request clears the staged record.
    Returns:
        None.
    Raises:
        AssertionError: If staged entries persist after abort.
    """
    frame = AethericFrame(Aether(), "component-ccm-abort-staged")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:spellbook:spellbook-1"],
        )
        manager.admit_request(request)
        assert manager.orchestrator().get_staged(request.request_id) is not None
        manager.abort_request(request.request_id)
        assert manager.orchestrator().get_staged(request.request_id) is None
    finally:
        frame.cleanup()


def test_component_change_control_update_staged_merges_metadata() -> None:
    """
    Purpose:
        Validate staged metadata updates merge rather than replace.
    Contract:
        - Metadata from admission remains after update.
        - New metadata keys are merged into the staged record.
    Returns:
        None.
    Raises:
        AssertionError: If metadata is not merged.
    """
    frame = AethericFrame(Aether(), "component-ccm-staged-metadata")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-1",
            scope_keys=["scope:spellbook:spellbook-1"],
            metadata={"origin": "admit"},
        )
        manager.admit_request(request)
        assert manager.update_staged_request(
            request.request_id,
            metadata={"ticket": "T-200"},
        )
        staged = manager.orchestrator().get_staged(request.request_id)
        assert staged is not None
        assert staged.metadata["origin"] == "admit"
        assert staged.metadata["ticket"] == "T-200"
    finally:
        frame.cleanup()

def test_component_change_control_admit_request_rejects_conflict() -> None:
    """
    Purpose:
        Validate admission rejects requests with overlapping scope keys.
    Contract:
        - Second admission is denied with conflict evidence.
        - In-flight registry retains only the first request.
    Returns:
        None.
    Raises:
        AssertionError: If conflict admission is not enforced.
    """
    frame = AethericFrame(Aether(), "component-ccm-conflict")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        request_a = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-a",
            scope_keys=["scope:shared"],
        )
        request_b = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-b",
            scope_keys=["scope:shared"],
        )

        admission_a = manager.admit_request(request_a)
        admission_b = manager.admit_request(request_b)
        assert admission_a.admitted is True
        assert admission_b.admitted is False
        assert admission_b.conflicts == (request_a.request_id,)
        assert manager.transaction_manager().list_in_flight() == [request_a]
    finally:
        frame.cleanup()


def test_component_change_control_admit_request_rejects_embargo() -> None:
    """
    Purpose:
        Validate embargoed scopes block admission.
    Contract:
        - Second admission is denied with embargo evidence.
        - Conflict evidence remains empty when scopes do not overlap.
    Returns:
        None.
    Raises:
        AssertionError: If embargo admission is not enforced.
    """
    frame = AethericFrame(Aether(), "component-ccm-embargo")
    manager = frame.dev_ops_manager.change_control_manager
    binding_scope = manager.transaction_manager().make_scope_key_binding(
        "frame",
        "__default__",
    )
    try:
        request_a = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-a",
            binding_keys=[("frame", "__default__")],
        )
        request_b = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-b",
            scope_keys=[binding_scope],
        )
        assert manager.admit_request(request_a).admitted is True
        admission_b = manager.admit_request(request_b)
        assert admission_b.admitted is False
        assert admission_b.conflicts == ()
        assert admission_b.embargoes == (binding_scope,)
    finally:
        frame.cleanup()


def test_component_change_control_abort_request_releases_embargoes() -> None:
    """
    Purpose:
        Validate abort releases implicit embargoes for a request.
    Contract:
        - Embargo scopes are present after admission.
        - abort_request clears embargoes and in-flight state.
    Returns:
        None.
    Raises:
        AssertionError: If embargoes remain after abort.
    """
    frame = AethericFrame(Aether(), "component-ccm-abort-embargo")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        request = manager.transaction_manager().build_request(
            request_type=ChangeTransactionType.BIND,
            initiator_conduit_id="conduit-a",
            scope_keys=["scope:spellbook:spellbook-1"],
        )
        assert manager.admit_request(request).admitted is True
        assert manager.embargo_manager().describe()["embargo_count"] == 1

        manager.abort_request(request.request_id)
        assert manager.transaction_manager().list_in_flight() == []
        assert manager.embargo_manager().describe()["embargo_count"] == 0
    finally:
        frame.cleanup()


def test_component_change_control_notify_unknown_spell_tracks_dirty() -> None:
    """
    Purpose:
        Validate unknown spell ids do not mark dirty state without mappings.
    Contract:
        - notify_spell_changed leaves dirty state empty without component_of mappings.
    Returns:
        None.
    Raises:
        AssertionError: If dirty tracking is incorrect.
    """
    frame = AethericFrame(Aether(), "component-ccm-unknown")
    manager = frame.dev_ops_manager.change_control_manager
    try:
        manager.rebuild_component_of(CONDUIT_ID, {})
        manager.notify_spell_changed("ghost-spell")
        info = manager.describe()
        assert info["dirty_spells_by_conduit"][CONDUIT_ID] == set()
        assert info["dirty_roots_by_conduit"][CONDUIT_ID] == set()
        assert info["monitor_active_by_conduit"][CONDUIT_ID] is False
    finally:
        frame.cleanup()


def test_component_change_control_revalidate_dirty_roots_failure_keeps_dirty() -> None:
    """
    Purpose:
        Validate dirty roots remain when revalidation fails.
    Contract:
        - revalidate_dirty_roots propagates the revalidator exception.
        - dirty roots stay marked after failure.
        - monitor_active remains True.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are cleared after failure.
    """
    frame = AethericFrame(Aether(), "component-ccm-revalidate-failure")
    states = frame.spell_system_states
    root_id = "root-ccm-failure"
    dep_id = "dep-ccm-failure"
    root_index = _register_index(states, root_id)
    _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = frame.dev_ops_manager.change_control_manager
    blueprints: dict[str, object] = {}

    def _revalidate(_dirty_roots, _cancel_event) -> None:
        raise RuntimeError("revalidate failed")

    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(CONDUIT_ID, blueprints)
        manager.set_revalidator(CONDUIT_ID, _revalidate)

        manager.notify_spell_changed(dep_id)
        assert manager.is_root_dirty(CONDUIT_ID, root_id) is True

        with pytest.raises(RuntimeError, match="revalidate failed"):
            manager.revalidate_dirty_roots(CONDUIT_ID)

        info = manager.describe()
        assert root_id in info["dirty_roots_by_conduit"][CONDUIT_ID]
        assert info["monitor_active_by_conduit"][CONDUIT_ID] is True
    finally:
        _cleanup_blueprints(blueprints)
        frame.cleanup()


def test_component_change_control_revalidate_dirty_roots_no_revalidator_noop() -> None:
    """
    Purpose:
        Validate revalidation is a no-op when no revalidator is registered.
    Contract:
        - Dirty roots remain marked when revalidate_dirty_roots is called without a hook.
        - monitor_active remains True.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are cleared without a revalidator.
    """
    frame = AethericFrame(Aether(), "component-ccm-revalidate-no-hook")
    states = frame.spell_system_states
    root_id = "root-ccm-no-hook"
    dep_id = "dep-ccm-no-hook"
    root_index = _register_index(states, root_id)
    _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = frame.dev_ops_manager.change_control_manager
    blueprints: dict[str, object] = {}

    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(CONDUIT_ID, blueprints)
        manager.notify_spell_changed(dep_id)
        assert manager.is_root_dirty(CONDUIT_ID, root_id) is True

        manager.revalidate_dirty_roots(CONDUIT_ID)
        info = manager.describe()
        assert root_id in info["dirty_roots_by_conduit"][CONDUIT_ID]
        assert info["monitor_active_by_conduit"][CONDUIT_ID] is True
    finally:
        _cleanup_blueprints(blueprints)
        frame.cleanup()


def test_component_change_control_revalidate_dirty_roots_respects_cancellation() -> None:
    """
    Purpose:
        Validate cancellation aborts revalidation before the callback runs.
    Contract:
        - cancel_event throws before revalidator is called.
        - dirty roots remain marked and monitoring stays active.
    Returns:
        None.
    Raises:
        AssertionError: If cancellation does not abort the revalidation.
    """
    frame = AethericFrame(Aether(), "component-ccm-cancel")
    states = frame.spell_system_states
    root_id = "root-ccm-cancel"
    dep_id = "dep-ccm-cancel"
    root_index = _register_index(states, root_id)
    _register_index(states, dep_id)
    states.update_dependencies(root_index, [dep_id])

    manager = frame.dev_ops_manager.change_control_manager
    blueprints: dict[str, object] = {}
    calls: list[set[str]] = []

    def _revalidate(dirty_roots: set[str], _cancel_event) -> None:
        calls.append(set(dirty_roots))

    signal = CancellationEventSignal()

    try:
        blueprints = _build_root_blueprints(states)
        manager.rebuild_component_of(CONDUIT_ID, blueprints)
        manager.set_revalidator(CONDUIT_ID, _revalidate)
        manager.notify_spell_changed(dep_id)
        assert manager.is_root_dirty(CONDUIT_ID, root_id) is True

        signal.cancel()
        with pytest.raises(OperationCancelledError):
            manager.revalidate_dirty_roots(CONDUIT_ID, cancel_event=signal.event)

        assert calls == []
        info = manager.describe()
        assert root_id in info["dirty_roots_by_conduit"][CONDUIT_ID]
        assert info["monitor_active_by_conduit"][CONDUIT_ID] is True
    finally:
        signal.cleanup()
        _cleanup_blueprints(blueprints)
        frame.cleanup()


