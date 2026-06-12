from typing import TYPE_CHECKING, Dict

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


class FrameOperationalViewStrategy(DevopsInformationStrategy):
    """
    Frame-wide operational rollup of the mirrored DevOps state.

    Purpose:
        Give one detached "what does this frame look like right now" answer:
        population by identity kind, ownership/link/cluster shape, live
        transaction pressure by type, and how much of the frame carries fact
        baselines at all.

    Why this exists:
        Deep views are one of the few justified strategy runs in the
        control-plane economy. Operators and agents joining a frame need the
        whole-station picture once, then live off commit deltas; this
        strategy is that single-shot deep view.

    Contract:
        - No required metadata; optional `max_age_in_seconds` turns the
          baseline-coverage section into a staleness verdict over every
          region that has ever been reported.
        - Counts and ids only; never returns live object references.
    """

    @staticmethod
    def execute(
            *,
            devops_information_registry: "DevopsInformationRegistry",
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build one detached frame-wide operational view.

        Args:
            devops_information_registry:
                Live mirrored DevOps registry to consume.
            metadata:
                Optional "max_age_in_seconds" staleness tolerance.

        Returns:
            Dict[str, object]: {"strategy", "aetheric_frame_name",
            "identity_count", "identity_counts_by_kind", "spellbook_count",
            "owned_conduit_count", "link_edge_count", "cluster_count",
            "live_transaction_count", "transaction_counts_by_type",
            "fact_record_count", "fact_record_counts_by_family",
            "freshness"}.
        """
        max_age = InformationFreshnessInspector.read_optional_max_age(metadata)
        described = devops_information_registry.describe()
        maps = devops_information_registry.snapshot_relationship_maps()

        identity_counts_by_kind = {
            kind: len(keys)
            for kind, keys in described["identity_keys_by_kind"].items()
        }
        owned_conduit_count = sum(
            len(conduits)
            for conduits in maps["spellbook_to_conduits"].values()
        )
        link_edge_count = sum(
            len(borrowers)
            for borrowers in maps["provider_to_borrowers"].values()
        )
        transaction_counts_by_type = {
            transaction_type: len(transaction_ids)
            for transaction_type, transaction_ids in maps[
                "transaction_ids_by_type"
            ].items()
        }

        fact_records = devops_information_registry.list_fact_records()
        fact_record_counts_by_family: Dict[str, int] = {}
        for record in fact_records:
            fact_record_counts_by_family[record.fact_family] = (
                fact_record_counts_by_family.get(record.fact_family, 0) + 1
            )
        reported_regions = {record.region for record in fact_records}

        return {
            "strategy": "frame_operational_view",
            "aetheric_frame_name": described["aetheric_frame_name"],
            "identity_count": described["identity_count"],
            "identity_counts_by_kind": identity_counts_by_kind,
            "spellbook_count": len(maps["spellbook_to_conduits"]),
            "owned_conduit_count": owned_conduit_count,
            "link_edge_count": link_edge_count,
            "cluster_count": len(maps["cluster_to_conduits"]),
            "live_transaction_count": described["transaction_count"],
            "transaction_counts_by_type": transaction_counts_by_type,
            "fact_record_count": len(fact_records),
            "fact_record_counts_by_family": fact_record_counts_by_family,
            "freshness": InformationFreshnessInspector.build_freshness_view(
                devops_information_registry=devops_information_registry,
                regions=reported_regions,
                max_age_in_seconds=max_age,
            ),
        }
