from typing import Any, Dict, List, Optional, Protocol, Set, Tuple, runtime_checkable
from melder.aether.spellbook.spell_crafter.dag.dag_index import PathRegistry
from melder.utilities.interfaces.icleanable import ICleanable

OccurrenceKey = Tuple[str, int]
InstanceKey = Tuple[str, Optional[int]]

@runtime_checkable
class IOccurrencePlan(ICleanable, Protocol):
    """
    Phase-8 occurrence plan contract consumed by `SpellCrafter`.
    """

    @property
    def root_spell_id(self) -> str:
        ...

    @property
    def occurrence_graph(self) -> Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]]:
        ...

    @property
    def execution_order(self) -> List[str]:
        ...

    @property
    def instance_keys_by_spell_id(self) -> Dict[str, List[InstanceKey]]:
        ...

    @property
    def canonical_occurrences_by_spell_id(self) -> Dict[str, OccurrenceKey]:
        ...

    @property
    def root_instance_key(self) -> InstanceKey:
        ...

    @property
    def shared_spell_ids(self) -> Set[str]:
        ...

    @property
    def contract_overrides_by_occurrence(self) -> Dict[OccurrenceKey, Dict[str, Any]]:
        ...

    @property
    def contract_overrides_by_spell_id(
            self,
    ) -> Dict[str, List[Tuple[OccurrenceKey, Dict[str, Any]]]]:
        ...

    @property
    def contract_dependencies_complete(self) -> bool:
        ...

    @property
    def path_registry(self) -> PathRegistry:
        ...
