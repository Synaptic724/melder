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


class AddSpellToContractTransactionStrategy(TransactionStrategy):
    """
    Add-spell-to-contract transaction resolver (grant/borrow one spell across a link).

    Purpose:
        Resolve one `ADD_SPELL_TO_CONTRACT` request -- a single spell being added
        to the contract between the borrower conduit and its provider peer. This
        is the self-admitting envelope used when the add is performed standalone
        rather than inside an existing link/cluster transaction.

    Contract:
        - Seals both participating conduits (the borrower and the provider peer)
          and their wards EXCLUSIVE, because the contract mutation writes the
          borrower ward and reads the provider surface; this blocks link, unlink,
          transfer, cluster, and other contract work on either side for the
          duration. The owning spellbook(s) are claimed INTENT so the add does
          not serialize unrelated piece-work on a whole spellbook.
        - The actual contract write runs inside the held window via the
          Conduit-owned `_conduit_ward._add_spell_to_contract` seam.
        - Envelope-only: this strategy never reaches into the runtime.
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
        Build the change-control request inputs for one add-spell-to-contract transaction.
        """
        del devops_information_registry
        conduit_ids: Set[str] = set()
        for key in ("owner_conduit_id", "peer_conduit_id", "source_conduit_id", "target_conduit_id"):
            value = metadata.get(key)
            if isinstance(value, str) and value:
                conduit_ids.add(value)
        if not conduit_ids:
            conduit_ids.add(identity.owner_id)

        spellbook_id = metadata.get("spellbook_id")
        if not isinstance(spellbook_id, str) or not spellbook_id:
            spellbook_id = None

        binding_key = cls._resolve_binding_key(metadata=metadata)

        scope_keys: Set[str] = set()
        scope_claims: List[Tuple[str, str]] = []
        for conduit_id in sorted(conduit_ids):
            conduit_scope = transaction_manager.make_scope_key_conduit(conduit_id)
            ward_scope = transaction_manager.make_scope_key_identity(
                owner_kind="conduit_ward",
                owner_id=conduit_id,
            )
            scope_keys.add(conduit_scope)
            scope_claims.append((conduit_scope, ClaimMode.EXCLUSIVE.value))
            scope_keys.add(ward_scope)
            scope_claims.append((ward_scope, ClaimMode.EXCLUSIVE.value))
        if spellbook_id is not None:
            spellbook_scope = transaction_manager.make_scope_key_spellbook(spellbook_id)
            scope_keys.add(spellbook_scope)
            scope_claims.append((spellbook_scope, ClaimMode.INTENT.value))
        if binding_key is not None:
            binding_scope = transaction_manager.make_scope_key_binding(
                binding_key[0],
                binding_key[1],
            )
            scope_keys.add(binding_scope)
            scope_claims.append((binding_scope, ClaimMode.EXCLUSIVE.value))
        scope_keys.update(metadata.get("scope_keys", ()))

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["contract_mode"] = "add_spell_to_contract"

        initiator = metadata.get("initiator_conduit_id")
        if not isinstance(initiator, str) or not initiator:
            owner_conduit_id = metadata.get("owner_conduit_id")
            if isinstance(owner_conduit_id, str) and owner_conduit_id:
                initiator = owner_conduit_id
            else:
                initiator = identity.owner_id

        return {
            "initiator_conduit_id": initiator,
            "spellbook_id": spellbook_id,
            "conduit_ids": tuple(sorted(conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_claims": tuple(scope_claims),
            "scope_hashes": tuple(metadata.get("scope_hashes", ())),
            "binding_keys": tuple(metadata.get("binding_keys", ())),
            "contract_keys": tuple(metadata.get("contract_keys", ())),
            "granted_capabilities": ("add_spell_to_contract", "contract_mutation"),
            "required_capabilities": ("add_spell_to_contract", "contract_mutation"),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def _resolve_binding_key(
            *,
            metadata: Dict[str, object],
    ) -> Optional[Tuple[str, str]]:
        """
        Resolve the targeted (frame_key, binding_key) lookup pair, if supplied.
        """
        binding_key = metadata.get("binding_key")
        if (
            isinstance(binding_key, (tuple, list))
            and len(binding_key) == 2
            and all(isinstance(part, str) and part for part in binding_key)
        ):
            return (binding_key[0], binding_key[1])
        return None

    @staticmethod
    def on_start(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """Add-spell-to-contract transactions need no extra local start-side effects right now."""
        return None

    @staticmethod
    def on_end(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """Add-spell-to-contract transactions need no extra local end-side effects right now."""
        return None
