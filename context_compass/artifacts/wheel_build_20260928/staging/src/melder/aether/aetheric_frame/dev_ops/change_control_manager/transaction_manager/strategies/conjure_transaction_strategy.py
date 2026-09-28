from typing import TYPE_CHECKING, Dict, Set

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


class ConjureTransactionStrategy(TransactionStrategy):
    """
    Conjure transaction resolver (spellbook -> root conduit genesis).

    Purpose:
        Resolve one spellbook `CONJURE` request into the normalized
        change-control plan. Conjure builds the spellbook's single root Conduit;
        this strategy seals the owning spellbook for the whole creation pipeline
        so the genesis is admitted through the mediator instead of riding the
        Spellbook lock alone.

    Contract:
        - Claims the owning spellbook EXCLUSIVE so bind, scan, link,
          transfer_ownership, and every other spellbook-level transaction is
          blocked for the duration, while different spellbooks still conjure in
          parallel (disjoint scope keys).
        - No conduit, ward, or cluster scope is claimed: the root conduit id is
          minted mid-pipeline and nothing can target the conduit until
          activation registers it.
        - The initiator id is the spellbook pseudo-owner id because no root
          conduit exists yet (mirrors the pre-conjure bind plan).
        - Envelope-only: the conduit build itself runs inside the held window via
          `SpellbookCreationSystem.conjure()`; this strategy never reaches into
          the Spellbook runtime.

    Threading:
        Stateless class-level strategy; concurrency is owned by the mediator
        and the scope claims this plan requests.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the transaction
        family; never instantiated and never bindable.

    Subsystem Context:
        The `conjure` member of the transaction family - the genesis event that
        every other conduit-scoped strategy presupposes. Bind's own plan has a
        pre-conjure and post-conjure shape for exactly this reason: before this
        transaction completes, there is no conduit to claim.

    System Context:
        The deliberate ABSENCE of conduit, ward, and cluster scope is the
        subtle part, and it follows from a chicken-and-egg constraint: the root
        conduit id is minted mid-pipeline, so at plan time there is no id to
        claim. That would be dangerous if anything could target the conduit
        concurrently - but nothing can, because a conduit is unreachable until
        activation registers it. The scope plan is therefore complete despite
        naming only the spellbook.
        The same reasoning explains the pseudo-owner initiator id: the plan
        needs an owner identity and no root conduit exists yet, so it mirrors
        the pre-conjure bind plan rather than inventing an identity.
        Claiming the spellbook EXCLUSIVE for the WHOLE creation pipeline is
        what moves conjure from "riding the Spellbook lock" to being properly
        admitted - and because scope keys are per-spellbook, different books
        still conjure in parallel.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Conjure transaction resolver (spellbook -> root conduit genesis).
        Melder kernel machinery: read it to understand the runtime, do not drive it directly.
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
        Build the change-control request inputs for one conjure transaction.

        Contract:
            - Resolves the owning spellbook id from metadata, falling back to the
              submitter identity owner id.
            - Seals exactly one scope: the owning spellbook, claimed EXCLUSIVE.
            - Records the affected identity key so commit-time fact baselines and
              risk surfaces can attribute the genesis to the spellbook.
        """
        del devops_information_registry
        spellbook_id = metadata.get("spellbook_id")
        if not isinstance(spellbook_id, str) or not spellbook_id:
            spellbook_id = identity.owner_id

        spellbook_scope = transaction_manager.make_scope_key_spellbook(spellbook_id)
        scope_keys: Set[str] = {spellbook_scope}
        scope_keys.update(metadata.get("scope_keys", ()))

        affected_identity_keys = {
            (identity.owner_kind, identity.owner_id),
        }

        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["spellbook_id"] = spellbook_id
        normalized_metadata["conjure_mode"] = "root_conduit"
        normalized_metadata["affected_identity_keys"] = tuple(
            sorted(affected_identity_keys)
        )

        return {
            "initiator_conduit_id": f"spellbook:{spellbook_id}",
            "spellbook_id": spellbook_id,
            "conduit_ids": tuple(),
            "scope_keys": tuple(sorted(scope_keys)),
            "scope_claims": (
                (spellbook_scope, ClaimMode.EXCLUSIVE.value),
            ),
            "scope_hashes": tuple(metadata.get("scope_hashes", ())),
            "binding_keys": tuple(),
            "contract_keys": tuple(),
            "granted_capabilities": ("conjure",),
            "required_capabilities": ("conjure",),
            "metadata": normalized_metadata,
        }

    @staticmethod
    def on_start(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """
        Conjure transactions need no extra local start-side effects right now.

        Returns:
            None.
        """
        return None

    @staticmethod
    def on_end(*, devops_information_registry: DevopsInformationRegistry, identity: DevopsIdentity, metadata: Dict[str, object]) -> None:
        """
        Conjure transactions need no extra local end-side effects right now.

        Returns:
            None.
        """
        return None
