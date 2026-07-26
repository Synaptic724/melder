from typing import TYPE_CHECKING, Dict, List, Set, Tuple

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy import (
    TransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.embargo_manager.embargo_manager import (
    ClaimMode,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )


class UnelectConduitClusterLeaderTransactionStrategy(TransactionStrategy):
    """
    Unelect-cluster-leader transaction resolver (freeze envelope; no domain effect).

    Purpose:
        Mediate one `UNELECT_CONDUIT_CLUSTER_LEADER` request. Unelection takes the
        active cluster back to inert. Because the cluster is active, a meld may be
        mid-create against the leader store right now (a meld holds its gate ticket
        across the whole executor), so the team-store must NOT be re-targeted while
        a reader is in flight. This strategy provides the freeze: it drains every
        member root lineage to zero before the domain effect runs and reopens them
        after. The actual unbind of the team-store is run by the domain call site
        (ConduitCluster) inside the held window, between start and end -- exactly as
        Spellbook runs `_apply_notch`. This strategy does NOT touch creations.

    Call-site metadata contract:
        - "member_conduit_ids": tuple[str] -- member conduit ids (seal footprint).
        - "member_root_conduit_ids": tuple[str] -- member root ids (drain footprint).
        - "conduit_lineage_gate_ops": ConduitLineageGateOps (drain/reopen facade).

    Lifecycle (the freeze):
        - build_start_plan: seal the member conduits EXCLUSIVE.
        - on_start (scopes held, before the domain unbind): QUIESCE every member
          root lineage via the gate facade - PARK mode (patch
          notch_conduit_gate_freeze_2026_07_12): concurrent melds park at their
          gate and resume on reopen. The original terminal drain verb made
          in-window melds RAISE and left gates unresurrectable (open() never
          clears the terminal flag) - the same freeze-verb defect the notch
          lane fixed. A drain timeout raises here -> abort.
        - commit: base fact-baseline stamp only (no domain effect here).
        - on_end (every exit path -- commit, abort, or error; dispatched by the
          mediator from root finalize since the same patch, which is what makes
          the reopen actually fire on plain end_transaction callers): reopen
          every member root lineage. A failed drain leaves the leader still
          bound and the lineages reopened (fail-closed), never permanently
          gated.

    Threading:
        Stateless class-level strategy, but it owns a real runtime freeze: it
        drains every member root lineage to zero before the domain effect and
        reopens them afterwards.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the transaction
        family; never instantiated and never bindable.

    Subsystem Context:
        The deactivation half of the cluster's optional leader layer, and the
        heavier twin of `ElectConduitClusterLeaderTransactionStrategy`.

    System Context:
        This strategy needs the freeze for precisely the reason notch does, and
        the two are worth reading together: SCOPE CLAIMS EXCLUDE OTHER
        TRANSACTIONS ONLY. A meld holds no claim, yet it holds its gate ticket
        across the entire executor - so a reader can be mid-create against the
        leader store while every transactional surface is properly sealed.
        Re-targeting the team store underneath that reader would hand it a
        store that no longer belongs to the cluster it resolved against.
        Draining every member root lineage to zero before the unbind is the
        only mechanism that reaches a non-transactional reader, and reopening
        afterwards on every exit path is mandatory - a gate left closed wedges
        the conduit permanently.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Unelect-cluster-leader transaction resolver (freeze envelope; no
        domain effect). Melder kernel machinery: read it to understand the runtime, do not drive
        it directly.
    """

    @classmethod
    def build_start_plan(
            cls,
            *,
            transaction_manager: "ChangeControlTransactionManager",
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build the change-control request inputs for one leader-unelect transaction.

        Contract:
            Freeze envelope with no domain effect (the registry argument is
            unused): collects the cluster member conduit ids and claims each one
            EXCLUSIVE, so no concurrent transaction touches a member while the
            leader is stepped down. The unelect EFFECT runs at the call site;
            this plan owns isolation only. Sets `cluster_leader_mode="unelect"`
            and the transaction identity. Pure planning - no runtime object is
            mutated here.

        Args:
            transaction_manager:
                Frame-local scope-key/request helper surface.
            devops_information_registry:
                Unused by this envelope strategy (accepted for contract parity).
            identity:
                Submitter identity (owner-id fallback for the initiator).
            metadata:
                Caller metadata carrying the member conduit ids and options.

        Returns:
            Dict[str, object]:
                Normalized request inputs (initiator, member conduit set,
                EXCLUSIVE scope claims, capabilities, normalized metadata) for
                mediator admission.
        """
        del devops_information_registry
        member_conduit_ids = cls._member_conduit_ids(metadata)
        scope_keys: Set[str] = set(metadata.get("scope_keys", ()))
        scope_claims: List[Tuple[str, str]] = []
        for conduit_id in sorted(member_conduit_ids):
            scope = transaction_manager.make_scope_key_conduit(conduit_id)
            scope_keys.add(scope)
            scope_claims.append((scope, ClaimMode.EXCLUSIVE.value))

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["cluster_leader_mode"] = "unelect"

        initiator = metadata.get("initiator_conduit_id")
        if not isinstance(initiator, str) or not initiator:
            initiator = next(iter(sorted(member_conduit_ids)), identity.owner_id)

        return {
            "initiator_conduit_id": initiator,
            "spellbook_id": metadata.get("spellbook_id"),
            "conduit_ids": tuple(sorted(member_conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_claims": tuple(scope_claims),
            "scope_hashes": tuple(metadata.get("scope_hashes", ())),
            "binding_keys": tuple(metadata.get("binding_keys", ())),
            "contract_keys": tuple(metadata.get("contract_keys", ())),
            "granted_capabilities": ("unelect_conduit_cluster_leader", "cluster_leader_election"),
            "required_capabilities": ("unelect_conduit_cluster_leader", "cluster_leader_election"),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def on_start(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Quiesce every member root lineage (scopes held) so no meld is
        mid-create when the domain call site unbinds the team-store.

        Contract:
            - PARK mode (`quiesce_conduit_lineage`): concurrent melds wait at
              their gate and resume when `on_end` reopens - they are never
              turned into errors and the gates are never terminally closed.

        Returns:
            None.
        """
        del devops_information_registry, identity
        gate_ops = metadata.get("conduit_lineage_gate_ops")
        if gate_ops is None:
            return
        for root_id in metadata.get("member_root_conduit_ids", ()):
            if isinstance(root_id, str) and root_id:
                gate_ops.quiesce_conduit_lineage(root_id)

    @staticmethod
    def on_end(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Reopen every member root lineage on every exit path (fail-closed).

        Returns:
            None.
        """
        del devops_information_registry, identity
        gate_ops = metadata.get("conduit_lineage_gate_ops")
        if gate_ops is None:
            return
        for root_id in metadata.get("member_root_conduit_ids", ()):
            if isinstance(root_id, str) and root_id:
                gate_ops.enable_conduit_lineage(root_id)

    @staticmethod
    def _member_conduit_ids(metadata: Dict[str, object]) -> Set[str]:
        """
        Collect the cluster member conduit ids (the seal footprint) from metadata.
        """
        out: Set[str] = set()
        for conduit_id in metadata.get("member_conduit_ids", ()):
            if isinstance(conduit_id, str) and conduit_id:
                out.add(conduit_id)
        return out
