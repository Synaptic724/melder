
from typing import ClassVar, Dict, List

from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import (
    PersistenceAnalysisStrategy,
)


class ContractPeerStrategy(PersistenceAnalysisStrategy):
    """
    Detect contracts whose endpoints are not both in the bundle.

    Purpose:
        A contract needs both conduit endpoints rebuilt before its
        details re-grant; a formation captured around ONE side carries
        the contract as a recorded reference the restore will shortfall
        (endpoint_not_rebuilt). Surface that before bootload.

    Contract:
        - Severity "warning": restore completes; the contract's details
          shortfall until the peer exists.

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
        This row is the RELATIONSHIP half of bundle-completeness, paired
        with `LinkIntegrityStrategy` (conduit link edges) and
        `ClusterMembershipStrategy` (cluster members). It reads the
        `ContractCrystal` endpoints the record emits at link and
        re-snapshots through the eight public contract verbs.

    System Context:
        A contract is a TWO-SIDED runtime relationship: ConduitWard
        re-grants its per-side detail projections only once both conduit
        endpoints are live. A formation captured around one side is
        therefore not corrupt - it is partial - so this row warns rather
        than blocks, and the restore reports an `endpoint_not_rebuilt`
        shortfall instead of refusing. Severity is a load-control
        decision made at the `RestoreEngine` fold->preflight seam:
        blockers refuse before any replay, warnings proceed and ride the
        report.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Detect contracts whose endpoints are not both in the bundle. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )


    @property
    def name(self) -> str:
        """
        Return the strategy's stable report name.

        Returns:
            str: "contract_peer".
        """
        return "contract_peer"

    def analyze(
            self,
            payload_bundle: Dict[str, Dict[str, Dict[str, object]]],
    ) -> List[Dict[str, object]]:
        """
        Flag every contract with a missing endpoint conduit.

        Args:
            payload_bundle:
                {kind: {key: payload}} bundle under analysis.

        Returns:
            List[Dict[str, object]]: One warning row per absent side.
        """
        conduits = dict(payload_bundle.get("conduit", {}))
        findings: List[Dict[str, object]] = []
        for contract_id, payload in dict(
                payload_bundle.get("contract", {})
        ).items():
            for side_field in ("conduit_a_id", "conduit_b_id"):
                side_id = str(payload.get(side_field))
                if side_id in conduits:
                    continue
                findings.append({
                    "strategy": self.name,
                    "severity": "warning",
                    "kind": "contract",
                    "key": contract_id,
                    "detail": (
                        "{0} {1!r} is not in this bundle; the restore "
                        "will shortfall this contract's details".format(
                            side_field, side_id
                        )
                    ),
                })
        return findings
