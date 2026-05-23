from typing import TYPE_CHECKING, Dict, Set, Tuple

from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy import (
    TransactionStrategy,
)
if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )
    from melder.aether.aetheric_frame.dev_ops.devops_identity import DevopsIdentity


class ClusterLinkTransactionStrategy(TransactionStrategy):
    """
    Cluster-owned share/unshare transaction resolver.

    Purpose:
        Resolve one `CLUSTER_LINK` transaction into the normalized
        change-control plan used by the mediator for cluster-driven share and
        unshare operations.

    Runtime shape:
        - one initiating conduit
        - at least one peer conduit
        - one owning cluster identity
        - the wards and spellbooks attached to the participating conduits

    Contract:
        - Uses metadata supplied by the cluster-owned runtime operation to
          validate participants and cluster identity.
        - Uses sets for scope and identity accumulation, then normalizes once
          at the return boundary.
        - Grants cluster-link plus contract-mutation capability because the
          actual runtime work still mutates cross-conduit contract surfaces.
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
        Build the change-control request inputs for one cluster-owned share/unshare operation.
        """
        cluster_id = cls._resolve_cluster_id(identity=identity, metadata=metadata)
        conduit_ids = cls._resolve_participant_conduit_ids(metadata=metadata)
        explicit_scope_keys = tuple(metadata.get("scope_keys", ()))
        explicit_scope_hashes = tuple(metadata.get("scope_hashes", ()))
        explicit_binding_keys = tuple(metadata.get("binding_keys", ()))
        explicit_contract_keys = tuple(metadata.get("contract_keys", ()))

        scope_keys: Set[str] = set(explicit_scope_keys)
        scope_keys.add(transaction_manager.make_scope_key_cluster(cluster_id))
        affected_identity_keys: Set[Tuple[str, str]] = {
            ("conduit_cluster", cluster_id),
        }

        cluster_identity = devops_information_registry.get_identity(
            owner_kind="conduit_cluster",
            owner_id=cluster_id,
        )
        if cluster_identity is not None:
            cls._add_transaction_owner_scopes(
                scope_keys=scope_keys,
                transaction_manager=transaction_manager,
                identity=cluster_identity,
            )

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
            scope_keys.add(
                transaction_manager.make_scope_key_spellbook(spellbook_id)
            )
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
        normalized_metadata["cluster_mode"] = "cluster_link"
        normalized_metadata["cluster_id"] = cluster_id
        normalized_metadata["participant_conduit_ids"] = tuple(sorted(conduit_ids))
        normalized_metadata["affected_identity_keys"] = tuple(
            sorted(affected_identity_keys)
        )

        spellbook_id = identity.metadata.get("spellbook_id")
        if not isinstance(spellbook_id, str) or not spellbook_id:
            spellbook_id = None

        return {
            "initiator_conduit_id": identity.owner_id,
            "spellbook_id": spellbook_id,
            "conduit_ids": tuple(sorted(conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": explicit_binding_keys,
            "contract_keys": explicit_contract_keys,
            "granted_capabilities": ("cluster_link", "contract_mutation"),
            "required_capabilities": ("cluster_link", "contract_mutation"),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def _resolve_cluster_id(
            *,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> str:
        """
        Resolve the cluster identity backing this transaction.
        """
        cluster_id = metadata.get("cluster_id")
        if isinstance(cluster_id, str) and cluster_id.strip():
            return cluster_id
        raise RuntimeError(
            "Cluster-link transaction requires cluster_id metadata."
        )

    @staticmethod
    def _resolve_participant_conduit_ids(
            *,
            metadata: Dict[str, object],
    ) -> Set[str]:
        """
        Resolve and validate the participating conduit ids for one cluster-link request.
        """
        conduit_ids: Set[str] = set()
        raw_ids = metadata.get("conduit_ids", ())
        for conduit_id in raw_ids:
            if not isinstance(conduit_id, str):
                raise TypeError("conduit_ids must contain string conduit ids.")
            normalized_id = conduit_id.strip()
            if not normalized_id:
                continue
            conduit_ids.add(normalized_id)
        if len(conduit_ids) < 2:
            raise RuntimeError(
                "[CONDUIT_CLUSTER] Cluster link transactions must include at least two conduit ids."
            )
        return conduit_ids

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
        Cluster-link transactions do not need extra local start-side effects right now.
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
        Cluster-link transactions do not need extra local end-side effects right now.
        """
        return None
