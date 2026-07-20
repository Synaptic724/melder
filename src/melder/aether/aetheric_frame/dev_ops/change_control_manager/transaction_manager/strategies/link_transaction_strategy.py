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


class LinkTransactionStrategy(TransactionStrategy):
    """
    Link transaction resolver.

    Purpose:
        Resolve one conduit-owned `LINK` request into the normalized
        change-control plan used by the mediator.

    Runtime shape:
        - the initiating conduit is always affected
        - at least one peer conduit must also be affected
        - each participating conduit implies:
          - the conduit itself
          - its ward
          - its owning spellbook, when resolvable from registry metadata

    Contract:
        - Conduit only supplies public input facts through metadata; this
          strategy owns participant validation and scope planning.
        - Uses sets for scope and affected-identity accumulation, then
          normalizes once at the return boundary.
        - Preserves caller-supplied explicit binding and contract keys.
        - Emits claim modes: participant conduits and their wards stay
          EXCLUSIVE (each side is frozen from other structural work for the
          link's duration, since a link mutates both wards); owning spellbooks
          are claimed INTENT (`ClaimMode.INTENT`) so a whole-spellbook claim
          (such as a transfer's EXCLUSIVE spellbook claim) is excluded while a
          link is in flight, without serializing unrelated piece-work on those
          spellbooks.

    Threading:
        Stateless class-level strategy; concurrency is owned by the mediator
        and the scope claims this plan requests.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the transaction
        family; never instantiated and never bindable.

    Subsystem Context:
        The `link` member of the transaction family and the exact inverse of
        `UnlinkTransactionStrategy`, which mirrors these claim modes because a
        sever mutates the same surfaces. Both sit above `ConduitWard`, which
        performs the actual contract creation under sorted ward lock ordering.

    System Context:
        The mixed claim modes are the interesting engineering here, and they
        encode a precise statement about what a link actually mutates.
        Participant conduits and their wards go EXCLUSIVE because a link
        rewrites BOTH wards' contract indices - each side must be frozen from
        other structural work for the duration. Owning spellbooks go INTENT
        because a link touches only a contract bucket on each book, not the
        book as a whole.
        `INTENT` is what makes concurrency tolerable at frame scale: it
        excludes a whole-spellbook EXCLUSIVE claim (a transfer, say) so those
        two operations cannot interleave destructively, while still permitting
        unrelated piece-work on the same books to proceed. Claiming the
        spellbooks EXCLUSIVE instead would be correct but would serialize
        every book that participates in any link, which in a densely linked
        frame is close to serializing the frame.
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
        Build the change-control request inputs for one link transaction.
        """
        conduit_ids = cls._resolve_participant_conduit_ids(
            identity=identity,
            metadata=metadata,
        )
        explicit_scope_keys = tuple(metadata.get("scope_keys", ()))
        explicit_scope_hashes = tuple(metadata.get("scope_hashes", ()))
        explicit_binding_keys = tuple(metadata.get("binding_keys", ()))
        explicit_contract_keys = tuple(metadata.get("contract_keys", ()))

        scope_keys: Set[str] = set(explicit_scope_keys)
        affected_identity_keys: Set[Tuple[str, str]] = set()
        affected_spellbook_ids: Set[str] = set()

        for conduit_id in conduit_ids:
            scope_keys.add(transaction_manager.make_scope_key_conduit(conduit_id))
            scope_keys.add(
                transaction_manager.make_scope_key_identity(
                    owner_kind="conduit_ward",
                    owner_id=conduit_id,
                )
            )
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
            affected_identity_keys.add(("conduit_ward", conduit_id))

            spellbook_id = devops_information_registry.get_spellbook_for_conduit(
                conduit_id
            )
            if spellbook_id is None:
                continue
            affected_spellbook_ids.add(spellbook_id)
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
        normalized_metadata["link_mode"] = "conduit_link"
        normalized_metadata["participant_conduit_ids"] = tuple(sorted(conduit_ids))
        normalized_metadata["affected_spellbook_ids"] = tuple(
            sorted(affected_spellbook_ids)
        )
        normalized_metadata["affected_identity_keys"] = tuple(
            sorted(affected_identity_keys)
        )

        spellbook_id = identity.metadata.get("spellbook_id")
        if not isinstance(spellbook_id, str) or not spellbook_id:
            spellbook_id = None

        # Owning spellbooks are claimed INTENT, not EXCLUSIVE: a link only adds
        # one contract bucket to each spellbook, so it should block a
        # whole-spellbook claim (transfer) without serializing unrelated
        # piece-work. Conduits and wards are left to default EXCLUSIVE.
        spellbook_scope_claims: Tuple[Tuple[str, str], ...] = tuple(
            (
                transaction_manager.make_scope_key_spellbook(affected_spellbook_id),
                ClaimMode.INTENT.value,
            )
            for affected_spellbook_id in sorted(affected_spellbook_ids)
        )

        return {
            "initiator_conduit_id": identity.owner_id,
            "spellbook_id": spellbook_id,
            "conduit_ids": tuple(sorted(conduit_ids)),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_claims": spellbook_scope_claims,
            "scope_hashes": explicit_scope_hashes,
            "binding_keys": explicit_binding_keys,
            "contract_keys": explicit_contract_keys,
            "granted_capabilities": ("link", "contract_mutation"),
            "required_capabilities": ("link", "contract_mutation"),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def _resolve_participant_conduit_ids(
            *,
            identity: DevopsIdentity,
            metadata: Dict[str, object],
    ) -> Set[str]:
        """
        Resolve and validate the participating conduit ids for one link request.
        """
        conduit_ids: Set[str] = {identity.owner_id}
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
                "[CONDUIT] Link transactions must include the local conduit and at least one peer conduit."
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
        Link transactions do not need extra local start-side effects right now.
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
        Link transactions do not need extra local end-side effects right now.
        """
        return None
