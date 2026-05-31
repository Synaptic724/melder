from typing import Any, Dict, List, Tuple

from melder.utilities.general_base.cleanable import Cleanable

OccurrenceKey = Tuple[str, int]


class SpellOccurrenceContractAnalysis(Cleanable):
    """
    Processor-owned occurrence contract-routing artifact.

    Purpose:
        Hold SpellContract-derived payload routing and completeness truth
        derived from analyzer-owned occurrence graph data.
    """

    __slots__ = Cleanable.__slots__ + [
        "contract_overrides_by_occurrence",
        "contract_overrides_by_spell_id",
        "contract_dependencies_complete",
        "contract_override_occurrence_count",
        "contract_override_spell_count",
        "contract_payload_count",
    ]

    def __init__(
            self,
            *,
            contract_overrides_by_occurrence: Dict[OccurrenceKey, Dict[str, Any]],
            contract_overrides_by_spell_id: Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]],
            contract_dependencies_complete: bool,
    ) -> None:
        """
        Build one occurrence-contract artifact.
        """
        super().__init__()
        self.contract_overrides_by_occurrence = contract_overrides_by_occurrence
        self.contract_overrides_by_spell_id = contract_overrides_by_spell_id
        self.contract_dependencies_complete = contract_dependencies_complete
        self.contract_override_occurrence_count = len(contract_overrides_by_occurrence)
        self.contract_override_spell_count = len(contract_overrides_by_spell_id)
        self.contract_payload_count = sum(
            len(payload)
            for payload in contract_overrides_by_occurrence.values()
        )

    def cleanup(self) -> None:
        """
        Deterministically release owned contract-analysis data.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.contract_overrides_by_occurrence.clear()
        self.contract_overrides_by_spell_id.clear()
        del self.contract_overrides_by_occurrence
        del self.contract_overrides_by_spell_id
        del self.contract_dependencies_complete
        del self.contract_override_occurrence_count
        del self.contract_override_spell_count
        del self.contract_payload_count
