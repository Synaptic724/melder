from typing import Dict, List, Mapping, Optional, Set

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
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent

@mypyc_attr(native_class=True)
class RootReachabilityStrategy(SpellSystemValidationStrategy):
    """
    Guard that each root blueprint is a true root-reachable DAG.

    A root blueprint should contain exactly the dependency closure reachable
    from its declared root. If the root node is missing or the DAG still holds
    orphaned nodes that cannot be reached from that root, later occurrence and
    execution planning are reasoning over stale or structurally invalid graph
    state. This strategy catches that mismatch.
    """
    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, IRootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: SpellSystemStates,
            spell_lookup: Mapping[str, ISpell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Validate that every blueprint DAG node is reachable from its root.

        Purpose:
            Detect orphan nodes that are not reachable from the root spell.
        Contract:
            - Root-less DAGs raise a root_missing_in_dag diagnostic.
            - Orphan nodes produce ``dag_orphan_node`` diagnostics.
            - Cancellation is honored between roots.
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
                If ``cancel_event`` is set while iterating.
        """
        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            dag = blueprint.dag
            root_node = dag.get_node(root_id)
            if root_node is None:
                diagnostics.append(
                    SystemDiagnostic(
                        code="root_missing_in_dag",
                        message=(
                            f"Root '{root_id}' is not present in blueprint DAG."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=root_id,
                        root_id=root_id,
                        details={
                            "root_id": root_id,
                            "dag_node_count": len(dag.nodes),
                            "dag_nodes": sorted(dag.nodes.keys()),
                        },
                    )
                )
                continue

            reachable: Set[str] = set()
            stack = [root_node]
            while stack:
                node = stack.pop()
                node_id = node.id
                if node_id in reachable:
                    continue
                reachable.add(node_id)
                for dep in node.dependencies:
                    stack.append(dep)

            for node_id in dag.nodes.keys():
                if node_id in reachable:
                    continue
                diagnostics.append(
                    SystemDiagnostic(
                        code="dag_orphan_node",
                        message=(
                            f"Blueprint DAG for root '{root_id}' contains orphan node '{node_id}'."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=node_id,
                        root_id=root_id,
                        details={
                            "root_id": root_id,
                            "spell_id": node_id,
                            "reachable_node_count": len(reachable),
                            "reachable_nodes": sorted(reachable),
                        },
                    )
                )

