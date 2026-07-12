from typing import List, Tuple

import pytest

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.notch_transaction_strategy import (
    NotchTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.add_to_index_transaction_strategy import (
    AddToIndexTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.remove_from_index_transaction_strategy import (
    RemoveFromIndexTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.elect_conduit_cluster_leader_transaction_strategy import (
    ElectConduitClusterLeaderTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.unelect_conduit_cluster_leader_transaction_strategy import (
    UnelectConduitClusterLeaderTransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
    ChangeControlTransactionManager,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ClaimMode,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _manager_and_registry() -> Tuple[ChangeControlTransactionManager, DevopsInformationRegistry]:
    """Return a fresh transaction manager + registry for one frame."""
    return ChangeControlTransactionManager(), DevopsInformationRegistry("frame-1")


def _spellbook_identity(owner_id: str, transaction_name: str) -> DevopsIdentity:
    """Build and return a registered-shape spellbook identity for index transactions."""
    return DevopsIdentity(
        owner_kind="spellbook",
        owner_id=owner_id,
        aetheric_frame_name="frame-1",
        metadata={},
        available_transactions=(transaction_name,),
    )


def _leader_identity(transaction_name: str) -> DevopsIdentity:
    """Build a conduit identity supporting one cluster-leader transaction."""
    return DevopsIdentity(
        owner_kind="conduit",
        owner_id="conduit-1",
        aetheric_frame_name="frame-1",
        metadata={},
        available_transactions=(transaction_name,),
    )


class _RecordingGateOps:
    """
    Lineage-gate double recording drain/reopen calls for freeze coordination
    tests (unelect terminal drain + notch park-mode quiesce).

    Purpose:
        Capture the order and footprint of conduit-lineage drain/quiesce/reopen
        requests without standing up the real CreationGateController.
    """

    def __init__(self) -> None:
        """Start with empty drain, quiesce, and reopen logs."""
        self.closed: List[str] = []
        self.quiesced: List[str] = []
        self.enabled: List[str] = []

    def close_and_wait_conduit_lineage(self, root_id: str) -> None:
        """Record a terminal drain-to-zero request for one root lineage."""
        self.closed.append(root_id)

    def quiesce_conduit_lineage(self, root_id: str) -> None:
        """Record a park-mode freeze+drain request for one root lineage."""
        self.quiesced.append(root_id)

    def enable_conduit_lineage(self, root_id: str) -> None:
        """Record a reopen request for one root lineage."""
        self.enabled.append(root_id)


# ---------------------------------------------------------------------------
# NOTCH
# ---------------------------------------------------------------------------
def test_notch_seals_spellbook_conduit_and_binding_exclusive() -> None:
    """
    Purpose:
        Verify a notch seals the owning spellbook, its conduit, and the targeted
        binding key all EXCLUSIVE.
    Contract:
        - spellbook, conduit, and binding scopes carry EXCLUSIVE.
        - index_mode marks the notch shape.
    Returns:
        None.
    Raises:
        AssertionError: If the notch seal is not fully exclusive.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "notch")
    registry.register_identity(identity)

    plan = NotchTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "owner_conduit_id": "conduit-1",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    scope_claims = dict(plan["scope_claims"])
    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-A")
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims[binding_scope] == ClaimMode.EXCLUSIVE.value
    assert plan["metadata"]["index_mode"] == "notch"


def test_notch_binding_scope_tracks_the_targeted_lookup_key() -> None:
    """
    Purpose:
        Verify the sealed binding scope reflects the exact targeted lookup key.
    Contract:
        - A different binding key yields a different sealed binding scope.
    Returns:
        None.
    Raises:
        AssertionError: If the binding scope does not track the lookup key.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "notch")
    registry.register_identity(identity)

    plan = NotchTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "owner_conduit_id": "conduit-9",
            "binding_key": ("frame-1", "lookup-key-Z"),
        },
    )

    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-Z")
    assert binding_scope in dict(plan["scope_claims"])
    assert "scope:conduit:conduit-9" in plan["scope_keys"]


def test_notch_includes_spellbook_conduit_and_binding_in_scope_keys() -> None:
    """
    Purpose:
        Verify all three sealed surfaces appear in scope_keys (not only scope_claims).
    Contract:
        - spellbook, conduit, and binding scopes are present in scope_keys.
    Returns:
        None.
    Raises:
        AssertionError: If a sealed surface is missing from scope_keys.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "notch")
    registry.register_identity(identity)

    plan = NotchTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "owner_conduit_id": "conduit-1",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    scope_keys = set(plan["scope_keys"])
    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-A")
    assert "scope:spellbook:spellbook-1" in scope_keys
    assert "scope:conduit:conduit-1" in scope_keys
    assert binding_scope in scope_keys


def test_notch_plan_quiesce_footprint_matches_the_sealed_conduits() -> None:
    """
    Purpose:
        Verify the plan-derived runtime-freeze footprint is exactly the
        conduit set the notch seals EXCLUSIVE (gate freeze and embargo seal
        must never diverge).
    Contract:
        - normalized metadata carries quiesce_root_conduit_ids equal to the
          plan's conduit_ids (sorted, deduplicated).
    Returns:
        None.
    Raises:
        AssertionError: If the freeze footprint diverges from the seal.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "notch")
    registry.register_identity(identity)

    plan = NotchTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "owner_conduit_id": "conduit-1",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    assert plan["metadata"]["quiesce_root_conduit_ids"] == plan["conduit_ids"]
    assert "conduit-1" in plan["metadata"]["quiesce_root_conduit_ids"]


def test_notch_on_start_quiesces_every_planned_lineage_park_mode() -> None:
    """
    Purpose:
        Verify the notch freeze quiesces (park-mode, never terminal) every
        plan-derived lineage through the DevOps gate facade.
    Contract:
        - on_start calls quiesce_conduit_lineage once per planned root id.
        - The terminal drain verb is never used by the notch freeze.
    Returns:
        None.
    Raises:
        AssertionError: If the freeze footprint or verb is wrong.
    """
    _, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "notch")
    gate_ops = _RecordingGateOps()

    NotchTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "conduit_lineage_gate_ops": gate_ops,
            "quiesce_root_conduit_ids": ("conduit-1", "conduit-2"),
        },
    )

    assert gate_ops.quiesced == ["conduit-1", "conduit-2"]
    assert gate_ops.closed == []
    assert gate_ops.enabled == []


def test_notch_on_end_reopens_every_planned_lineage() -> None:
    """
    Purpose:
        Verify the notch reopen restores admission for every frozen lineage
        (fail-closed: dispatched by the mediator on every root end).
    Contract:
        - on_end calls enable_conduit_lineage once per planned root id.
    Returns:
        None.
    Raises:
        AssertionError: If any frozen lineage is not reopened.
    """
    _, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "notch")
    gate_ops = _RecordingGateOps()

    NotchTransactionStrategy.on_end(
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "conduit_lineage_gate_ops": gate_ops,
            "quiesce_root_conduit_ids": ("conduit-1", "conduit-2"),
        },
    )

    assert gate_ops.enabled == ["conduit-1", "conduit-2"]
    assert gate_ops.quiesced == []


def test_notch_freeze_is_a_noop_without_the_gate_facade() -> None:
    """
    Purpose:
        Verify envelope-only notch starts stay legal: no facade in metadata
        means neither freeze nor reopen fires (unelect precedent).
    Contract:
        - on_start and on_end tolerate absent conduit_lineage_gate_ops.
    Returns:
        None.
    Raises:
        AssertionError: If the freeze path raises without a facade.
    """
    _, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "notch")

    NotchTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata={"quiesce_root_conduit_ids": ("conduit-1",)},
    )
    NotchTransactionStrategy.on_end(
        devops_information_registry=registry,
        identity=identity,
        metadata={"quiesce_root_conduit_ids": ("conduit-1",)},
    )


def test_notch_freeze_and_reopen_footprints_are_symmetric() -> None:
    """
    Purpose:
        Verify the freeze and reopen walk the same root set in the same
        order, so no lineage is frozen without a matching reopen.
    Contract:
        - quiesced and enabled logs are identical for one metadata payload.
    Returns:
        None.
    Raises:
        AssertionError: If the footprints diverge.
    """
    _, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "notch")
    gate_ops = _RecordingGateOps()
    metadata = {
        "conduit_lineage_gate_ops": gate_ops,
        "quiesce_root_conduit_ids": ("conduit-3", "conduit-7", "conduit-9"),
    }

    NotchTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata=metadata,
    )
    NotchTransactionStrategy.on_end(
        devops_information_registry=registry,
        identity=identity,
        metadata=metadata,
    )

    assert gate_ops.quiesced == gate_ops.enabled


# ---------------------------------------------------------------------------
# ADD_TO_INDEX
# ---------------------------------------------------------------------------
def test_add_to_index_seals_both_sides_exclusive() -> None:
    """
    Purpose:
        Verify add-to-index seals BOTH source and target spellbooks/conduits plus
        the moved binding key, all EXCLUSIVE (a cross-spellbook ownership move).
    Contract:
        - Both spellbook scopes, both conduit scopes, and the binding scope are
          EXCLUSIVE.
        - index_mode marks the add_to_index shape.
    Returns:
        None.
    Raises:
        AssertionError: If either side is not sealed exclusively.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "add_to_index")
    registry.register_identity(identity)

    plan = AddToIndexTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "source_spellbook_id": "spellbook-1",
            "target_spellbook_id": "spellbook-2",
            "source_conduit_id": "conduit-1",
            "target_conduit_id": "conduit-2",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    scope_claims = dict(plan["scope_claims"])
    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-A")
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:spellbook:spellbook-2"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-2"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims[binding_scope] == ClaimMode.EXCLUSIVE.value
    assert plan["metadata"]["index_mode"] == "add_to_index"


def test_add_to_index_scope_keys_carry_both_sides_and_binding() -> None:
    """
    Purpose:
        Verify both participants and the binding appear in scope_keys.
    Contract:
        - source/target spellbook + conduit scopes and the binding scope are present.
    Returns:
        None.
    Raises:
        AssertionError: If a participant or the binding is missing from scope_keys.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "add_to_index")
    registry.register_identity(identity)

    plan = AddToIndexTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "source_spellbook_id": "spellbook-1",
            "target_spellbook_id": "spellbook-2",
            "source_conduit_id": "conduit-1",
            "target_conduit_id": "conduit-2",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    scope_keys = set(plan["scope_keys"])
    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-A")
    assert {
        "scope:spellbook:spellbook-1",
        "scope:spellbook:spellbook-2",
        "scope:conduit:conduit-1",
        "scope:conduit:conduit-2",
        binding_scope,
    } <= scope_keys


# ---------------------------------------------------------------------------
# REMOVE_FROM_INDEX
# ---------------------------------------------------------------------------
def test_remove_from_index_seals_spellbook_conduit_and_binding_exclusive() -> None:
    """
    Purpose:
        Verify remove-from-index seals the owning spellbook, conduit, and the moved
        binding key all EXCLUSIVE.
    Contract:
        - spellbook, conduit, and binding scopes carry EXCLUSIVE.
        - index_mode marks the remove_from_index shape.
    Returns:
        None.
    Raises:
        AssertionError: If the remove seal is not fully exclusive.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "remove_from_index")
    registry.register_identity(identity)

    plan = RemoveFromIndexTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "spellbook_id": "spellbook-1",
            "owner_conduit_id": "conduit-1",
            "binding_key": ("frame-1", "lookup-key-A"),
        },
    )

    scope_claims = dict(plan["scope_claims"])
    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-A")
    assert scope_claims["scope:spellbook:spellbook-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims[binding_scope] == ClaimMode.EXCLUSIVE.value
    assert plan["metadata"]["index_mode"] == "remove_from_index"


def test_remove_from_index_binding_scope_tracks_the_lookup_key() -> None:
    """
    Purpose:
        Verify the sealed binding scope reflects the exact targeted lookup key.
    Contract:
        - A different binding key yields a different sealed binding scope.
    Returns:
        None.
    Raises:
        AssertionError: If the binding scope does not track the lookup key.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _spellbook_identity("spellbook-1", "remove_from_index")
    registry.register_identity(identity)

    plan = RemoveFromIndexTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "spellbook_id": "spellbook-1",
            "owner_conduit_id": "conduit-1",
            "binding_key": ("frame-1", "lookup-key-Q"),
        },
    )

    binding_scope = transaction_manager.make_scope_key_binding("frame-1", "lookup-key-Q")
    assert binding_scope in dict(plan["scope_claims"])


# ---------------------------------------------------------------------------
# ELECT_CONDUIT_CLUSTER_LEADER
# ---------------------------------------------------------------------------
def test_elect_seals_member_conduits_exclusive_and_marks_mode() -> None:
    """
    Purpose:
        Verify electing a leader seals every member conduit EXCLUSIVE and marks the mode.
    Contract:
        - Each member conduit scope is EXCLUSIVE.
        - conduit_ids carries the sorted footprint; cluster_leader_mode is elect.
    Returns:
        None.
    Raises:
        AssertionError: If elect does not seal the members exclusively.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _leader_identity("elect_conduit_cluster_leader")
    registry.register_identity(identity)

    plan = ElectConduitClusterLeaderTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"member_conduit_ids": ("conduit-2", "conduit-1")},
    )

    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-2"] == ClaimMode.EXCLUSIVE.value
    assert plan["conduit_ids"] == ("conduit-1", "conduit-2")
    assert plan["metadata"]["cluster_leader_mode"] == "elect"


def test_elect_isolates_to_conduits_only_no_spellbook_claim() -> None:
    """
    Purpose:
        Verify elect seals only member conduits (no spellbook/binding claim), since
        the bind is a domain effect run in-window, not part of the seal.
    Contract:
        - No spellbook-scope claim appears in elect's scope_claims.
    Returns:
        None.
    Raises:
        AssertionError: If elect widens beyond the member conduits.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _leader_identity("elect_conduit_cluster_leader")
    registry.register_identity(identity)

    plan = ElectConduitClusterLeaderTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"member_conduit_ids": ("conduit-1",)},
    )

    scope_claims = dict(plan["scope_claims"])
    assert not any(key.startswith("scope:spellbook:") for key in scope_claims)


def test_elect_on_start_does_not_drain_any_lineage() -> None:
    """
    Purpose:
        Verify elect performs NO lineage drain (inert->active needs no quiesce).
    Contract:
        - on_start leaves the gate-ops drain log empty even when one is supplied.
    Returns:
        None.
    Raises:
        AssertionError: If elect drains a lineage.
    """
    registry = DevopsInformationRegistry("frame-1")
    identity = _leader_identity("elect_conduit_cluster_leader")
    registry.register_identity(identity)
    gate_ops = _RecordingGateOps()

    ElectConduitClusterLeaderTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "member_root_conduit_ids": ("root-1", "root-2"),
            "conduit_lineage_gate_ops": gate_ops,
        },
    )

    assert gate_ops.closed == []


# ---------------------------------------------------------------------------
# UNELECT_CONDUIT_CLUSTER_LEADER
# ---------------------------------------------------------------------------
def test_unelect_seals_member_conduits_exclusive_and_marks_mode() -> None:
    """
    Purpose:
        Verify unelecting a leader seals every member conduit EXCLUSIVE and marks the mode.
    Contract:
        - Each member conduit scope is EXCLUSIVE; cluster_leader_mode is unelect.
    Returns:
        None.
    Raises:
        AssertionError: If unelect does not seal the members exclusively.
    """
    transaction_manager, registry = _manager_and_registry()
    identity = _leader_identity("unelect_conduit_cluster_leader")
    registry.register_identity(identity)

    plan = UnelectConduitClusterLeaderTransactionStrategy.build_start_plan(
        transaction_manager=transaction_manager,
        devops_information_registry=registry,
        identity=identity,
        metadata={"member_conduit_ids": ("conduit-1", "conduit-2")},
    )

    scope_claims = dict(plan["scope_claims"])
    assert scope_claims["scope:conduit:conduit-1"] == ClaimMode.EXCLUSIVE.value
    assert scope_claims["scope:conduit:conduit-2"] == ClaimMode.EXCLUSIVE.value
    assert plan["metadata"]["cluster_leader_mode"] == "unelect"


def test_unelect_on_start_quiesces_every_member_root_lineage() -> None:
    """
    Purpose:
        Verify unelect quiesces every member root lineage on_start (the
        use-after-dispose guard: no meld may be mid-create against a store
        about to be unbound) in PARK mode, so concurrent melds wait instead
        of erroring and the gates stay reopenable.
    Contract:
        - on_start quiesces each supplied member root exactly once.
        - The terminal drain verb is never used (the pre-patch defect).
    Returns:
        None.
    Raises:
        AssertionError: If the freeze footprint or verb does not match.
    """
    registry = DevopsInformationRegistry("frame-1")
    identity = _leader_identity("unelect_conduit_cluster_leader")
    registry.register_identity(identity)
    gate_ops = _RecordingGateOps()

    UnelectConduitClusterLeaderTransactionStrategy.on_start(
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "member_root_conduit_ids": ("root-1", "root-2"),
            "conduit_lineage_gate_ops": gate_ops,
        },
    )

    assert sorted(gate_ops.quiesced) == ["root-1", "root-2"]
    assert gate_ops.closed == []
    assert gate_ops.enabled == []


def test_unelect_on_end_reopens_every_member_root_lineage() -> None:
    """
    Purpose:
        Verify unelect reopens every member root lineage on_end (fail-closed: gates
        must reopen on every exit path so a failed unelect never leaves them gated).
    Contract:
        - on_end reopens each supplied member root exactly once.
    Returns:
        None.
    Raises:
        AssertionError: If the reopen footprint does not match the member roots.
    """
    registry = DevopsInformationRegistry("frame-1")
    identity = _leader_identity("unelect_conduit_cluster_leader")
    registry.register_identity(identity)
    gate_ops = _RecordingGateOps()

    UnelectConduitClusterLeaderTransactionStrategy.on_end(
        devops_information_registry=registry,
        identity=identity,
        metadata={
            "member_root_conduit_ids": ("root-1", "root-2"),
            "conduit_lineage_gate_ops": gate_ops,
        },
    )

    assert sorted(gate_ops.enabled) == ["root-1", "root-2"]


def test_unelect_quiesce_then_reopen_cover_the_same_root_set() -> None:
    """
    Purpose:
        Verify the quiesce (on_start) and reopen (on_end) footprints are the
        same root set, so every gate frozen is later reopened.
    Contract:
        - The set of quiesced roots equals the set of reopened roots.
    Returns:
        None.
    Raises:
        AssertionError: If freeze and reopen footprints diverge.
    """
    registry = DevopsInformationRegistry("frame-1")
    identity = _leader_identity("unelect_conduit_cluster_leader")
    registry.register_identity(identity)
    gate_ops = _RecordingGateOps()
    metadata = {
        "member_root_conduit_ids": ("root-1", "root-2", "root-3"),
        "conduit_lineage_gate_ops": gate_ops,
    }

    UnelectConduitClusterLeaderTransactionStrategy.on_start(
        devops_information_registry=registry, identity=identity, metadata=metadata,
    )
    UnelectConduitClusterLeaderTransactionStrategy.on_end(
        devops_information_registry=registry, identity=identity, metadata=metadata,
    )

    assert set(gate_ops.quiesced) == set(gate_ops.enabled)
    assert set(gate_ops.quiesced) == {"root-1", "root-2", "root-3"}
