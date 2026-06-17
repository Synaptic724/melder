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


class ElectConduitClusterLeaderTransactionStrategy(TransactionStrategy):
    """
    Elect-cluster-leader transaction resolver (bind the cluster team-store facade).

    Purpose:
        Resolve one `ELECT_CONDUIT_CLUSTER_LEADER` request: bind the cluster's
        `cluster_creations` facade to the elected leader conduit's `Creations`.
        Election is an inert -> active transition; while inert the cluster door
        hard-errors, so no in-flight cluster create exists against a store and a
        light/atomic transaction is sufficient (no lineage drain).

    Call-site metadata contract (the cluster call site supplies these when it
    opens the transaction):
        - "member_conduit_ids": tuple[str] -- cluster member conduit ids (seal footprint).
        - "cluster_creations": the ClusterCreations facade (committed-effect target).
        - "leader_creations": the elected leader's Creations (bind target).

    Contract:
        - Seals the cluster member conduits EXCLUSIVE for the bind, isolated to
          them; no drain (inert invariant).
        - Committed effect (apply_commit_delta, scopes held): cluster_creations
          .bind(leader_creations); then the base fact-baseline stamp runs.
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
        Build the change-control request inputs for one elect transaction.
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
        normalized_metadata["cluster_leader_mode"] = "elect"

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
            "granted_capabilities": ("elect_conduit_cluster_leader", "cluster_leader_election"),
            "required_capabilities": ("elect_conduit_cluster_leader", "cluster_leader_election"),
            "metadata": normalized_metadata,
        }

    @classmethod
    def apply_commit_delta(
            cls,
            *,
            devops_information_registry: Optional[DevopsInformationRegistry],
            identity: DevopsIdentity,
            staged: "ChangeControlStagedMutation",
    ) -> None:
        """
        Committed effect: bind the cluster facade to the leader's Creations.
        """
        staged_metadata = getattr(staged, "metadata", None) or {}
        cluster_creations = staged_metadata.get("cluster_creations")
        leader_creations = staged_metadata.get("leader_creations")
        if cluster_creations is not None and leader_creations is not None:
            cluster_creations.bind(leader_creations)
        super().apply_commit_delta(
            devops_information_registry=devops_information_registry,
            identity=identity,
            staged=staged,
        )

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

    @staticmethod
    def on_start(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """Elect needs no start-side coordination (inert -> active)."""
        return None

    @staticmethod
    def on_end(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """Elect needs no end-side coordination."""
        return None
