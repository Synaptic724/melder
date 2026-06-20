from typing import TYPE_CHECKING, Dict, Set, Tuple

from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.strategies.transaction_strategy import (
    TransactionStrategy,
)
from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
    DevopsInformationRegistry,
)
from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )


class TransferOwnershipTransactionStrategy(TransactionStrategy):
    """
    Ownership-transfer transaction resolver (DevOps scope isolation only).

    Purpose:
        Resolve one `TRANSFER_OWNERSHIP` request into the normalized change-control
        plan used by the mediator, using ONLY the affected footprint the conduit
        call site already discovered and stamped into metadata.

    Design split:
        - The Conduit owns the transaction AND the footprint discovery: it runs the
          read-only `TransferOfOwnership` preflight in
          `Conduit._build_transfer_transaction_metadata` (it holds the live source
          conduit, the live spell, and may reach the runtime because it IS the
          runtime), and passes the full footprint in metadata.
        - This strategy owns ONLY the DevOps scope plan: it turns the metadata
          footprint into scope keys + transaction-owner scopes. It never resolves a
          live conduit/cluster/spell object and never constructs `TransferOfOwnership`.
        - `TransferOfOwnership` owns execution (run in-window by the ward).

    Contract:
        - Requires a conduit submitter identity.
        - Requires `participant_conduit_ids` in metadata (the footprint built by the
          conduit call site); raises if absent.
        - Reads `participant_conduit_ids`, `affected_cluster_ids`,
          `affected_identity_keys`, `binding_keys`, and `source_spellbook_id` from
          metadata.
        - Uses only `transaction_manager.make_scope_key_*` and registry
          `get_identity` (a topology read used by every strategy to add
          transaction-owner scopes). No live-object reach.
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
        Build the change-control request inputs for one ownership transfer.

        Args:
            transaction_manager:
                Scope-key helper owner used to normalize the transfer request.
            devops_information_registry:
                Frame-local topology registry used only to resolve affected
                identities for transaction-owner scopes.
            identity:
                Conduit identity originating the transfer request.
            metadata:
                Transfer metadata, including the affected footprint discovered by
                the conduit call site.

        Returns:
            Dict[str, object]:
                Normalized request inputs for mediator admission.

        Raises:
            RuntimeError: If the submitter is not a conduit, or the conduit-built
                footprint (`participant_conduit_ids`) is missing from metadata.
        """
        if identity.owner_kind != "conduit":
            raise RuntimeError(
                "Transfer-ownership transactions must originate from a conduit identity."
            )

        participant_conduit_ids = tuple(metadata.get("participant_conduit_ids", ()))
        if not participant_conduit_ids:
            raise RuntimeError(
                "Transfer-ownership transaction requires participant_conduit_ids metadata "
                "(the affected footprint is discovered by the conduit call site)."
            )

        affected_cluster_ids = tuple(metadata.get("affected_cluster_ids", ()))
        affected_identity_keys: Set[Tuple[str, str]] = {
            (str(owner_kind), str(owner_id))
            for owner_kind, owner_id in metadata.get("affected_identity_keys", ())
        }
        source_spellbook_id = metadata.get("source_spellbook_id")

        explicit_scope_keys = tuple(metadata.get("scope_keys", ()))
        explicit_scope_hashes = tuple(metadata.get("scope_hashes", ()))
        explicit_contract_keys = tuple(metadata.get("contract_keys", ()))
        binding_keys = tuple(metadata.get("binding_keys", ()))

        conduit_ids: Set[str] = {
            str(conduit_id) for conduit_id in participant_conduit_ids
        }
        cluster_ids: Set[str] = {str(cluster_id) for cluster_id in affected_cluster_ids}

        scope_keys: Set[str] = set(explicit_scope_keys)
        for conduit_id in conduit_ids:
            scope_keys.add(transaction_manager.make_scope_key_conduit(conduit_id))
            scope_keys.add(
                transaction_manager.make_scope_key_identity(
                    owner_kind="conduit_ward",
                    owner_id=conduit_id,
                )
            )

        spellbook_ids = cls._collect_spellbook_ids_from_identities(
            affected_identity_keys=affected_identity_keys,
        )
        for spellbook_id in spellbook_ids:
            scope_keys.add(transaction_manager.make_scope_key_spellbook(spellbook_id))

        for cluster_id in cluster_ids:
            scope_keys.add(transaction_manager.make_scope_key_cluster(cluster_id))

        for frame_key, binding_key in binding_keys:
            scope_keys.add(
                transaction_manager.make_scope_key_binding(frame_key, binding_key)
            )

        for owner_kind, owner_id in sorted(affected_identity_keys):
            resolved_identity = devops_information_registry.get_identity(
                owner_kind=owner_kind,
                owner_id=owner_id,
            )
            if resolved_identity is None:
                continue
            cls._add_transaction_owner_scopes(
                scope_keys=scope_keys,
                transaction_manager=transaction_manager,
                identity=resolved_identity,
            )

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata.setdefault("transfer_mode", "conduit_transfer_ownership")
        normalized_metadata["participant_conduit_ids"] = tuple(sorted(conduit_ids))
        normalized_metadata["affected_cluster_ids"] = tuple(sorted(cluster_ids))
        normalized_metadata["affected_identity_keys"] = tuple(
            sorted(affected_identity_keys)
        )

        return {
            "initiator_conduit_id": identity.owner_id,
            "spellbook_id": source_spellbook_id,
            "conduit_ids": tuple(sorted(conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": binding_keys,
            "contract_keys": explicit_contract_keys,
            "granted_capabilities": (
                "transfer_ownership",
                "contract_mutation",
                "cluster_link",
            ),
            "required_capabilities": (
                "transfer_ownership",
                "contract_mutation",
                "cluster_link",
            ),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def _collect_spellbook_ids_from_identities(
            *,
            affected_identity_keys: Set[Tuple[str, str]],
    ) -> Set[str]:
        """
        Collect spellbook ids from the affected identity set.

        Args:
            affected_identity_keys:
                Affected identity keys supplied by the conduit footprint.

        Returns:
            Set[str]:
                Spellbook ids represented in the affected identity set.
        """
        spellbook_ids: Set[str] = set()
        for owner_kind, owner_id in affected_identity_keys:
            if owner_kind == "spellbook":
                spellbook_ids.add(owner_id)
        return spellbook_ids

    @staticmethod
    def _add_transaction_owner_scopes(
            *,
            scope_keys: Set[str],
            transaction_manager: "ChangeControlTransactionManager",
            identity: DevopsIdentity,
    ) -> None:
        """
        Add transaction-owner scopes for every declared transaction on one identity.

        Args:
            scope_keys:
                Scope-key set being accumulated.
            transaction_manager:
                Scope-key helper owner.
            identity:
                Identity whose available transactions should be turned into
                owner-specific scopes.
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
        Ownership-transfer transactions do not need extra local start effects yet.
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
        Ownership-transfer transactions do not need extra local end effects yet.
        """
        return None
