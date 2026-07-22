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


class ElectConduitClusterLeaderTransactionStrategy(TransactionStrategy):
    """
    Elect-cluster-leader transaction resolver (concurrency envelope only).

    Purpose:
        Mediate one `ELECT_CONDUIT_CLUSTER_LEADER` request. Election is an
        inert -> active transition; while inert the cluster door hard-errors, so
        no meld is mid-create against the team-store and a light/atomic envelope
        is sufficient (no lineage drain). The actual leadership effect (binding
        the cluster team-store to the elected leader's `Creations`) is run by the
        domain call site (ConduitCluster) inside the held transaction window --
        exactly as Spellbook runs `_apply_notch` between start and end. This
        strategy does NOT touch creations; its only job is to seal the footprint.

    Call-site metadata contract:
        - "member_conduit_ids": tuple[str] -- cluster member conduit ids (seal footprint).

    Contract:
        - Seals the cluster member conduits EXCLUSIVE for the duration, isolated
          to them; no drain (inert invariant).
        - Commit runs only the base fact-baseline stamp (no domain effect here).

    Threading:
        Stateless class-level strategy. Notably it needs NO lineage drain -
        see System Context for why the light envelope is sufficient here.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the transaction
        family; never instantiated and never bindable.

    Subsystem Context:
        The activation half of the cluster's OPTIONAL second layer, paired with
        `UnelectConduitClusterLeaderTransactionStrategy`. Membership and
        sharing - the always-on first layer - are handled separately by
        cluster join and leave.

    System Context:
        The asymmetry between elect and unelect is the instructive part, and it
        turns on one fact: WHICH DIRECTION THE TRANSITION RUNS.
        Election goes inert -> active. While inert the cluster door
        hard-errors, so no meld can be mid-create against the team store, and
        an atomic envelope with no lineage drain is provably sufficient.
        Unelection goes active -> inert, where a meld may be holding its gate
        ticket across an executor right now - so that direction requires the
        full freeze.
        The domain effect is deliberately NOT performed here. This strategy
        seals the footprint and `ConduitCluster` binds the team store inside
        the held window, exactly as Spellbook runs `_apply_notch` between start
        and end. Strategies own isolation; call sites own effect.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Elect-cluster-leader transaction resolver (concurrency envelope only). "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

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
        Build the change-control request inputs for one leader-elect transaction.

        Contract:
            Concurrency envelope only (the registry argument is unused): collects
            the cluster member conduit ids and claims each one EXCLUSIVE, so no
            concurrent transaction touches a member while the leader is chosen.
            The election EFFECT runs at the call site; this plan owns isolation
            only. Sets `cluster_leader_mode="elect"` and the transaction
            identity. Pure planning - no runtime object is mutated here.

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
    def on_start(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """
        Elect needs no start-side coordination (inert -> active).

        Returns:
            None.
        """
        return None

    @staticmethod
    def on_end(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """
        Elect needs no end-side coordination.

        Returns:
            None.
        """
        return None
