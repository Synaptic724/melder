
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.crystallizer.persistence.analysis.persistence_analysis_strategy import (
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
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

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
