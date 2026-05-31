from typing import Any, Dict, List, Tuple

from melder.utilities.general_base.cleanable import Cleanable

OccurrenceKey = Tuple[str, int]


class SpellOccurrenceGraphAnalysis(Cleanable):
    """
    Occurrence-graph analysis artifact.

    Purpose:
        Hold the expanded runtime occurrence graph and the cheap graph-level
        metrics gathered while deriving it.

    Contract:
        - Owns the occurrence graph mapping.
        - Borrows `path_registry`; it must not clean it.
        - Stores only occurrence-graph analysis, not execution ordering or
          final plan decisions.
    """

    __slots__ = Cleanable.__slots__ + [
        "root_spell_id",
        "occurrence_graph",
        "path_registry",
        "occurrence_count",
        "edge_count",
        "topology_dependency_count",
        "dag_fallback_dependency_count",
        "mutation_override_dependency_count",
        "shared_collapse_enabled",
    ]

    def __init__(
            self,
            *,
            root_spell_id: str,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            path_registry: Any,
            occurrence_count: int,
            edge_count: int,
            topology_dependency_count: int,
            dag_fallback_dependency_count: int,
            mutation_override_dependency_count: int,
            shared_collapse_enabled: bool,
    ) -> None:
        """
        Build one occurrence-graph analysis artifact.
        """
        super().__init__()
        self.root_spell_id = root_spell_id
        self.occurrence_graph = occurrence_graph
        self.path_registry = path_registry
        self.occurrence_count = occurrence_count
        self.edge_count = edge_count
        self.topology_dependency_count = topology_dependency_count
        self.dag_fallback_dependency_count = dag_fallback_dependency_count
        self.mutation_override_dependency_count = mutation_override_dependency_count
        self.shared_collapse_enabled = shared_collapse_enabled

    def cleanup(self) -> None:
        """
        Deterministically release owned graph-analysis data.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.occurrence_graph.clear()
        del self.root_spell_id
        del self.occurrence_graph
        del self.path_registry
        del self.occurrence_count
        del self.edge_count
        del self.topology_dependency_count
        del self.dag_fallback_dependency_count
        del self.mutation_override_dependency_count
        del self.shared_collapse_enabled
