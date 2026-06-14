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


class AddToIndexTransactionStrategy(TransactionStrategy):
    """
    Add-to-index transaction resolver (move a spell into a target index).

    Purpose:
        Resolve one spellbook-owned `ADD_TO_INDEX` request. Moving a spell into
        a target index is a move-in: the spell leaves its current (default)
        index and joins the target; if the source index empties it is GC'd
        inside this same transaction (no empty index ever rests).

    Contract:
        - Seals off the source AND target surfaces EXCLUSIVELY: both owning
          spellbooks and both owning conduits (deduped when the same), plus the
          moved spell's binding key. Blocks bind/transfer/link/sever/cluster and
          other index ops on those surfaces, isolated to them.
        - The member-store move + source GC run inside the held window via the
          Spellbook-owned `_apply_add_to_index` seam (SpellIndex-model lane).
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
        Build the change-control request inputs for one add-to-index transaction.
        """
        del devops_information_registry
        spellbook_ids = cls._collect_ids(
            metadata, ("source_spellbook_id", "target_spellbook_id", "spellbook_id")
        )
        if not spellbook_ids:
            spellbook_ids = {identity.owner_id}
        conduit_ids = cls._collect_ids(
            metadata, ("source_conduit_id", "target_conduit_id", "owner_conduit_id")
        )
        binding_key = cls._resolve_binding_key(metadata=metadata)

        scope_keys, scope_claims = cls._seal_scope_keys(
            transaction_manager=transaction_manager,
            spellbook_ids=spellbook_ids,
            conduit_ids=conduit_ids,
            binding_key=binding_key,
        )
        scope_keys.update(metadata.get("scope_keys", ()))

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["index_mode"] = "add_to_index"

        initiator = metadata.get("initiator_conduit_id")
        if not isinstance(initiator, str) or not initiator:
            initiator = next(iter(sorted(conduit_ids)), identity.owner_id)

        return {
            "initiator_conduit_id": initiator,
            "spellbook_id": metadata.get("spellbook_id") or next(iter(sorted(spellbook_ids)), None),
            "conduit_ids": tuple(sorted(conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_claims": tuple(scope_claims),
            "scope_hashes": tuple(metadata.get("scope_hashes", ())),
            "binding_keys": tuple(metadata.get("binding_keys", ())),
            "contract_keys": tuple(metadata.get("contract_keys", ())),
            "granted_capabilities": ("add_to_index", "spell_index_mutation"),
            "required_capabilities": ("add_to_index", "spell_index_mutation"),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def _collect_ids(metadata: Dict[str, object], keys: Tuple[str, ...]) -> Set[str]:
        """
        Collect non-empty string ids from the named metadata keys.
        """
        out: Set[str] = set()
        for key in keys:
            value = metadata.get(key)
            if isinstance(value, str) and value:
                out.add(value)
        return out

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
    def _seal_scope_keys(
            *,
            transaction_manager: "ChangeControlTransactionManager",
            spellbook_ids: Set[str],
            conduit_ids: Set[str],
            binding_key: Optional[Tuple[str, str]],
    ) -> Tuple[Set[str], List[Tuple[str, str]]]:
        """
        Build the EXCLUSIVE seal: every listed spellbook + conduit, plus the
        targeted binding key, all claimed EXCLUSIVE so bind / transfer / link /
        cluster / other index ops on those surfaces are sealed off for the
        duration, isolated to exactly those spellbooks and conduits.
        """
        scope_keys: Set[str] = set()
        scope_claims: List[Tuple[str, str]] = []
        for spellbook_id in sorted(spellbook_ids):
            scope = transaction_manager.make_scope_key_spellbook(spellbook_id)
            scope_keys.add(scope)
            scope_claims.append((scope, ClaimMode.EXCLUSIVE.value))
        for conduit_id in sorted(conduit_ids):
            scope = transaction_manager.make_scope_key_conduit(conduit_id)
            scope_keys.add(scope)
            scope_claims.append((scope, ClaimMode.EXCLUSIVE.value))
        if binding_key is not None:
            scope = transaction_manager.make_scope_key_binding(
                binding_key[0],
                binding_key[1],
            )
            scope_keys.add(scope)
            scope_claims.append((scope, ClaimMode.EXCLUSIVE.value))
        return scope_keys, scope_claims

    @staticmethod
    def on_start(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """Add-to-index transactions need no extra local start-side effects right now."""
        return None

    @staticmethod
    def on_end(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """Add-to-index transactions need no extra local end-side effects right now."""
        return None
