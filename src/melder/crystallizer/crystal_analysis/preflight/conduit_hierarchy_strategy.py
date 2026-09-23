from typing import Dict, List

from melder.crystallizer.crystal_analysis.conduit_hierarchy import ConduitHierarchy
from melder.crystallizer.crystal_analysis.preflight.persistence_analysis_strategy import PersistenceAnalysisStrategy


class ConduitHierarchyStrategy(PersistenceAnalysisStrategy):
    """Refuse malformed named-scope topology before restore builds runtime objects.

    Contract:
        Stateless and read-only. Root-only legacy bundles keep their existing
        analysis behavior; child-bearing bundles must carry a coherent shared
        Book/root/parent hierarchy, including necessary unnamed support values.
        Errors use the normal blocker finding shape and existing admission gate.

    Lifecycle / Registration:
        Owned as a stateless default strategy by PersistenceAnalyzer; no resources.
        Internal Crystallizer machinery, never an application binding.
    """

    @property
    def name(self) -> str:
        """Return the stable report key for this structural admission pass."""
        return "conduit_hierarchy"

    def analyze(self, payload_bundle: Dict[str, Dict[str, Dict[str, object]]]) -> List[Dict[str, object]]:
        """Report invalid child topology without mutating the recorded bundle.

        Args:
            payload_bundle: Folded or formation payloads by kind and identity.
        Returns:
            List[Dict[str, object]]: One actionable blocker, or an empty list.
        """
        conduits = payload_bundle.get("conduit", {})
        try:
            if all(ConduitHierarchy.role(payload) == "normal" for payload in conduits.values()):
                return []
            ConduitHierarchy.build(conduits, payload_bundle.get("spellbook", {}))
        except ValueError as error:
            return [{
                "strategy": self.name, "severity": "blocker", "kind": "conduit", "key": "hierarchy",
                "detail": str(error),
            }]
        return []
