from typing import Dict, List, Mapping, Optional, Set
# Melder imports
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
from melder.utilities.interfaces.interfaces import ISpell, ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent

class CycleDetectionStrategy(SpellSystemValidationStrategy):
    """
    Detect cycles in the system dependency graph described by SpellSystemIndex.

    Purpose:
        Identify whether any dependency cycle exists and emit a single
        "cycle_detected" diagnostic when one is found.

    Contract:
        - Does not mutate the index or its nodes.
        - Appends at most one diagnostic for any cycle presence.
        - Honors cancel_event by delegating to cancel_event.throw_if_set()
          during traversal.

    Threading:
        Stateless; safe for concurrent use when inputs are not shared.

    Lifecycle:
        No owned resources; no cleanup required.
    """
    __slots__ = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Dict[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: ISpellSystemStates,
            spell_lookup: Mapping[str, ISpell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Detect dependency cycles across SpellSystemIndex nodes.

        Purpose:
            Run a Kahn-style topological traversal to determine whether the
            dependency graph is acyclic.

        Contract:
            - Appends a single "cycle_detected" error diagnostic if any cycle exists.
            - Leaves diagnostics unchanged when no cycle is present.
            - Does not mutate the index or nodes.
            - Checks cancel_event during traversal and propagates its exception.

        Args:
            index: Spell system index to scan; must not be None.
            blueprints: Phase-5 blueprints (unused by this strategy).
            phase4_results: Phase-4 results (unused by this strategy).
            broken_spell_ids: Broken spell ids (unused by this strategy).
            spell_system_states: SpellSystemStates registry (unused by this strategy).
            spell_lookup: Mapping of visible spell version ids (unused by this strategy).
            diagnostics: Mutable list that receives diagnostics.
            cancel_event: Optional cancellation signal.

        Returns:
            None.

        Raises:
            ValueError: If index is None.
            Exception: Propagates any exception raised by cancel_event.throw_if_set()
                when cancellation is signaled.

        Threading:
            Stateless; callers must synchronize shared inputs (e.g., diagnostics).

        Lifecycle:
            No owned resources; no cleanup required.
        """
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
            if cancel_event is not None:
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
