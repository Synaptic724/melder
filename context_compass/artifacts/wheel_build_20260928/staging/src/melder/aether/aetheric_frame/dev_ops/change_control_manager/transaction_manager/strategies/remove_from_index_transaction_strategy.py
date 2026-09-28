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


class RemoveFromIndexTransactionStrategy(TransactionStrategy):
    """
    Remove-from-index transaction resolver (move a spell out to a fresh index).

    Purpose:
        Resolve one spellbook-owned `REMOVE_FROM_INDEX` request. Because a spell
        is always in exactly one index, removing it is a move-out to a fresh
        fresh index established inside this same transaction (the split).

    Contract:
        - Seals off the owning spellbook and conduit EXCLUSIVELY, plus the moved
          spell's binding key. Blocks bind/transfer/link/sever/cluster and other
          index ops on that spellbook+conduit, isolated to them.
        - The owned-spell move into a fresh index runs inside the held window via
          the Spellbook-owned `_apply_remove_from_index` seam.

    Threading:
        Stateless class-level strategy; concurrency is owned by the mediator
        and the scope claims this plan requests.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the transaction
        family; never instantiated and never bindable.

    Subsystem Context:
        The move-out counterpart to `AddToIndexTransactionStrategy`, sharing
        the same one-index-per-spell invariant.

    System Context:
        Removal is a MOVE, not a deletion, and that follows directly from the
        invariant: since a spell is always in exactly one index, taking it out
        of its current index requires somewhere for it to land. A fresh index
        is established inside this same transaction - the split.
        This is why the seal is narrower than the move-in's: only one spellbook
        and one conduit are involved, because the destination index is created
        here rather than being an existing surface some other transaction might
        be holding.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Remove-from-index transaction resolver (move a spell out to a fresh
        index). Melder kernel machinery: read it to understand the runtime, do not drive it
        directly.
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
        Build the change-control request inputs for one remove-from-index move.

        Contract:
            Produces the EXCLUSIVE-seal request for a move-out (the split):
            resolves the owning spellbook (owner-id fallback) and acting
            conduit, extends the conduit seal to that conduit's borrowers and
            providers, resolves the optional binding key, and claims them
            EXCLUSIVE via `_seal_scope_keys`. The seal is deliberately narrower
            than the move-in's - one spellbook and one conduit - because the
            destination index is created here rather than being a pre-existing
            surface a peer might hold. Stamps normalized metadata with the
            transaction identity, `index_mode="remove_from_index"`, and the
            quiesce root-conduit footprint that `on_start`/`on_end` freeze. Pure
            planning - no runtime object is mutated here.

        Args:
            transaction_manager:
                Frame-local scope-key/request helper surface.
            devops_information_registry:
                Topology registry used to expand the conduit seal to peers.
            identity:
                Submitter identity (owner-id fallback for the seal).
            metadata:
                Caller metadata carrying the spellbook/conduit ids and options.

        Returns:
            Dict[str, object]:
                Normalized request inputs (initiator, spellbook, sealed conduit
                set, EXCLUSIVE scope claims, capabilities, normalized metadata)
                for mediator admission.
        """
        spellbook_id = metadata.get("spellbook_id")
        if not isinstance(spellbook_id, str) or not spellbook_id:
            spellbook_id = identity.owner_id
        conduit_ids: Set[str] = set()
        owner_conduit_id = metadata.get("owner_conduit_id")
        if isinstance(owner_conduit_id, str) and owner_conduit_id:
            conduit_ids.add(owner_conduit_id)
        # Extend the EXCLUSIVE seal to conduits linked to the acting conduit --
        # its borrowers and providers -- so new links / binds / transfer on those
        # peers are blocked for the op's duration too.
        for acting_conduit_id in tuple(conduit_ids):
            conduit_ids.update(
                devops_information_registry.list_borrowers_for_provider(acting_conduit_id)
            )
            conduit_ids.update(
                devops_information_registry.list_providers_for_borrower(acting_conduit_id)
            )
        binding_key = cls._resolve_binding_key(metadata=metadata)

        scope_keys, scope_claims = cls._seal_scope_keys(
            transaction_manager=transaction_manager,
            spellbook_ids={spellbook_id},
            conduit_ids=conduit_ids,
            binding_key=binding_key,
        )
        scope_keys.update(metadata.get("scope_keys", ()))

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["index_mode"] = "remove_from_index"
        # Freeze footprint (freeze parity with notch, owner-ruled
        # 2026-07-12): the runtime quiesce in on_start/on_end targets
        # exactly the conduit set this plan seals EXCLUSIVE, so no
        # in-flight meld/validator can straddle the member split.
        normalized_metadata["quiesce_root_conduit_ids"] = tuple(
            sorted(conduit_ids)
        )

        initiator = metadata.get("initiator_conduit_id")
        if not isinstance(initiator, str) or not initiator:
            initiator = next(iter(conduit_ids), identity.owner_id)

        return {
            "initiator_conduit_id": initiator,
            "spellbook_id": spellbook_id,
            "conduit_ids": tuple(sorted(conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_claims": tuple(scope_claims),
            "scope_hashes": tuple(metadata.get("scope_hashes", ())),
            "binding_keys": tuple(metadata.get("binding_keys", ())),
            "contract_keys": tuple(metadata.get("contract_keys", ())),
            "granted_capabilities": ("remove_from_index", "spell_index_mutation"),
            "required_capabilities": ("remove_from_index", "spell_index_mutation"),
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
        """
        Freeze the sealed conduits' runtime gates (scopes held) before the split.

        Contract (freeze parity with notch, patch
        notch_conduit_gate_freeze_2026_07_12):
            - Quiesces every plan-derived lineage through the
              metadata-carried DevOps facade in PARK mode; absent facade
              = no-op (envelope-only starts stay legal).
            - A drain timeout raises -> the mediator aborts the start and
              root finalize still dispatches `on_end` (reopen).

        Raises:
            RuntimeError: Propagated from a gate drain timeout.

        Returns:
            None.
        """
        del devops_information_registry, identity
        gate_ops = metadata.get("conduit_lineage_gate_ops")
        if gate_ops is None:
            return
        for root_id in metadata.get("quiesce_root_conduit_ids", ()):
            if isinstance(root_id, str) and root_id:
                gate_ops.quiesce_conduit_lineage(root_id)

    @staticmethod
    def on_end(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """
        Reopen every frozen conduit lineage on every exit path (fail-closed).

        Contract:
            - Mirrors `on_start`'s footprint exactly; absent facade = no-op.
            - Dispatched by the mediator from root-session finalize.

        Returns:
            None.
        """
        del devops_information_registry, identity
        gate_ops = metadata.get("conduit_lineage_gate_ops")
        if gate_ops is None:
            return
        for root_id in metadata.get("quiesce_root_conduit_ids", ()):
            if isinstance(root_id, str) and root_id:
                gate_ops.enable_conduit_lineage(root_id)
