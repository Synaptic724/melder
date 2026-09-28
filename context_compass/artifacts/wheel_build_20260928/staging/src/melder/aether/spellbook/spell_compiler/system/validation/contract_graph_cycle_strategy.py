from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Set, Tuple

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.system.spell_system_index import (
        SpellSystemIndex,
    )
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )
            


from melder.aether.spellbook.spell_compiler.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.helpers.general_helpers import SpellInputUtils


class ContractGraphCycleStrategy(SpellSystemValidationStrategy):
    """
    Guard that contract-only edges do not introduce cycles outside the normal DAG.

    The rooted system graph is primarily built from NORMAL dependency edges, but
    SpellContract sockets can add an extra contract graph
    on top of that structure. This strategy builds that contract-only view and
    checks whether it introduces loops that are invisible to the ordinary DAG
    cycle checks.
    """
    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: SpellSystemStates,
            spell_lookup: Mapping[str, Spell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Validate that contract edges do not introduce cycles.

        Purpose:
            Detect cycles in the contract resolution graph for visible spells.
        Contract:
            - Uses contract sockets from local topologies.
            - Uses visible spells to resolve contract keys to providers.
            - Emits at least one diagnostic per detected cycle.
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
        provider_map: Dict[Tuple[str, str], Set[str]] = {}
        for spell_id, spell in spell_lookup.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            key = SpellInputUtils.make_spell_key_from_parts(
                spellframe=spell.spellframe,
                spell_name=spell.spell_name,
                binding_name=spell.binding_name,
            )
            provider_map.setdefault(key, set()).add(spell_id)

        contract_graph: Dict[str, Set[str]] = {}
        edge_contract_keys: Dict[Tuple[str, str], Set[Tuple[str, str]]] = {}

        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            topology = spell_system_states.get_local_topology_by_id(node.spell_id)
            if topology is None:
                continue

            for socket in topology.iter_sockets():
                if socket.socket_kind is not SocketKind.SPELL_CONTRACT:
                    continue
                if socket.contract_key is None:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="contract_key_missing",
                            message=(
                                f"Spell '{node.spell_id}' has a contract socket '{socket.param_name}' "
                                "without a canonical contract key."
                            ),
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=node.spell_id,
                            root_id=None,
                            details={
                                "spell_id": node.spell_id,
                                "param_name": socket.param_name,
                                "socket_kind": socket.socket_kind.name,
                            },
                        )
                    )
                    continue

                providers = provider_map.get(socket.contract_key, set())
                if not providers:
                    continue

                for provider_id in providers:
                    contract_graph.setdefault(node.spell_id, set()).add(provider_id)
                    edge_contract_keys.setdefault(
                        (node.spell_id, provider_id), set()
                    ).add(socket.contract_key)

        cycles = self._detect_cycles(contract_graph, cancel_event)
        for cycle in cycles:
            edge_keys: Dict[str, List[Tuple[str, str]]] = {}
            for idx in range(len(cycle) - 1):
                edge = (cycle[idx], cycle[idx + 1])
                keys = edge_contract_keys.get(edge, set())
                edge_keys[f"{cycle[idx]}->{cycle[idx + 1]}"] = sorted(keys)

            diagnostics.append(
                SystemDiagnostic(
                    code="contract_cycle_detected",
                    message=(
                        "Contract resolution cycle detected: "
                        f"{' -> '.join(cycle)}."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=cycle[0] if cycle else None,
                    root_id=None,
                    details={
                        "cycle_spell_ids": cycle,
                        "edge_contract_keys": edge_keys,
                    },
                )
            )

    def _detect_cycles(
        self,
        graph: Dict[str, Set[str]],
        cancel_event: Optional[CancellationEvent],
    ) -> List[List[str]]:
        """
        Find cycles in the provided adjacency graph.

        Purpose:
            Collect all unique cycles in the contract dependency graph.
        Contract:
            - Returns an empty list when no cycles are present.
            - Normalizes cycles to avoid duplicate reporting.
        Args:
            graph: Adjacency mapping of spell ids.
            cancel_event: Optional cancellation signal.
        Returns:
            list[list[str]]: Detected cycles.
        """
        visited: Set[str] = set()
        stack: List[str] = []
        stack_index: Dict[str, int] = {}
        cycles: List[List[str]] = []
        seen_cycles: Set[Tuple[str, ...]] = set()

        def _walk(node_id: str) -> None:
            """
            Depth-first walk over the contract graph for cycle discovery.

            Contract:
                - Honors cancellation before descending.
                - Records normalized cycles once even if discovered from
                  multiple traversal entrypoints.
            """
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if node_id in stack_index:
                start = stack_index[node_id]
                cycle = stack[start:] + [node_id]
                normalized = self._normalize_cycle(cycle)
                if normalized not in seen_cycles:
                    seen_cycles.add(normalized)
                    cycles.append(list(normalized))
                return

            if node_id in visited:
                return

            visited.add(node_id)
            stack_index[node_id] = len(stack)
            stack.append(node_id)

            for neighbor in graph.get(node_id, ()):
                _walk(neighbor)

            stack.pop()
            stack_index.pop(node_id, None)

        for node_id in list(graph.keys()):
            _walk(node_id)

        return cycles

    def _normalize_cycle(self, cycle: List[str]) -> Tuple[str, ...]:
        """
        Normalize a cycle representation for stable comparison.

        Purpose:
            Ensure cycles are reported once, regardless of traversal order.
        Contract:
            - Returns a tuple starting from the lexicographically smallest node.
            - Preserves the closing node for explicit cycle representation.
        Args:
            cycle: Cycle list including the repeated start/end node.
        Returns:
            Tuple[str, ...]: Normalized cycle tuple.
        """
        if len(cycle) < 2:
            return tuple(cycle)

        trimmed = cycle[:-1]
        min_index = 0
        for idx in range(1, len(trimmed)):
            if trimmed[idx] < trimmed[min_index]:
                min_index = idx
        rotated = trimmed[min_index:] + trimmed[:min_index]
        rotated.append(rotated[0])
        return tuple(rotated)




