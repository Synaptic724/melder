from typing import TYPE_CHECKING, Dict

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


class RemediationTransactionStrategy(TransactionStrategy):
    """
    Remediation transaction resolver (meld-time lazy revalidation).

    Purpose:
        Close the CONFIRMED lineage race (probe-proven 2026-07-12): a
        remediation window straddling a notch wrote its stale terminal
        verdict onto the shared lineage record and permanently poisoned
        the notched-in member. Owner ruling: remediation is a WRITER -
        it re-runs phases and writes lineage/resolution validity - so
        it rides admission like every other writer.

    Contract:
        - Claims EXACTLY ONE scope: the targeted lineage
          (`lineage:<spell_index_id>`) EXCLUSIVE. The membership
          families (notch/add_to_index/remove_from_index/transfer) add
          the same scope to their seals, so a revalidation window and a
          membership repoint on one lineage provably serialize - in
          BOTH directions.
        - Deliberately narrow: no spellbook/conduit claims (remediation
          mutates no membership; claiming the book would serialize it
          against every bind), no staged binding keys (remediation runs
          its OWN phases; the commit-side structural validator stays
          out), envelope-only preserved.
        - Warm melds and plain validity READS never admit this family -
          only the gated rerun-and-write branch enters the plane (the
          readers-never-enter law survives for actual reads).

    Threading:
        Static-execute like every family strategy; borrows the
        mediator-held collaborators, owns nothing.
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
        Build the change-control request inputs for one remediation.

        Args:
            transaction_manager:
                Scope-key vocabulary owner.
            devops_information_registry:
                Unused (remediation needs no relational fan-out).
            identity:
                The admitting surface's identity (the owning spellbook).
            metadata:
                Must carry `spell_index_id` (the lineage under
                revalidation); `spellbook_id`/`spell_id` ride as
                diagnostic context.

        Returns:
            Dict[str, object]: The normalized request plan (one
            exclusive lineage claim).

        Raises:
            ValueError: If `spell_index_id` is absent or empty.
        """
        spell_index_id = metadata.get("spell_index_id")
        if not isinstance(spell_index_id, str) or not spell_index_id:
            raise ValueError(
                "remediation requires metadata['spell_index_id'] - the "
                "lineage whose validity is being rewritten."
            )
        lineage_scope = transaction_manager.make_scope_key_lineage(
            spell_index_id
        )
        normalized_metadata = dict(metadata)
        normalized_metadata["transaction_identity"] = identity.describe()
        normalized_metadata["remediation_lane"] = str(
            metadata.get("remediation_lane", "structural")
        )
        spellbook_id = metadata.get("spellbook_id")
        if not isinstance(spellbook_id, str) or not spellbook_id:
            spellbook_id = identity.owner_id
        return {
            "initiator_conduit_id": str(
                metadata.get("owner_conduit_id", identity.owner_id)
            ),
            "spellbook_id": spellbook_id,
            "conduit_ids": tuple(),
            "scope_keys": (lineage_scope,),
            "scope_claims": ((lineage_scope, ClaimMode.EXCLUSIVE.value),),
            "scope_hashes": tuple(metadata.get("scope_hashes", ())),
            "binding_keys": tuple(),
            "contract_keys": tuple(),
            "granted_capabilities": ("remediation",),
            "required_capabilities": ("remediation",),
            "metadata": normalized_metadata,
        }
