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
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


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
        - Analysis only: the strategy records value facts on the supplied
          result and neither imports modules nor participates in restore.

    Threading:
        Stateless strategy object. The supplied result remains owned by the
        analyzer thread while `finalize()` writes the order.

    Lifecycle / Cleanup:
        Holds no resources or references between calls; inherited cleanup is a
        no-op beyond the strategy lifecycle contract.

    Registration:
        MELDER KERNEL - guarded. A per-analysis fact strategy in the analyzer's
        set; never user-constructed or bound.

    Subsystem Context:
        A concrete `CrystalFactStrategy` in the `crystal_analysis` fact family.
        Unlike the per-node strategies, it runs in `finalize` (post-walk) because
        it needs the COMPLETE direct-dependency edge map: it derives the
        topological, dependencies-before-dependents unfold order over the walked
        modules and records it as `module_load_order` on the
        `CrystalAnalysisResult`.

    System Context:
        Recording the unfold order at ANALYSIS time is the S1 capability that
        replaced the restore engine's dot-depth heuristics with crystal-side
        TRUTH: the loader no longer guesses activation order at restore, it reads
        an order the analyzer already proved. The cycle-tolerant contract keeps
        that honest under real code - when a dependency cycle blocks a clean
        topological sort, the remaining nodes are appended deterministically and a
        walk error names them, so the order stays usable AND the honesty ledger
        records that the graph had a cycle rather than silently papering over it.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Derive the topological unfold order over walked modules. Melder kernel "
        "machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
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

        Contract:
            Reads a detached dependency map from the result, runs Kahn's
            algorithm over edges whose endpoints were both walked, and writes
            exactly one ordered list back. Dependencies outside the walked
            module set remain manifest facts but do not become ordering nodes.
            A cycle never raises: unresolved nodes are appended
            deterministically and reported through the result's honesty lane.

        Args:
            result:
                Analysis result carrying the completed dependency edges.

        Returns:
            None.

        Raises:
            RuntimeError: If the supplied result has been cleaned.

        Threading:
            Must run during the analyzer's single-writer finalize phase.
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
