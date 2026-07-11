"""
Fact strategy for the topological module load order (S1 NEW capability).

Computes an explicit dependencies-first unfold order over the walked module
graph, replacing the restore engine's dot-depth heuristics with crystal-side
truth (gap map 1.2 / philosophy V2 duty #2). Runs in `finalize` because it
needs the complete edge map.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

from typing import Dict, List, Set

from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.strategies.base_strategy import (
    CrystalFactStrategy,
)


class DependencyViewStrategy(CrystalFactStrategy):
    """
    Derive the topological unfold order over walked modules.

    Purpose:
        Give loaders an explicit dependencies-before-dependents module
        order computed at analysis time, so unfold ordering is recorded
        truth instead of restore-time guessing.

    Contract:
        - Nodes: every walked module (keys of the direct-dependency map).
        - Edges: dependency -> dependent, restricted to walked modules
          (external leaves order themselves by absence).
        - Deterministic: ready nodes are processed in sorted name order.
        - Cycle-tolerant: when a cycle blocks completion, the remaining
          nodes are appended in sorted order and one walk error names
          them - the order stays usable, the honesty ledger stays honest.
    """

    __slots__ = ()

    @property
    def name(self) -> str:
        """
        Return the stable strategy name.

        Returns:
            str: `dependency_view`.
        """
        return "dependency_view"

    def finalize(self, result: CrystalAnalysisResult) -> None:
        """
        Compute and record the topological load order.

        Args:
            result:
                Analysis result carrying the completed dependency edges.

        Returns:
            None.
        """
        dependency_edges: Dict[str, List[str]] = (
            result.module_to_direct_dependencies
        )
        walked_modules: Set[str] = set(dependency_edges.keys())

        # Kahn's algorithm over walked-module edges, sorted tie-breaking.
        remaining_dependency_counts: Dict[str, int] = {}
        dependents_by_module: Dict[str, List[str]] = {}
        for module_name, dependency_names in dependency_edges.items():
            walked_dependencies = [
                dependency_name
                for dependency_name in dependency_names
                if dependency_name in walked_modules
                and dependency_name != module_name
            ]
            remaining_dependency_counts[module_name] = len(
                set(walked_dependencies)
            )
            for dependency_name in set(walked_dependencies):
                dependents_by_module.setdefault(dependency_name, []).append(
                    module_name
                )

        ready_modules: List[str] = sorted(
            module_name
            for module_name, count in remaining_dependency_counts.items()
            if count == 0
        )
        load_order: List[str] = []
        while ready_modules:
            current_module = ready_modules.pop(0)
            load_order.append(current_module)
            for dependent_name in sorted(
                    dependents_by_module.get(current_module, [])
            ):
                remaining_dependency_counts[dependent_name] -= 1
                if remaining_dependency_counts[dependent_name] == 0:
                    # Insert preserving sorted readiness order.
                    ready_modules.append(dependent_name)
                    ready_modules.sort()

        unresolved_modules = sorted(
            module_name
            for module_name, count in remaining_dependency_counts.items()
            if count > 0
        )
        if unresolved_modules:
            load_order.extend(unresolved_modules)
            result.record_walk_error(
                "dependency_view: import cycle prevented a full topological "
                "order; appended in name order: {0}".format(
                    ", ".join(unresolved_modules)
                )
            )

        result.set_module_load_order(load_order)
