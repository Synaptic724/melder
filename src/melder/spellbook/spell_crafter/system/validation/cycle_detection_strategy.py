from __future__ import annotations

from typing import Dict, List, Optional, Set

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class CycleDetectionStrategy(SpellSystemValidationStrategy):
    """
    Detect cycles in the system dependency graph using SpellSystemIndex edges.
    """

    __slots__ = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Dict[str, object],
            broken_spell_ids: Set[str],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        if index is None:
            raise ValueError("index must not be None.")

        nodes = index.nodes
        indegree: Dict[str, int] = {}
        children_by_parent: Dict[str, Set[str]] = {}

        # Build indegree (count of parents) and adjacency (parent -> children).
        for child_id, node in nodes.items():
            deps = node.dependencies
            indegree.setdefault(child_id, 0)
            for parent_id in deps:
                children_by_parent.setdefault(parent_id, set()).add(child_id)
                indegree[child_id] = indegree.get(child_id, 0) + 1
                indegree.setdefault(parent_id, 0)

        # Kahn's algorithm for cycle detection.
        queue: List[str] = [n for n, deg in indegree.items() if deg == 0]
        idx = 0
        visited = 0

        while idx < len(queue):
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            current = queue[idx]
            idx += 1
            visited += 1

            for child in children_by_parent.get(current, ()):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

        if visited != len(indegree):
            diagnostics.append(
                SystemDiagnostic(
                    code="cycle_detected",
                    message="Cycle detected in system dependency graph.",
                    severity=SystemDiagnosticSeverity.ERROR,
                )
            )
