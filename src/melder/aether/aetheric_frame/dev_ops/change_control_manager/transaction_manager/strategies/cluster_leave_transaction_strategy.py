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


class ClusterLeaveTransactionStrategy(TransactionStrategy):
    """
    Cluster-leave transaction resolver (DevOps scope isolation only).

    Purpose:
        Resolve one `CLUSTER_LEAVE` request into the change-control scope plan that
        isolates a conduit's EXIT from a cluster. Leaving tears down spell-share
        contracts between the departing conduit and every remaining member, so the
        entire exit is treated as one link over EVERY involved conduit: this
        transaction seals them all for the duration, and the membership + unshare
        work runs as the in-window effect. The cluster owns the effect; this
        strategy owns only the isolation (it never reaches into the runtime).

    Runtime shape (the seal footprint):
        - Every involved conduit -- the leaving conduit plus every remaining member
          it shared with -- supplied by the cluster call site as
          `metadata["conduit_ids"]`.
        - Each involved conduit implies its conduit scope, its ward, and its
          owning spellbook (when resolvable from the DevOps registry).

    Contract:
        - The cluster call site supplies the involved conduit ids through
          metadata; this strategy owns only scope planning, with no live-object
          reach.
        - Claim modes mirror the link pattern: participant conduits and wards are
          EXCLUSIVE (frozen from other structural work while the leave is held),
          owning spellbooks are INTENT (block a whole-spellbook claim, such as a
          transfer's EXCLUSIVE spellbook claim, without serializing unrelated
          piece-work on those spellbooks).
        - Because the leave SUBSUMES the per-pair `cluster_link` unshare contracts,
          the in-window unshare effect must NOT open its own `cluster_link`
          transactions -- they would self-conflict on the scopes this seal holds
          (a `cluster_link` runs on a conduit identity, a different owner than
          this cluster identity, so the embargo would block and time out).
        - This transaction concerns membership and sharing only; the elected-leader
          team store (if any) is the separate elect/unelect concern.

    Threading:
        Stateless class-level strategy; concurrency is owned by the mediator
        and the scope claims this plan requests.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the transaction
        family; never instantiated and never bindable.

    Subsystem Context:
        The `cluster_leave` member of the transaction family and the exact
        inverse of `ClusterJoinTransactionStrategy`, with matching claim modes
        because an exit mutates the same surfaces an entry does.

    System Context:
        The final contract line draws the boundary that keeps this strategy
        tractable: leave handles MEMBERSHIP AND SHARING ONLY, while the elected
        leader is the separate elect/unelect concern. That separation reflects
        the cluster's own two-layer design - spell sharing is the always-on core
        that needs no leader, and the team store exists solely for
        `unique_per_conduit_cluster` spells. Folding leadership into leave would
        couple the common path to a mechanism most clusters never use.
        The same self-conflict rule as join applies in reverse: the in-window
        unshare must NOT open its own `cluster_link` transactions, because they
        would contend with the scopes this seal holds under a different owner
        identity and time out rather than fail loudly.
        Sealing every remaining member - not just the departing conduit - is
        what makes exit safe. The departing member's shares are torn down in
        both directions across the whole membership, so a narrower seal would
        let a peer observe a half-removed member.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Cluster-leave transaction resolver (DevOps scope isolation only). "
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
        Build the change-control scope plan for one cluster-leave transaction.

        Contract:
            DevOps scope-isolation envelope (the move-out counterpart to
            cluster-join): resolves the involved conduit ids and, for each,
            seals the conduit + its `conduit_ward` + owning spellbook + every
            resolved identity's transaction-owner scopes (the link footprint).
            The actual membership change runs at the call site; this plan only
            isolates the affected scopes. Stamps normalized metadata with the
            transaction identity and the affected id sets. Pure planning - no
            runtime object is mutated here.

        Args:
            transaction_manager:
                Frame-local scope-key/request helper surface.
            devops_information_registry:
                Topology registry used to resolve each conduit's identity and
                owning spellbook.
            identity:
                Submitter identity (initiator + spellbook hint).
            metadata:
                Caller metadata carrying the involved conduit ids and explicit
                scope keys/hashes/binding/contract keys.

        Returns:
            Dict[str, object]:
                Normalized request inputs (sealed conduit/ward/spellbook scopes,
                capabilities, normalized metadata) for mediator admission.
        """
        conduit_ids = cls._involved_conduit_ids(metadata)
        explicit_scope_keys = tuple(metadata.get("scope_keys", ()))
        explicit_scope_hashes = tuple(metadata.get("scope_hashes", ()))
        explicit_binding_keys = tuple(metadata.get("binding_keys", ()))
        explicit_contract_keys = tuple(metadata.get("contract_keys", ()))

        scope_keys: Set[str] = set(explicit_scope_keys)
        affected_identity_keys: Set[Tuple[str, str]] = set()
        affected_spellbook_ids: Set[str] = set()

        for conduit_id in conduit_ids:
            scope_keys.add(transaction_manager.make_scope_key_conduit(conduit_id))
            scope_keys.add(
                transaction_manager.make_scope_key_identity(
                    owner_kind="conduit_ward",
                    owner_id=conduit_id,
                )
            )
            affected_identity_keys.add(("conduit_ward", conduit_id))
            conduit_identity = devops_information_registry.get_identity(
                owner_kind="conduit",
                owner_id=conduit_id,
            )
            if conduit_identity is not None:
                affected_identity_keys.add(
                    (conduit_identity.owner_kind, conduit_identity.owner_id)
                )
                cls._add_transaction_owner_scopes(
                    scope_keys=scope_keys,
                    transaction_manager=transaction_manager,
                    identity=conduit_identity,
                )

            spellbook_id = devops_information_registry.get_spellbook_for_conduit(
                conduit_id
            )
            if spellbook_id is None:
                continue
            affected_spellbook_ids.add(spellbook_id)
            scope_keys.add(transaction_manager.make_scope_key_spellbook(spellbook_id))
            spellbook_identity = devops_information_registry.get_identity(
                owner_kind="spellbook",
                owner_id=spellbook_id,
            )
            if spellbook_identity is None:
                continue
            affected_identity_keys.add(
                (spellbook_identity.owner_kind, spellbook_identity.owner_id)
            )
            cls._add_transaction_owner_scopes(
                scope_keys=scope_keys,
                transaction_manager=transaction_manager,
                identity=spellbook_identity,
            )

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["cluster_membership_mode"] = "cluster_leave"
        normalized_metadata["participant_conduit_ids"] = tuple(sorted(conduit_ids))
        normalized_metadata["affected_spellbook_ids"] = tuple(
            sorted(affected_spellbook_ids)
        )
        normalized_metadata["affected_identity_keys"] = tuple(
            sorted(affected_identity_keys)
        )

        # Owning spellbooks claimed INTENT (a membership change only adds/removes
        # contract buckets), conduits and wards default to EXCLUSIVE.
        spellbook_scope_claims: Tuple[Tuple[str, str], ...] = tuple(
            (
                transaction_manager.make_scope_key_spellbook(affected_spellbook_id),
                ClaimMode.INTENT.value,
            )
            for affected_spellbook_id in sorted(affected_spellbook_ids)
        )

        return {
            "initiator_conduit_id": next(iter(sorted(conduit_ids)), identity.owner_id),
            "spellbook_id": None,
            "conduit_ids": tuple(sorted(conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_claims": spellbook_scope_claims,
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": explicit_binding_keys,
            "contract_keys": explicit_contract_keys,
            "granted_capabilities": ("cluster_leave", "cluster_link", "contract_mutation"),
            "required_capabilities": ("cluster_leave", "cluster_link", "contract_mutation"),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def _involved_conduit_ids(metadata: Dict[str, object]) -> Set[str]:
        """
        Collect the involved conduit ids (the seal footprint) from metadata.
        """
        out: Set[str] = set()
        for conduit_id in metadata.get("conduit_ids", ()):
            if isinstance(conduit_id, str) and conduit_id.strip():
                out.add(conduit_id.strip())
        if not out:
            raise RuntimeError(
                "Cluster-leave transaction requires at least one conduit id in metadata."
            )
        return out

    @staticmethod
    def _add_transaction_owner_scopes(
            *,
            scope_keys: Set[str],
            transaction_manager: "ChangeControlTransactionManager",
            identity: DevopsIdentity,
    ) -> None:
        """
        Add transaction-owner scopes for every declared transaction on one identity.
        """
        for transaction_name in identity.available_transactions:
            scope_keys.add(
                transaction_manager.make_scope_key_transaction_owner(
                    owner_kind=identity.owner_kind,
                    owner_id=identity.owner_id,
                    transaction_name=transaction_name,
                )
            )

    @staticmethod
    def on_start(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Cluster-leave needs no DevOps start-side coordination.

        Returns:
            None.
        """
        return None

    @staticmethod
    def on_end(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Cluster-leave needs no DevOps end-side coordination.

        Returns:
            None.
        """
        return None
