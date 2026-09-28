from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Set, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_order_analysis import (
    SpellOccurrenceOrderAnalysis,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


OccurrenceKey = Tuple[str, int]


class SpellOccurrenceOrderProcessorStrategy(SpellArtifactProcessorStrategy):
    """
    Fit the occurrence-order section of `SpellCodegenModel`.

    Purpose:
        Consume analyzer-owned occurrence graph truth and materialize the
        deterministic spell execution order that later planner work can use
        without reopening graph traversal logic.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable processor strategy id.
        """
        return "spell_occurrence_order_processor"

    def process(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            model: SpellCodegenModel,
    ) -> None:
        """
        Fit the occurrence-order model section.

        Contract:
            - Reads only analyzer-owned graph truth from the model shell.
            - Writes only `model.order_shape` plus compatible top-level
              `node_count`.
            - Does not write back onto `SpellCompilerArtifact`.
        """
        _ = spell
        _ = artifact
        graph_shape = model.graph_shape
        if graph_shape is None:
            raise RuntimeError(
                "SpellOccurrenceOrderProcessorStrategy requires graph_shape first."
            )

        order_shape = SpellOccurrenceOrderAnalysis(
            execution_order=self._build_execution_order(
                occurrence_graph=graph_shape.occurrence_graph,
                fallback_occurrences=tuple(graph_shape.occurrence_graph.keys()),
            )
        )
        previous_order_shape = model.order_shape
        model.order_shape = order_shape
        model.node_count = order_shape.execution_order_count
        self._cleanup_previous(previous_order_shape, order_shape)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceOrderAnalysis],
            current: SpellOccurrenceOrderAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded order section.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

    @staticmethod
    def _occurrence_sort_key(
            occurrence: OccurrenceKey,
    ) -> Tuple[str, int]:
        """
        Build a deterministic ordering key for occurrence tuples.
        """
        if occurrence[1] is None:
            return occurrence[0], -1
        return occurrence[0], occurrence[1]

    @staticmethod
    def _build_execution_order(
            *,
            occurrence_graph: Dict[OccurrenceKey, Dict[str, List[OccurrenceKey]]],
            fallback_occurrences: Sequence[OccurrenceKey],
    ) -> List[str]:
        """
        Build a dependency-safe execution order for spell ids.

        Contract:
            - Uses the occurrence graph as the primary dependency source.
            - Uses spell-id lexical ordering as the stable topological
              tie-breaker.
            - Falls back to the first-seen occurrence order when the graph is
              cyclic or incomplete.
        """
        edges: Dict[str, Set[str]] = {}
        indegree: Dict[str, int] = {}
        nodes: Set[str] = set()

        for occurrence in sorted(
                occurrence_graph.keys(),
                key=SpellOccurrenceOrderProcessorStrategy._occurrence_sort_key,
        ):
            node_id = occurrence[0]
            nodes.add(node_id)
            for dependency_name in sorted(occurrence_graph[occurrence].keys()):
                for dependency_occurrence in occurrence_graph[occurrence][dependency_name]:
                    dependency_id = dependency_occurrence[0]
                    nodes.add(dependency_id)
                    dependency_children = edges.setdefault(dependency_id, set())
                    if node_id not in dependency_children:
                        dependency_children.add(node_id)
                        indegree[node_id] = indegree.get(node_id, 0) + 1

        for node_id in sorted(nodes):
            indegree.setdefault(node_id, 0)

        queue = [
            node_id
            for node_id, degree in indegree.items()
            if degree == 0
        ]
        import heapq
        heapq.heapify(queue)
        order: List[str] = []

        while queue:
            node_id = heapq.heappop(queue)
            order.append(node_id)
            for child_id in sorted(edges.get(node_id, ())):
                indegree[child_id] -= 1
                if indegree[child_id] == 0:
                    heapq.heappush(queue, child_id)

        if len(order) == len(nodes):
            return order

        resolved: List[str] = []
        seen: Set[str] = set()
        for occurrence in fallback_occurrences:
            node_id = occurrence[0]
            if node_id in nodes and node_id not in seen:
                seen.add(node_id)
                resolved.append(node_id)
        for node_id in sorted(nodes):
            if node_id not in seen:
                seen.add(node_id)
                resolved.append(node_id)
        return resolved
