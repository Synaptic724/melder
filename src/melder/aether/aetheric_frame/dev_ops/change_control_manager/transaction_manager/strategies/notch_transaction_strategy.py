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


class NotchTransactionStrategy(TransactionStrategy):
    """
    Notch transaction resolver (intra-index active-spell repoint).

    Purpose:
        Resolve one spellbook-owned `NOTCH` request into the normalized
        change-control plan. A notch repoints one SpellIndex to a different
        active (resolvable) spell.

    Contract:
        - Seals the op off entirely on the owning surfaces: the owning spellbook
          and its conduit are claimed EXCLUSIVE, plus the targeted binding key.
          This blocks bind/new-spell-creation, transfer_ownership, link, sever,
          cluster, and other index ops on that spellbook+conduit for the
          duration, while staying isolated to exactly those surfaces.
        - RUNTIME FREEZE (owner ruling 2026-07-12, patch
          notch_conduit_gate_freeze_2026_07_12): embargo claims exclude other
          TRANSACTIONS only - a meld-side validator holds no claim, yet its
          verdict writes key by live `selected_spell_id`, so a validator
          straddling the repoint poisons the promoted member (probe-proven).
          `on_start` therefore quiesces every sealed conduit's lineage gates
          through the metadata-carried DevOps `ConduitLineageGateOps` facade:
          new melds park at their `CreationGate`, in-flight melds (validator
          included - the conduit ticket spans the whole meld) drain to zero
          BEFORE the swap. `on_end` reopens every lineage on every exit path
          (the mediator dispatches it from root finalize). A drain timeout in
          `on_start` aborts the transaction teach-grade; the abort path still
          reopens.
        - The active-spell repoint itself runs inside the held window via the
          Spellbook-owned `_apply_notch` seam (SpellIndex-model lane).
        - The targeted binding key is also emitted into the staged mutation's
          `binding_keys`, so the generalized commit-side machinery fires for a
          notch exactly like it does for a bind: the structural commit
          validator runs phases 1-4 for the promoted member (delegating to the
          owning Spellbook's own phase runner) and the commit dirty-marker
          dirties dependents in `SpellSystemStates`.

    Call-site metadata contract (freeze inputs):
        - "conduit_lineage_gate_ops": ConduitLineageGateOps - the DevOps
          drain/reopen facade (absent = freeze no-op, mirroring the unelect
          precedent so envelope-only starts stay legal in tests).
        - "quiesce_root_conduit_ids" is PLAN-DERIVED: `build_start_plan`
          stashes the sealed conduit set into normalized metadata so
          `on_start`/`on_end` freeze exactly the surfaces the seal claims.

    Threading:
        Stateless class-level strategy, but it owns the most intricate
        concurrency behaviour in the family: it drains conduit lineage gates in
        `on_start` and reopens them in `on_end` on EVERY exit path, including
        the drain-timeout abort.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the transaction
        family; never instantiated and never bindable.

    Subsystem Context:
        The `notch` member of the transaction family, paired with
        `add_to_index` and `remove_from_index` as the three SpellIndex mutation
        flows. All three run through the same admission path, but only notch
        needs the runtime freeze.

    System Context:
        This strategy documents the single most important limitation of the
        change-control model, and it is worth internalizing beyond this class:
        EMBARGO CLAIMS EXCLUDE OTHER TRANSACTIONS ONLY. A meld-side validator
        holds no claim at all, so scope claims alone cannot make it wait.
        That gap is not theoretical - it was probe-proven. A validator
        straddling the repoint writes its verdict keyed by the LIVE
        `selected_spell_id`, so if the swap lands mid-validation the verdict
        attaches to the newly promoted member and poisons it. No amount of
        additional claiming fixes this, because the racing party is not a
        transaction.
        The answer is therefore a different mechanism entirely: quiesce the
        RUNTIME. `on_start` parks new melds at each sealed conduit's
        `CreationGate` and drains in-flight melds to zero - the conduit ticket
        spans the whole meld, so the validator drains with them - and only then
        does the swap proceed. `on_end` reopens on every exit path because a
        gate left closed would silently wedge the conduit; that is why the
        abort path reopens too rather than relying on the happy path.
        The lesson generalizes: transaction claims serialize STRUCTURE, gates
        serialize RUNTIME, and an operation that races runtime readers needs
        both.
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
        Build the change-control request inputs for one notch transaction.
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
        # peers are blocked for the op's duration too (the notch changes what they
        # resolve through their contracts).
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
        normalized_metadata["index_mode"] = "notch"
        # Freeze footprint: the runtime quiesce in on_start/on_end targets
        # exactly the conduit set this plan seals EXCLUSIVE, so gate freeze
        # and embargo seal never diverge.
        normalized_metadata["quiesce_root_conduit_ids"] = tuple(
            sorted(conduit_ids)
        )

        # Stage the promoted member's binding key onto the request so the
        # commit-side structural validator and dirty-marker (the same
        # generalized staged-keys path bind uses) participate at notch commit.
        staged_binding_keys: List[Tuple[str, str]] = [
            (frame_key, bind_key)
            for frame_key, bind_key in metadata.get("binding_keys", ())
        ]
        if binding_key is not None and binding_key not in staged_binding_keys:
            staged_binding_keys.append(binding_key)

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
            "binding_keys": tuple(staged_binding_keys),
            "contract_keys": tuple(metadata.get("contract_keys", ())),
            "granted_capabilities": ("notch", "spell_index_mutation"),
            "required_capabilities": ("notch", "spell_index_mutation"),
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
        Freeze the sealed conduits' runtime gates (scopes held) before the swap.

        Purpose:
            Give the notch-holding thread exclusive RUNTIME rights, not just
            plane rights: park new melds at their `CreationGate` and drain
            every in-flight meld ticket to zero, so no meld-side validator
            can straddle the `selected_spell_id` repoint (its verdict would
            land keyed to the promoted member - the probe-proven poison).

        Contract:
            - Reads the DevOps facade from
              `metadata["conduit_lineage_gate_ops"]`; absent facade = no-op
              (unelect precedent - envelope-only starts stay legal).
            - Quiesces every plan-derived `quiesce_root_conduit_ids` lineage
              in PARK mode (non-terminal; melds resume on reopen).
            - A drain timeout raises here -> the mediator aborts the start
              and root finalize still dispatches `on_end` (reopen).

        Raises:
            RuntimeError: Propagated from a gate drain timeout.
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
            - Dispatched by the mediator from root-session finalize, so the
              reopen fires once per root end - commit, abort, or error.
        """
        del devops_information_registry, identity
        gate_ops = metadata.get("conduit_lineage_gate_ops")
        if gate_ops is None:
            return
        for root_id in metadata.get("quiesce_root_conduit_ids", ()):
            if isinstance(root_id, str) and root_id:
                gate_ops.enable_conduit_lineage(root_id)
