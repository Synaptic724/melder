from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Set, Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_order_analysis import (
    SpellOccurrenceOrderAnalysis,
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
    Build processor-owned occurrence execution order from graph truth.

    Purpose:
        Consume the analyzer-owned occurrence graph and produce the
        deterministic execution-order artifact that later processor/model
        stages can consume without touching analyzer internals.
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
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            model: "SpellCodegenModel",
    ) -> None:
        """
        Build and publish the occurrence-order artifact on the compiler
        artifact.
        """
        _ = spell
        graph_analysis = artifact._occurrence_graph_analysis
        if graph_analysis is None:
            raise RuntimeError(
                "SpellOccurrenceOrderProcessorStrategy requires occurrence graph analysis first."
            )
        root_blueprint = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellOccurrenceOrderProcessorStrategy requires Phase 5 root blueprint truth."
            )

        order_analysis = SpellOccurrenceOrderAnalysis(
            execution_order=self._build_execution_order(
                occurrence_graph=graph_analysis.occurrence_graph,
                fallback_order=root_blueprint.ordered_node_ids,
            )
        )
        previous_order = model.occurrence_order_analysis
        model.occurrence_order_analysis = order_analysis
        self._cleanup_previous(previous_order, order_analysis)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceOrderAnalysis],
            current: SpellOccurrenceOrderAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded occurrence-order artifact.
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
            fallback_order: Sequence[str],
    ) -> List[str]:
        """
        Build a dependency-safe execution order for spell ids.
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
        for node_id in fallback_order:
            if node_id in nodes and node_id not in seen:
                seen.add(node_id)
                resolved.append(node_id)
        for node_id in sorted(nodes):
            if node_id not in seen:
                seen.add(node_id)
                resolved.append(node_id)
        return resolved
