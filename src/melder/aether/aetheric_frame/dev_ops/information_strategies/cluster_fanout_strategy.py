from typing import TYPE_CHECKING, Dict, List, Set

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


class ClusterFanoutStrategy(DevopsInformationStrategy):
    """
    Registry-backed cluster fan-out view for one conduit or one cluster.

    Purpose:
        Answer "if this participant changes, which cluster members feel it"
        from the mirrored cluster membership maps.

    Why this exists:
        Cluster operations admit under shared or exclusive claims depending
        on how far the change reaches. Before claiming, a caller wants the
        membership picture: which clusters a conduit sits in and every
        sibling conduit reachable through them, or one cluster's full member
        roster. This strategy is that read, with freshness for each touched
        conduit region.

    Contract:
        - Metadata requires exactly one of `conduit_id` or `cluster_id`.
        - Sibling computation for a conduit unions the members of every
          cluster the conduit belongs to, excluding the conduit itself.
        - Returns ids only; honors optional `max_age_in_seconds`.

    Threading:
        Stateless static strategy; reads mirrored cluster membership only.

    Registration:
        MELDER KERNEL - guarded. Registered as a CLASS in the information
        family; resolved by name through `DevopsInformationStrategyBuilder`.

    Subsystem Context:
        The membership read behind cluster operations, feeding the same
        decisions `ClusterJoinTransactionStrategy` and
        `ClusterLeaveTransactionStrategy` must plan for.

    System Context:
        Cluster changes are N-way rather than pairwise: a join fans shares out
        to every existing member, and a leave tears them down across the whole
        membership. So the claim footprint is the entire involved set, and a
        caller that has not seen the roster cannot anticipate how wide its
        transaction will reach.
        Unioning the members of every cluster a conduit belongs to - excluding
        the conduit itself - answers the question that actually matters before
        claiming: not "which clusters am I in" but "who feels it if I change".
        Requiring exactly one of `conduit_id` or `cluster_id` keeps the two
        directions of that question distinct rather than silently merging a
        participant-centric and a cluster-centric answer.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Registry-backed cluster fan-out view for one conduit or one cluster. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    @staticmethod
    def execute(
            *,
            devops_information_registry: "DevopsInformationRegistry",
            metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Build one detached cluster fan-out view.

        Args:
            devops_information_registry:
                Live mirrored DevOps registry to consume.
            metadata:
                - "conduit_id": fan out from one conduit across its clusters.
                - "cluster_id": fan out across one cluster's members.
                - optional "max_age_in_seconds" staleness tolerance.

        Returns:
            Dict[str, object]: For a conduit: {"strategy", "conduit_id",
            "cluster_ids", "sibling_conduit_ids", "fanout_size", "freshness"}.
            For a cluster: {"strategy", "cluster_id", "member_conduit_ids",
            "fanout_size", "freshness"}.

        Raises:
            ValueError: If neither or both of `conduit_id`/`cluster_id` are
                supplied, or the supplied value is empty.
        """
        conduit_id = metadata.get("conduit_id")
        cluster_id = metadata.get("cluster_id")
        max_age = InformationFreshnessInspector.read_optional_max_age(metadata)
        if (conduit_id is None) == (cluster_id is None):
            raise ValueError(
                "cluster_fanout requires exactly one of conduit_id or "
                "cluster_id."
            )

        if conduit_id is not None:
            if not conduit_id:
                raise ValueError("conduit_id must not be empty.")
            target_conduit_id = str(conduit_id)
            cluster_ids = devops_information_registry.get_clusters_for_conduit(
                target_conduit_id
            )
            siblings: Set[str] = set()
            for member_cluster_id in cluster_ids:
                siblings.update(
                    devops_information_registry.get_conduits_for_cluster(
                        member_cluster_id
                    )
                )
            siblings.discard(target_conduit_id)
            regions: List[str] = [f"conduit:{target_conduit_id}"]
            regions.extend(f"conduit:{sibling}" for sibling in siblings)
            return {
                "strategy": "cluster_fanout",
                "conduit_id": target_conduit_id,
                "cluster_ids": tuple(sorted(cluster_ids)),
                "sibling_conduit_ids": tuple(sorted(siblings)),
                "fanout_size": len(siblings),
                "freshness": (
                    InformationFreshnessInspector.build_freshness_view(
                        devops_information_registry=(
                            devops_information_registry
                        ),
                        regions=regions,
                        max_age_in_seconds=max_age,
                    )
                ),
            }

        if not cluster_id:
            raise ValueError("cluster_id must not be empty.")
        target_cluster_id = str(cluster_id)
        member_conduit_ids = devops_information_registry.get_conduits_for_cluster(
            target_cluster_id
        )
        return {
            "strategy": "cluster_fanout",
            "cluster_id": target_cluster_id,
            "member_conduit_ids": tuple(sorted(member_conduit_ids)),
            "fanout_size": len(member_conduit_ids),
            "freshness": InformationFreshnessInspector.build_freshness_view(
                devops_information_registry=devops_information_registry,
                regions=[
                    f"conduit:{member}" for member in member_conduit_ids
                ],
                max_age_in_seconds=max_age,
            ),
        }
