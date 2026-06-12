from typing import TYPE_CHECKING, Dict, List

from melder.aether.aetheric_frame.dev_ops.devops_information_strategy import (
    DevopsInformationStrategy,
)
from melder.aether.aetheric_frame.dev_ops.information_strategies.information_strategy_support import (
    InformationFreshnessInspector,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.devops_information_registry import (
        DevopsInformationRegistry,
    )


class TransferBlastRadiusStrategy(DevopsInformationStrategy):
    """
    Registry-backed impact set for transferring one conduit's ownership.

    Purpose:
        Enumerate everything a transfer-of-ownership touches before the
        transaction claims its scopes: the owning spellbook, sibling conduits
        under that owner, link partners in both directions, and cluster
        co-members.

    Why this exists:
        Transfer is the highest-leverage post-conjure transaction: it rewires
        who answers for a conduit while borrowers and clusters keep pointing
        at it. The transfer initiator should see the full relational blast
        radius — and how fresh the registry's picture of each affected region
        is — before deciding to proceed or to refresh first.

    Contract:
        - Metadata requires `conduit_id`.
        - All sets are mirrored-registry truth only; no live objects.
        - The freshness block covers the target conduit, the owning
          spellbook, and every related conduit in the radius.
        - Honors optional `max_age_in_seconds`.
    """

    @staticmethod
    def execute(
            *,
            devops_information_registry: "DevopsInformationRegistry",
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build one detached transfer blast-radius view.

        Args:
            devops_information_registry:
                Live mirrored DevOps registry to consume.
            metadata:
                - "conduit_id": conduit whose transfer is being considered.
                - optional "max_age_in_seconds" staleness tolerance.

        Returns:
            Dict[str, object]: {"strategy", "conduit_id",
            "owning_spellbook_id", "sibling_conduit_ids",
            "borrower_conduit_ids", "provider_conduit_ids", "cluster_ids",
            "blast_radius_size", "freshness"}.

        Raises:
            ValueError: If `conduit_id` is missing or empty.
        """
        conduit_id = metadata.get("conduit_id")
        if not conduit_id:
            raise ValueError("transfer_blast_radius requires conduit_id.")
        target_conduit_id = str(conduit_id)
        max_age = InformationFreshnessInspector.read_optional_max_age(metadata)

        owning_spellbook_id = (
            devops_information_registry.get_spellbook_for_conduit(
                target_conduit_id
            )
        )
        sibling_conduit_ids = tuple(
            sorted(
                conduit
                for conduit in (
                    devops_information_registry.get_conduits_for_spellbook(
                        owning_spellbook_id
                    )
                    if owning_spellbook_id is not None
                    else ()
                )
                if conduit != target_conduit_id
            )
        )
        borrower_conduit_ids = tuple(
            sorted(
                devops_information_registry.list_borrowers_for_provider(
                    target_conduit_id
                )
            )
        )
        provider_conduit_ids = tuple(
            sorted(
                devops_information_registry.list_providers_for_borrower(
                    target_conduit_id
                )
            )
        )
        cluster_ids = tuple(
            sorted(
                devops_information_registry.get_clusters_for_conduit(
                    target_conduit_id
                )
            )
        )

        related_conduits = set(sibling_conduit_ids)
        related_conduits.update(borrower_conduit_ids)
        related_conduits.update(provider_conduit_ids)
        related_conduits.discard(target_conduit_id)

        regions: List[str] = [f"conduit:{target_conduit_id}"]
        if owning_spellbook_id is not None:
            regions.append(f"spellbook:{owning_spellbook_id}")
        regions.extend(f"conduit:{related}" for related in related_conduits)

        return {
            "strategy": "transfer_blast_radius",
            "conduit_id": target_conduit_id,
            "owning_spellbook_id": owning_spellbook_id,
            "sibling_conduit_ids": sibling_conduit_ids,
            "borrower_conduit_ids": borrower_conduit_ids,
            "provider_conduit_ids": provider_conduit_ids,
            "cluster_ids": cluster_ids,
            "blast_radius_size": len(related_conduits)
            + len(cluster_ids)
            + (1 if owning_spellbook_id is not None else 0),
            "freshness": InformationFreshnessInspector.build_freshness_view(
                devops_information_registry=devops_information_registry,
                regions=regions,
                max_age_in_seconds=max_age,
            ),
        }
