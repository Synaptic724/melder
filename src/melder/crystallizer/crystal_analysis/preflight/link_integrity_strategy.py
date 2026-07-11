
from typing import ClassVar, Dict, List

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
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
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel

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
