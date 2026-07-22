from typing import Any, Dict, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_existence_occurrence_analysis import (
    SpellExistenceOccurrenceAnalysis,
)
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

    Registration:
        MELDER KERNEL - currently UNGUARDED. A compiler analysis artifact held on
        `SpellCompilerArtifact`; not a bind target. (Left untagged as-is; guard
        classification is the owner's call.)

    Subsystem Context:
        The occurrence-analysis output of the `spell_analyzer` package, produced by
        the occurrence-graph analyzer strategy; it borrows a `path_registry` it must
        not clean.

    System Context:
        Phase 8 (occurrence analysis) of the conjure pipeline. Stores the expanded
        occurrence graph plus cheap metrics - not execution ordering or plan choices.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-8 occurrence-graph artifact: owns the expanded occurrence_graph "
        "and cheap metrics (occurrence/edge/dependency counts, shared_collapse flag) plus the "
        "existence analysis. Borrows path_registry (does not clean it)."
    )

    __slots__ = Cleanable.__slots__ + [
        "root_spell_id",
        "occurrence_graph",
        "path_registry",
        "occurrence_count",
        "edge_count",
        "topology_dependency_count",
        "dag_fallback_dependency_count",
        "shared_collapse_enabled",
        "existence_occurrence_analysis",
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
            shared_collapse_enabled: bool,
            existence_occurrence_analysis: Optional[SpellExistenceOccurrenceAnalysis] = None,
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
        self.shared_collapse_enabled = shared_collapse_enabled
        self.existence_occurrence_analysis = existence_occurrence_analysis

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
        del self.shared_collapse_enabled
        del self.existence_occurrence_analysis
