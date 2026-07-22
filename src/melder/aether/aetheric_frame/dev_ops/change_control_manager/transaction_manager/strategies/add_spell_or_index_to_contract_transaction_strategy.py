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


class AddSpellOrIndexToContractTransactionStrategy(TransactionStrategy):
    """
    Add-spell-or-index-to-contract transaction resolver (grant/borrow across a link).

    Purpose:
        Resolve one `ADD_SPELL_OR_INDEX_TO_CONTRACT` request -- a single spell or
        spell index being added to the contract between the borrower conduit and
        its provider peer. This is the self-admitting envelope used when the add
        is performed standalone rather than inside an existing link/cluster
        transaction.

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

    Threading:
        Stateless class-level strategy; concurrency is owned by the mediator
        and the scope claims this plan requests.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the transaction
        family; never instantiated and never bindable.

    Subsystem Context:
        The grant half of the standalone contract-mutation pair, inverse of
        `RemoveSpellOrIndexFromContractTransactionStrategy`. Both are
        SELF-ADMITTING envelopes for work that would otherwise ride inside a
        link or cluster transaction.

    System Context:
        "Self-admitting" is the distinction that matters. The same contract
        mutation performed INSIDE a held link or cluster transaction must not
        open its own envelope - that is the self-conflict trap the cluster
        strategies warn about, where an inner transaction contends with the
        seal already covering it and times out. This strategy exists for the
        standalone case only.
        The asymmetric claim shape follows the actual work: both conduits and
        wards go EXCLUSIVE because the mutation WRITES the borrower ward and
        READS the provider surface, while spellbooks go INTENT because a single
        spell or index moving into a contract is piece-work rather than a
        whole-book rewrite.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Add-spell-or-index-to-contract transaction resolver (grant/borrow "
        "across a link). Melder kernel machinery: read it to understand the runtime, do not drive "
        "it directly."
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
        Build the change-control request inputs for one add-to-contract grant.

        Contract:
            Produces the mixed-claim request for a standalone contract add:
            collects the borrower + provider conduit ids from metadata (owner-id
            fallback) and claims each conduit AND its `conduit_ward` identity
            EXCLUSIVE (the mutation writes the borrower ward and reads the
            provider surface); the owning spellbook, when named, is claimed
            INTENT so a single spell/index add does not serialize unrelated
            piece-work on a whole book; an optional binding key is claimed
            EXCLUSIVE. Stamps normalized metadata with the transaction identity
            and `contract_mode="add_spell_or_index_to_contract"`. Envelope-only:
            the registry argument is unused and no runtime object is mutated
            here.

        Args:
            transaction_manager:
                Frame-local scope-key/request helper surface.
            devops_information_registry:
                Unused by this envelope strategy (accepted for contract parity).
            identity:
                Submitter identity (owner-id fallback for the seal + initiator).
            metadata:
                Caller metadata carrying the conduit/spellbook ids and options.

        Returns:
            Dict[str, object]:
                Normalized request inputs (initiator, spellbook, sealed conduit
                set, mixed EXCLUSIVE/INTENT scope claims, capabilities,
                normalized metadata) for mediator admission.
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
        normalized_metadata["contract_mode"] = "add_spell_or_index_to_contract"

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
            "granted_capabilities": ("add_spell_or_index_to_contract", "contract_mutation"),
            "required_capabilities": ("add_spell_or_index_to_contract", "contract_mutation"),
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
        """
        Add-spell-or-index-to-contract transactions need no extra local start-side effects right now.

        Returns:
            None.
        """
        return None

    @staticmethod
    def on_end(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """
        Add-spell-or-index-to-contract transactions need no extra local end-side effects right now.

        Returns:
            None.
        """
        return None
