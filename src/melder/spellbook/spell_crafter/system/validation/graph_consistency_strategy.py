from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

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


class GraphConsistencyStrategy(SpellSystemValidationStrategy):
    """
    Ensures blueprint DAG edges align with SpellSystemIndex dependencies.
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
        nodes = index.nodes
        # Collect all edges present in blueprint DAGs for reverse consistency checks.
        dag_edges: Set[Tuple[str, str]] = set()
        for blueprint in blueprints.values():
            dag = blueprint.dag
            for child_node in dag.nodes.values():
                child_id = child_node.id
                for parent_node in child_node.dependencies:
                    dag_edges.add((parent_node.id, child_id))

        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            dag = blueprint.dag
            for child_node in dag.nodes.values():
                child_id = child_node.id

                if child_id not in nodes:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="missing_index_node",
                            message=(
                                f"Blueprint DAG for root '{root_id}' references node '{child_id}' "
                                f"not present in SpellSystemIndex."
                            ),
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=child_id,
                            root_id=root_id,
                        )
                    )
                    continue

                child_index_node = nodes[child_id]
                expected_parents = child_index_node.dependencies

                for parent_node in child_node.dependencies:
                    parent_id = parent_node.id

                    if parent_id not in nodes:
                        diagnostics.append(
                            SystemDiagnostic(
                                code="missing_index_node",
                                message=(
                                    f"Blueprint DAG for root '{root_id}' references parent '{parent_id}' "
                                    f"not present in SpellSystemIndex."
                                ),
                                severity=SystemDiagnosticSeverity.ERROR,
                                spell_id=parent_id,
                                root_id=root_id,
                            )
                        )
                        continue

                    if parent_id not in expected_parents:
                        diagnostics.append(
                            SystemDiagnostic(
                                code="edge_mismatch_index",
                                message=(
                                    f"Edge {parent_id} -> {child_id} present in blueprint for root '{root_id}' "
                                    f"but missing from SpellSystemIndex dependencies."
                                ),
                                severity=SystemDiagnosticSeverity.ERROR,
                                spell_id=child_id,
                                root_id=root_id,
                                details={
                                    "parent_id": parent_id,
                                    "child_id": child_id,
                                    "root_id": root_id,
                                },
                            )
                        )

        # Check for edges present in the index but missing from all blueprints.
        for child_id, node in nodes.items():
            expected_parents = node.dependencies
            for parent_id in expected_parents:
                edge = (parent_id, child_id)
                if edge in dag_edges:
                    continue
                diagnostics.append(
                    SystemDiagnostic(
                        code="edge_missing_from_blueprint",
                        message=(
                            f"Edge {parent_id} -> {child_id} present in SpellSystemIndex "
                            f"but missing from all root blueprints."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=child_id,
                        root_id=None,
                        details={
                            "parent_id": parent_id,
                            "child_id": child_id,
                        },
                    )
                )
