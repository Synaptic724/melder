from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

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
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.orchestrator.staged_mutation import (
        ChangeControlStagedMutation,
    )


class UnelectConduitClusterLeaderTransactionStrategy(TransactionStrategy):
    """
    Unelect-cluster-leader transaction resolver (unbind the team-store facade safely).

    Purpose:
        Resolve one `UNELECT_CONDUIT_CLUSTER_LEADER` request: unbind the cluster's
        `cluster_creations` facade (cluster goes inert). This REQUIRES coordination
        -- every member root lineage must be drained so no meld is mid-create
        against the leader store when the facade unbinds (a meld holds its gate
        ticket across the whole executor).

    Call-site metadata contract:
        - "member_conduit_ids": tuple[str] -- member conduit ids (seal footprint).
        - "member_root_conduit_ids": tuple[str] -- member root ids (drain footprint).
        - "conduit_lineage_gate_ops": ConduitLineageGateOps (drain/reopen facade).
        - "cluster_creations": the ClusterCreations facade (unbind target).

    Lifecycle (the coordination):
        - build_start_plan: seal the member conduits EXCLUSIVE.
        - on_start (scopes held): drain every member root lineage via the gate
          facade. A drain timeout raises here -> the transaction aborts.
        - apply_commit_delta (commit only): cluster_creations.unbind().
        - on_end (every exit path -- commit, abort, or error): reopen every member
          root lineage. So a failed drain leaves the leader still bound and the
          lineages reopened (fail-closed), never permanently gated.
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
        Build the change-control request inputs for one unelect transaction.
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
        Drain every member root lineage (scopes held) so no meld is mid-create.
        """
        del devops_information_registry, identity
        gate_ops = metadata.get("conduit_lineage_gate_ops")
        if gate_ops is None:
            return
        for root_id in metadata.get("member_root_conduit_ids", ()):
            if isinstance(root_id, str) and root_id:
                gate_ops.close_and_wait_conduit_lineage(root_id)

    @classmethod
    def apply_commit_delta(
            cls,
            *,
            devops_information_registry: Optional[DevopsInformationRegistry],
            identity: DevopsIdentity,
            staged: "ChangeControlStagedMutation",
    ) -> None:
        """
        Committed effect (drain already done): unbind the cluster facade.
        """
        staged_metadata = getattr(staged, "metadata", None) or {}
        cluster_creations = staged_metadata.get("cluster_creations")
        if cluster_creations is not None:
            cluster_creations.unbind()
        super().apply_commit_delta(
            devops_information_registry=devops_information_registry,
            identity=identity,
            staged=staged,
        )

    @staticmethod
    def on_end(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Reopen every member root lineage on every exit path (fail-closed).
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

    @staticmethod
    def _member_root_ids(metadata: Dict[str, object]) -> List[str]:
        """
        Collect the cluster member root-conduit ids (lineage drain footprint).
        """
        out: List[str] = []
        for root_id in metadata.get("member_root_conduit_ids", ()):
            if isinstance(root_id, str) and root_id:
                out.append(root_id)
        return out
