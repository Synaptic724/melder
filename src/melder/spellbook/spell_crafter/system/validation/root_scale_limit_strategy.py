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
from melder.utilities.interfaces import ISpell, ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class RootScaleLimitStrategy(SpellSystemValidationStrategy):
    """
    Guard root DAG size against configured operational scale limits.

    This strategy is not about correctness of edge structure; it is an
    operational pressure gauge. It warns when a root blueprint becomes large,
    deep, or wide enough that later planning, execution, or debugging is likely
    to become problematic even if the graph is otherwise structurally valid.
    """
    __slots__ = [
        "_max_nodes",
        "_max_edges",
        "_max_depth",
        "_max_fan_out",
        "_severity",
    ]

    def __init__(
            self,
            *,
            max_nodes: int = 2000,
            max_edges: int = 10000,
            max_depth: int = 50,
            max_fan_out: int = 100,
            severity: SystemDiagnosticSeverity = SystemDiagnosticSeverity.WARNING,
    ) -> None:
        """
        Initialize scale thresholds for root DAG diagnostics.

        Purpose:
            Configure warning thresholds for DAG size and shape.
        Contract:
            - Any limit <= 0 disables that specific check.
            - Severity defaults to WARNING so scale issues do not gate validity.
        Args:
            max_nodes: Maximum allowed DAG node count before warning.
            max_edges: Maximum allowed DAG edge count before warning.
            max_depth: Maximum allowed dependency depth before warning.
            max_fan_out: Maximum allowed out-degree before warning.
            severity: Diagnostic severity to emit for breaches.
        """
        self._max_nodes = max_nodes
        self._max_edges = max_edges
        self._max_depth = max_depth
        self._max_fan_out = max_fan_out
        self._severity = severity

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
        Validate root DAG scale against configured thresholds.

        Purpose:
            Emit warnings when a root DAG is unusually large or deep.
        Contract:
            - Emits one diagnostic per breached threshold.
            - Depth checks are skipped if the root is missing or ordering fails.
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
            node_count = len(dag.nodes)

            edge_count = 0
            max_fan_out = 0
            for node in dag.nodes.values():
                edge_count += len(node.dependencies)
                fan_out = len(node.dependents)
                if fan_out > max_fan_out:
                    max_fan_out = fan_out

            if self._max_nodes is not None and self._max_nodes > 0:
                if node_count > self._max_nodes:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="root_dag_node_limit_exceeded",
                            message=(
                                f"Root '{root_id}' has {node_count} nodes "
                                f"exceeding limit {self._max_nodes}."
                            ),
                            severity=self._severity,
                            spell_id=root_id,
                            root_id=root_id,
                            details={
                                "node_count": node_count,
                                "limit": self._max_nodes,
                            },
                        )
                    )

            if self._max_edges is not None and self._max_edges > 0:
                if edge_count > self._max_edges:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="root_dag_edge_limit_exceeded",
                            message=(
                                f"Root '{root_id}' has {edge_count} edges "
                                f"exceeding limit {self._max_edges}."
                            ),
                            severity=self._severity,
                            spell_id=root_id,
                            root_id=root_id,
                            details={
                                "edge_count": edge_count,
                                "limit": self._max_edges,
                            },
                        )
                    )

            if self._max_fan_out is not None and self._max_fan_out > 0:
                if max_fan_out > self._max_fan_out:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="root_dag_fan_out_limit_exceeded",
                            message=(
                                f"Root '{root_id}' has fan-out {max_fan_out} "
                                f"exceeding limit {self._max_fan_out}."
                            ),
                            severity=self._severity,
                            spell_id=root_id,
                            root_id=root_id,
                            details={
                                "fan_out": max_fan_out,
                                "limit": self._max_fan_out,
                            },
                        )
                    )

            if self._max_depth is None or self._max_depth <= 0:
                continue

            root_node = dag.get_node(root_id)
            if root_node is None:
                continue

            try:
                ordered_node_ids = dag.collect_dependency_ids()
            except RuntimeError:
                continue

            depth_map: Dict[str, int] = {}
            for node_id in ordered_node_ids:
                node = dag.get_node(node_id)
                if node is None:
                    continue
                if not node.dependencies:
                    depth_map[node_id] = 0
                    continue
                max_parent_depth = 0
                for parent in node.dependencies:
                    parent_depth = depth_map.get(parent.id, 0)
                    if parent_depth > max_parent_depth:
                        max_parent_depth = parent_depth
                depth_map[node_id] = max_parent_depth + 1

            root_depth = depth_map.get(root_id, 0)
            if root_depth > self._max_depth:
                diagnostics.append(
                    SystemDiagnostic(
                        code="root_dag_depth_limit_exceeded",
                        message=(
                            f"Root '{root_id}' has dependency depth {root_depth} "
                            f"exceeding limit {self._max_depth}."
                        ),
                        severity=self._severity,
                        spell_id=root_id,
                        root_id=root_id,
                        details={
                            "depth": root_depth,
                            "limit": self._max_depth,
                        },
                    )
                )
