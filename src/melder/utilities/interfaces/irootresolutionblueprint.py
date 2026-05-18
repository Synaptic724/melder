from typing import List, Optional, Protocol, runtime_checkable
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, PathRegistry, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IRootResolutionBlueprint(ICleanable, Protocol):
    """
    Phase-5 rooted blueprint contract consumed by `SpellCrafter`.
    """

    @property
    def root_spell_id(self) -> str:
        ...

    @property
    def root_lineage_id(self) -> Optional[str]:
        ...

    @property
    def dag(self) -> DirectedAcyclicWorkGraph:
        ...

    @property
    def ordered_node_ids(self) -> List[str]:
        ...

    @property
    def socket_refs(self) -> List[SocketRef]:
        ...

    @property
    def dag_index(self) -> DagIndex:
        ...

    @property
    def path_registry(self) -> PathRegistry:
        ...
