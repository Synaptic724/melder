from typing import TYPE_CHECKING, Any, Dict, Tuple

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


class BindTransactionStrategy:
    """
    Static transaction strategy for bind requests.

    Purpose:
        Resolve how one bind request should be represented inside
        change-control land so callers only need to provide an identity plus
        metadata and do not carry transaction policy logic themselves.

    Contract:
        - Uses the submitter identity's available transaction names as the
          blocked transaction family for the Spellbook.
        - Expands affected conduit scope by querying the frame-local
          `DevopsInformationRegistry` instead of relying on spellbook-owned
          policy logic.
        - Uses the registry again during start/end side effects to resolve the
          live Spellbook object for bind-local pending-state setup and cleanup.
    """

    @staticmethod
    def build_start_plan(
            *,
            transaction_manager: "ChangeControlTransactionManager",
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build the change-control request inputs for one bind transaction.

        Args:
            transaction_manager:
                Scope-key helper owner used to normalize the bind request.
            devops_information_registry:
                Frame-local topology registry used to expand affected conduits
                and their transaction surfaces.
            identity:
                Spellbook identity originating the bind/scan family.
            metadata:
                Caller-supplied bind metadata.

        Returns:
            Dict[str, object]:
                Normalized request inputs for mediator admission.

        Contract:
            - Starts from the spellbook identity and expands to all known
              conduits currently mapped to that spellbook in the registry.
            - Adds spellbook transaction-owner scopes for every transaction the
              spellbook identity may originate.
            - Adds conduit scopes and conduit transaction-owner scopes for each
              affected conduit identity resolved from the registry.
            - Preserves caller-supplied explicit scope and binding metadata.

        """
        conduit_id = metadata.get("conduit_id")
        explicit_scope_keys = tuple(metadata.get("scope_keys", ()))
        explicit_scope_hashes = tuple(metadata.get("scope_hashes", ()))
        explicit_binding_keys = tuple(metadata.get("binding_keys", ()))
        initiator_conduit_id = f"spellbook:{identity.owner_id}"
        conduit_ids = list(
            devops_information_registry.get_conduits_for_spellbook(
                identity.owner_id,
            )
        )
        if isinstance(conduit_id, str) and conduit_id.strip():
            initiator_conduit_id = conduit_id
            if conduit_id not in conduit_ids:
                conduit_ids.append(conduit_id)
        elif conduit_ids:
            initiator_conduit_id = conduit_ids[0]

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
        for affected_conduit_id in conduit_ids:
            scope_keys.append(
                transaction_manager.make_scope_key_conduit(affected_conduit_id)
            )
            conduit_identity = devops_information_registry.get_identity(
                owner_kind="conduit",
                owner_id=affected_conduit_id,
            )
            if conduit_identity is None:
                continue
            for transaction_name in conduit_identity.available_transactions:
                scope_keys.append(
                    transaction_manager.make_scope_key_transaction_owner(
                        owner_kind="conduit",
                        owner_id=affected_conduit_id,
                        transaction_name=transaction_name,
                    )
                )

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["spellbook_id"] = identity.owner_id
        normalized_metadata["affected_conduit_ids"] = tuple(conduit_ids)
        return {
            "initiator_conduit_id": initiator_conduit_id,
            "spellbook_id": identity.owner_id,
            "conduit_ids": tuple(conduit_ids),
            "scope_keys": tuple(
                dict.fromkeys(tuple(scope_keys) + explicit_scope_keys)
            ),
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": explicit_binding_keys,
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
        Prepare Spellbook-local bind state after bind admission succeeds.

        Contract:
            - Resolves the live Spellbook object through the registry rather
              than trusting caller-owned metadata to carry that object.
            - Raises when the owning Spellbook cannot be resolved because bind
              local-state setup cannot proceed safely without it.
        """
        spellbook = devops_information_registry.get_object(
            owner_kind=identity.owner_kind,
            owner_id=identity.owner_id,
        )
        if spellbook is None:
            raise RuntimeError(
                "Bind transaction strategy could not resolve the owning Spellbook object."
            )
        spellbook._prepare_bind_transaction_state()

    @staticmethod
    def on_end(
            *,
            devops_information_registry: DevopsInformationRegistry,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> None:
        """
        Clear Spellbook-local bind state after bind finalization.

        Contract:
            - Best effort when the owning Spellbook can no longer be resolved.
            - No-ops when the registry no longer has the spellbook object.
        """
        spellbook = devops_information_registry.get_object(
            owner_kind=identity.owner_kind,
            owner_id=identity.owner_id,
        )
        if spellbook is None:
            return
        spellbook._clear_bind_transaction_state()
