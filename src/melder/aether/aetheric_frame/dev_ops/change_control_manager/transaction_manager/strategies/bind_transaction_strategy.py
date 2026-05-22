from typing import TYPE_CHECKING, Any, Dict, Tuple

from melder.aether.aetheric_frame.dev_ops.devops_identity import (
    DevopsIdentity,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.transaction_manager.transaction_manager import (
        ChangeControlTransactionManager,
    )


class BindTransactionStrategy:
    """
    Static transaction strategy for bind requests.

    Purpose:
        Resolve how one bind request should be represented inside
        change-control land so callers only need to provide an identity plus
        metadata and do not carry transaction policy logic themselves.

    Contract:
        - Requires `metadata["spellbook"]` to be present.
        - Uses the submitter identity's available transaction names as the
          blocked transaction family for the Spellbook.
        - When `metadata["conduit_id"]` is present, mirrors the same blocked
          transaction family onto the conduit identity surface as well.
    """

    @staticmethod
    def build_start_plan(
            *,
            transaction_manager: "ChangeControlTransactionManager",
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build the change-control request inputs for one bind transaction.

        Args:
            transaction_manager:
                Scope-key helper owner used to normalize the bind request.
            identity:
                Spellbook identity originating the bind.
            metadata:
                Caller-supplied bind metadata. Must include `spellbook`.

        Returns:
            Dict[str, object]:
                Normalized request inputs for mediator admission.

        Raises:
            ValueError: If required spellbook metadata is missing.
        """
        if "spellbook" not in metadata:
            raise ValueError(
                "bind transaction metadata must include the owning spellbook."
            )
        conduit_id = metadata.get("conduit_id")
        explicit_scope_keys = tuple(metadata.get("scope_keys", ()))
        explicit_scope_hashes = tuple(metadata.get("scope_hashes", ()))
        explicit_binding_keys = tuple(metadata.get("binding_keys", ()))
        initiator_conduit_id = f"spellbook:{identity.owner_id}"
        conduit_ids: Tuple[str, ...] = tuple()
        if isinstance(conduit_id, str) and conduit_id.strip():
            initiator_conduit_id = conduit_id
            conduit_ids = (conduit_id,)

        scope_keys = [
            transaction_manager.make_scope_key_spellbook(identity.owner_id),
        ]
        for transaction_name in identity.available_transactions:
            scope_keys.append(
                transaction_manager.make_scope_key_transaction_owner(
                    owner_kind=identity.owner_kind,
                    owner_id=identity.owner_id,
                    transaction_name=transaction_name,
                )
            )
            if conduit_ids:
                scope_keys.append(
                    transaction_manager.make_scope_key_transaction_owner(
                        owner_kind="conduit",
                        owner_id=conduit_ids[0],
                        transaction_name=transaction_name,
                    )
                )

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        return {
            "initiator_conduit_id": initiator_conduit_id,
            "spellbook_id": identity.owner_id,
            "conduit_ids": conduit_ids,
            "scope_keys": tuple(
                dict.fromkeys(tuple(scope_keys) + explicit_scope_keys)
            ),
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": explicit_binding_keys,
            "metadata": normalized_metadata,
        }

    @staticmethod
    def on_start(metadata: Dict[str, object]) -> None:
        """
        Prepare Spellbook-local bind state after bind admission succeeds.
        """
        spellbook = metadata["spellbook"]
        spellbook._prepare_bind_transaction_state()

    @staticmethod
    def on_end(metadata: Dict[str, object]) -> None:
        """
        Clear Spellbook-local bind state after bind finalization.
        """
        spellbook = metadata["spellbook"]
        spellbook._clear_bind_transaction_state()
