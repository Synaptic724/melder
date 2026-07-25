
from typing import ClassVar, Dict, List

from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class LinkIntegrityStrategy(PersistenceAnalysisStrategy):
    """
    Detect conduit link targets missing from the bundle.

    Purpose:
        The owner's founding case for the analyzer: "missing linking".
        A conduit whose recorded link_targets reference conduits OUTSIDE
        the bundle will restore, but those links shortfall - the user
        should know before they trust the formation.

    Contract:
        - Severity "warning": the restore completes; the link is
          reported, not rebuilt.

    Threading:
        Stateless - no instance state and no locks. One analyzer pass
        calls `analyze` once and the strategy retains nothing between
        calls, so a single instance is safe to reuse across bundles.

    Registration:
        MELDER KERNEL - guarded. Preflight strategies are constructed by
        `PersistenceAnalyzer`, never bound as spells.

    Subsystem Context:
        One of the ten DEFAULT rows of the preflight set that
        `PersistenceAnalyzer` iterates polymorphically over a detached
        payload bundle. It emits the shared finding shape every strategy
        in this package returns: {strategy, severity, kind, key, detail}.
        This row is the CONDUIT-EDGE half of bundle-completeness; its
        siblings cover the other edges - `ContractPeerStrategy` (contract
        endpoints) and `ClusterMembershipStrategy` (cluster members).

    System Context:
        Severity here is a LOAD-CONTROL DECISION, not a label. Every
        mediated load runs plan -> map -> verdict -> execute -> remember,
        and the verdict gate sits inside `RestoreEngine` at the
        fold->preflight seam - the only place holding authoritative
        FOLDED truth. Rows marked "blocker" refuse the load with a
        teach-grade error BEFORE any replay; "warning" rows like this one
        proceed and ride the report. That is why a dangling link is a
        warning: the conduit still rebuilds, only the edge shortfalls,
        so refusing the whole world would cost the user more than the
        missing link does.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Detect conduit link targets missing from the bundle. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )


    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "link_integrity".
        """
        return "link_integrity"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Flag every link_target that resolves to no bundled conduit.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: One warning row per dangling edge.
        """
        conduits = dict(payload_bundle.get("conduit", {}))
        findings: List[Dict[str, object]] = []
        for conduit_id, payload in conduits.items():
            for target_id in list(payload.get("link_targets", [])):
                if str(target_id) in conduits:
                    continue
                findings.append({
                    "strategy": self.name,
                    "severity": "warning",
                    "kind": "conduit",
                    "key": conduit_id,
                    "detail": (
                        "link_target {0!r} is not in this bundle; the "
                        "restore will shortfall this link".format(
                            str(target_id)
                        )
                    ),
                })
        return findings
