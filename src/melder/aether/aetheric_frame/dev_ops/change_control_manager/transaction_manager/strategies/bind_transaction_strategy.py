from typing import TYPE_CHECKING, Dict, Set, Tuple

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


class BindTransactionStrategy(TransactionStrategy):
    """
    Bind-family transaction resolver.

    Purpose:
        Resolve one bind or scan request into the minimal change-control plan
        that reflects the real runtime topology instead of a generic topology
        expansion model.

    Runtime shape:
        - Pre-conjure:
          - the Spellbook alone is affected
        - Post-conjure:
          - the Spellbook
          - the paired root Conduit
          - the paired ConduitWard
          - any ConduitCluster memberships of that root conduit

    Contract:
        - Uses sets for scope and identity accumulation, then normalizes once
          at the return boundary.
        - Never treats bind as a multi-conduit Spellbook fanout operation.
        - Uses the submitter identity's available transactions for Spellbook
          transaction-owner lock scopes.
        - Uses the paired conduit identity's available transactions for
          conduit-side lock scopes when conjured.
        - Uses cluster identities, when present, for cluster-side
          transaction-owner lock scopes.
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
        Build the change-control request inputs for one bind-family transaction.

        Args:
            transaction_manager:
                Scope-key helper owner used to normalize the bind request.
            devops_information_registry:
                Frame-local topology registry used to resolve the paired root
                conduit and any cluster memberships.
            identity:
                Spellbook identity originating the bind-family request.
            metadata:
                Caller-supplied bind-family metadata.

        Returns:
            Dict[str, object]:
                Normalized request inputs for mediator admission.
        """
        explicit_scope_keys = tuple(metadata.get("scope_keys", ()))
        explicit_scope_hashes = tuple(metadata.get("scope_hashes", ()))
        explicit_binding_keys = tuple(metadata.get("binding_keys", ()))
        identity_metadata = identity.metadata
        conjured = bool(identity_metadata.get("conjured"))
        if conjured:
            return cls._build_post_conjure_start_plan(
                transaction_manager=transaction_manager,
                devops_information_registry=devops_information_registry,
                identity=identity,
                metadata=metadata,
                explicit_scope_keys=explicit_scope_keys,
                explicit_scope_hashes=explicit_scope_hashes,
                explicit_binding_keys=explicit_binding_keys,
            )
        return cls._build_pre_conjure_start_plan(
            transaction_manager=transaction_manager,
            identity=identity,
            metadata=metadata,
            explicit_scope_keys=explicit_scope_keys,
            explicit_scope_hashes=explicit_scope_hashes,
            explicit_binding_keys=explicit_binding_keys,
        )

    @classmethod
    def _build_pre_conjure_start_plan(
            cls,
            *,
            transaction_manager: "ChangeControlTransactionManager",
            identity: DevopsIdentity,
            metadata: Dict[str, object],
            explicit_scope_keys: Tuple[str, ...],
            explicit_scope_hashes: Tuple[str, ...],
            explicit_binding_keys: Tuple[Tuple[str, str], ...],
    ) -> Dict[str, object]:
        """
        Build the bind-family request plan for a pre-conjure Spellbook.

        Contract:
            - Only spellbook scopes are claimed.
            - No conduit, ward, or cluster scopes are added.
            - The initiator id is the spellbook pseudo-owner id because no
              root conduit exists yet.
        """
        scope_keys: Set[str] = {
            transaction_manager.make_scope_key_spellbook(identity.owner_id),
        }
        cls._add_transaction_owner_scopes(
            scope_keys=scope_keys,
            transaction_manager=transaction_manager,
            identity=identity,
        )
        affected_identity_keys = {
            (identity.owner_kind, identity.owner_id),
        }
        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["spellbook_id"] = identity.owner_id
        normalized_metadata["bind_mode"] = "pre_conjure"
        normalized_metadata["affected_identity_keys"] = tuple(
            sorted(affected_identity_keys)
        )
        return {
            "initiator_conduit_id": f"spellbook:{identity.owner_id}",
            "spellbook_id": identity.owner_id,
            "conduit_ids": tuple(),
            "scope_keys": tuple(sorted(scope_keys.union(explicit_scope_keys))),
            "scope_claims": (
                (
                    transaction_manager.make_scope_key_spellbook(identity.owner_id),
                    ClaimMode.INTENT.value,
                ),
            ),
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": explicit_binding_keys,
            "contract_keys": tuple(),
            "granted_capabilities": ("bind",),
            "required_capabilities": ("bind",),
            "metadata": normalized_metadata,
        }

    @classmethod
    def _build_post_conjure_start_plan(
            cls,
            *,
            transaction_manager: "ChangeControlTransactionManager",
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
            explicit_scope_keys: Tuple[str, ...],
            explicit_scope_hashes: Tuple[str, ...],
            explicit_binding_keys: Tuple[Tuple[str, str], ...],
    ) -> Dict[str, object]:
        """
        Build the bind-family request plan for a conjured Spellbook.

        Contract:
            - Resolves exactly one paired root conduit for the Spellbook.
            - Claims spellbook, conduit, conduit-ward, and cluster scopes.
            - Adds transaction-owner scopes for the spellbook, conduit, and
              any resolved cluster identities.
        """
        conduit_id = cls._resolve_root_conduit_id(
            devops_information_registry=devops_information_registry,
            identity=identity,
            metadata=metadata,
        )
        conduit_identity = devops_information_registry.get_identity(
            owner_kind="conduit",
            owner_id=conduit_id,
        )
        if conduit_identity is None:
            raise RuntimeError(
                "Bind transaction strategy could not resolve the paired conduit identity."
            )

        scope_keys: Set[str] = {
            transaction_manager.make_scope_key_spellbook(identity.owner_id),
            transaction_manager.make_scope_key_conduit(conduit_id),
            transaction_manager.make_scope_key_identity(
                owner_kind="conduit_ward",
                owner_id=conduit_id,
            ),
        }
        cls._add_transaction_owner_scopes(
            scope_keys=scope_keys,
            transaction_manager=transaction_manager,
            identity=identity,
        )
        cls._add_transaction_owner_scopes(
            scope_keys=scope_keys,
            transaction_manager=transaction_manager,
            identity=conduit_identity,
        )

        affected_identity_keys = {
            (identity.owner_kind, identity.owner_id),
            (conduit_identity.owner_kind, conduit_identity.owner_id),
            ("conduit_ward", conduit_id),
        }
        cluster_ids = devops_information_registry.get_clusters_for_conduit(conduit_id)
        for cluster_id in cluster_ids:
            scope_keys.add(transaction_manager.make_scope_key_cluster(cluster_id))
            affected_identity_keys.add(("conduit_cluster", cluster_id))
            cluster_identity = devops_information_registry.get_identity(
                owner_kind="conduit_cluster",
                owner_id=cluster_id,
            )
            if cluster_identity is None:
                continue
            cls._add_transaction_owner_scopes(
                scope_keys=scope_keys,
                transaction_manager=transaction_manager,
                identity=cluster_identity,
            )

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["spellbook_id"] = identity.owner_id
        normalized_metadata["bind_mode"] = "post_conjure"
        normalized_metadata["root_conduit_id"] = conduit_id
        normalized_metadata["affected_cluster_ids"] = tuple(sorted(cluster_ids))
        normalized_metadata["affected_identity_keys"] = tuple(
            sorted(affected_identity_keys)
        )
        return {
            "initiator_conduit_id": conduit_id,
            "spellbook_id": identity.owner_id,
            "conduit_ids": (conduit_id,),
            "scope_keys": tuple(sorted(scope_keys.union(explicit_scope_keys))),
            "scope_claims": (
                (
                    transaction_manager.make_scope_key_spellbook(identity.owner_id),
                    ClaimMode.INTENT.value,
                ),
            ) + tuple(
                (
                    transaction_manager.make_scope_key_cluster(cluster_id),
                    ClaimMode.INTENT.value,
                )
                for cluster_id in sorted(cluster_ids)
            ),
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": explicit_binding_keys,
            "contract_keys": tuple(),
            "granted_capabilities": ("bind",),
            "required_capabilities": ("bind",),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def _resolve_root_conduit_id(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> str:
        """
        Resolve the one paired root conduit id for a conjured Spellbook.

        Contract:
            - Prefers an explicit metadata conduit id when supplied.
            - Otherwise resolves the single paired conduit from the registry.
            - Raises when no paired conduit can be resolved for a conjured
              Spellbook.
        """
        conduit_id = metadata.get("conduit_id")
        if isinstance(conduit_id, str) and conduit_id.strip():
            return conduit_id
        resolved_conduit_id = (
            devops_information_registry.get_primary_conduit_id_for_spellbook(
                identity.owner_id,
            )
        )
        if resolved_conduit_id is None:
            raise RuntimeError(
                "Bind transaction strategy expected a paired root conduit for a conjured Spellbook."
            )
        return resolved_conduit_id

    @staticmethod
    def _add_transaction_owner_scopes(
            *,
            scope_keys: Set[str],
            transaction_manager: "ChangeControlTransactionManager",
            identity: DevopsIdentity,
    ) -> None:
        """
        Add transaction-owner scopes for every transaction on one identity.

        Contract:
            - Uses the identity's declared available transactions only.
            - Adds one scope per transaction kind for that identity.
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
        No start-side coordination.

        Contract:
            - Spellbook-local bind state is prepared by the Spellbook itself
              (Spellbook.begin_transaction), not by this DevOps strategy. The
              mediator owns only the change-control envelope (admission/scopes),
              so this strategy never reaches into the Spellbook runtime.
        """
        del devops_information_registry, identity, metadata
        return None

    @staticmethod
    def on_end(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        No end-side coordination.

        Contract:
            - Spellbook-local bind state is cleared by the Spellbook itself
              (Spellbook.end_transaction), not by this DevOps strategy.
        """
        del devops_information_registry, identity, metadata
        return None
