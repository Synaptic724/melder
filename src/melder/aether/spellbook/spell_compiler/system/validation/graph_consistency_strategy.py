from typing import Dict, List, Mapping, Optional, Set, Tuple

from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
@mypyc_attr(native_class=True)
class GraphConsistencyStrategy(SpellSystemValidationStrategy):
    """
    Guard that rooted blueprint DAGs and the frame-level index describe the
    same dependency edges.

    Phase 5 produces two related structural views:

    - rooted DAG blueprints used by later planning
    - `SpellSystemIndex` nodes used by system validation/change control

    This strategy checks them in both directions so we catch drift where a
    blueprint references an edge the index does not know about, or the index
    records an edge that never appears in any rooted blueprint.
    """
    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, IRootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: ISpellSystemStates,
            spell_lookup: Mapping[str, ISpell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Validate DAG edges across blueprints against SpellSystemIndex.

        Purpose:
            Ensure root DAG edges and index dependencies remain consistent in
            both directions.
        Contract:
            - Missing index nodes referenced by blueprints produce errors.
            - Blueprint edges missing from the index produce errors.
            - Index edges missing from all blueprints produce errors.
            - Cancellation is honored during traversal.
        Args:
            index: Spell system index being validated.
            blueprints: Root blueprints keyed by root spell id.
            phase4_results: Phase-4 validation artifacts keyed by spell id.
            broken_spell_ids: Set of broken spell ids.
            spell_system_states: SpellSystemStates registry for topology and lineage data.
            spell_lookup: Mapping of visible spell version ids to spell objects.
            diagnostics: Collection that receives diagnostics.
            cancel_event: Optional cancellation signal.
        Returns:
            None.
        Raises:
            OperationCancelledError:
                If cancel_event is set while iterating.
        """
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

