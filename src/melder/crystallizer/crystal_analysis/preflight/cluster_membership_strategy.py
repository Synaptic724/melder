
from typing import ClassVar, Dict, List

from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class ClusterMembershipStrategy(PersistenceAnalysisStrategy):
    """
    Detect cluster members missing from the bundle.

    Purpose:
        A cluster rebuilds by re-adding its recorded members; members
        OUTSIDE the bundle cannot re-join and shortfall at restore.
        Leadership is a runtime election and is reported as context.

    Contract:
        - Severity "warning" per absent member conduit.
        - Severity "info" once per cluster with a recorded leader (the
          election re-runs live; the recorded leader is not replayed).

    Threading:
        Stateless - no instance state and no locks. One analyzer pass
        calls `analyze` once and the strategy retains nothing between
        calls, so a single instance is safe to reuse across bundles.

    Registration:
        MELDER KERNEL - guarded. Preflight strategies are constructed by
        `PersistenceAnalyzer`, never bound as spells.

    Subsystem Context:
        One of the ten DEFAULT rows of the preflight set that
        `PersistenceAnalyzer` iterates polymorphically, emitting the
        shared finding shape {strategy, severity, kind, key, detail}.
        This row is the CLUSTER half of bundle-completeness, alongside
        `LinkIntegrityStrategy` (link edges) and `ContractPeerStrategy`
        (contract endpoints). It reads the `ClusterCrystal` twin, which
        the cluster's own state mutators emit through the
        configuration-precedent singleton pull because clusters have no
        crystallizer-bearing parent to push for them.

    System Context:
        This strategy encodes the distinction between RECORDED STATE and
        RUNTIME ELECTION. Membership is recorded state and replays: a
        rebuilt cluster re-adds its recorded members, so an absent member
        is a real shortfall and warns. Leadership is NOT replayed - the
        election re-runs live against whoever actually came up - so the
        recorded leader is reported as "info" context rather than treated
        as a value to restore. Reporting it as a shortfall would tell the
        user something was lost when nothing was; staying silent would
        hide why the live leader may differ from the sealed one.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Detect cluster members missing from the bundle. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )


    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "cluster_membership".
        """
        return "cluster_membership"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Flag absent cluster members and note recorded leaders.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: Warning/info rows per cluster.
        """
        conduits = dict(payload_bundle.get("conduit", {}))
        findings: List[Dict[str, object]] = []
        for cluster_id, payload in dict(
                payload_bundle.get("cluster", {})
        ).items():
            for member_id in list(payload.get("member_conduit_ids", [])):
                if str(member_id) in conduits:
                    continue
                findings.append({
                    "strategy": self.name,
                    "severity": "warning",
                    "kind": "cluster",
                    "key": cluster_id,
                    "detail": (
                        "member conduit {0!r} is not in this bundle; "
                        "it cannot re-join the rebuilt cluster".format(
                            str(member_id)
                        )
                    ),
                })
            if payload.get("leader_conduit_id") is not None:
                findings.append({
                    "strategy": self.name,
                    "severity": "info",
                    "kind": "cluster",
                    "key": cluster_id,
                    "detail": (
                        "leadership is a runtime election; the recorded "
                        "leader is context, not a replayed act"
                    ),
                })
        return findings
