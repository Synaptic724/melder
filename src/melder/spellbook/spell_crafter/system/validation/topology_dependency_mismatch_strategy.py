from typing import Dict, List, Mapping, Optional, Set

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
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


class TopologyDependencyMismatchStrategy(SpellSystemValidationStrategy):
    """
    Detect mismatches between local topologies and index dependencies.

    Purpose:
        Ensure Phase 3 local topology sockets remain consistent with the
        dependency edges recorded in SpellSystemIndex.
    Contract:
        - Compares NORMAL socket targets to index dependency ids.
        - Emits errors when topology targets and index dependencies disagree.
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
        Validate topology socket targets against index dependencies.

        Purpose:
            Detect drift between socket targets and dependency edges.
        Contract:
            - Only NORMAL sockets contribute to dependency comparisons.
            - Emits an error when topology and index disagree.
            - Cancellation is honored between nodes.
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
        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            topology = spell_system_states.get_local_topology_by_id(node.spell_id)
            if topology is None:
                continue

            topology_deps: Set[str] = set()
            for socket in topology.iter_sockets():
                if socket.socket_kind is not SocketKind.NORMAL:
                    continue
                topology_deps.update(socket.target_spell_ids)

            index_deps = set(node.dependencies)
            missing_in_index = topology_deps.difference(index_deps)
            extra_in_index = index_deps.difference(topology_deps)

            if not missing_in_index and not extra_in_index:
                continue

            diagnostics.append(
                SystemDiagnostic(
                    code="topology_dependency_mismatch",
                    message=(
                        f"Spell '{node.spell_id}' has dependency mismatches between "
                        "local topology sockets and SpellSystemIndex."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=node.spell_id,
                    root_id=None,
                    details={
                        "spell_id": node.spell_id,
                        "missing_in_index": sorted(missing_in_index),
                        "extra_in_index": sorted(extra_in_index),
                        "topology_dependencies": sorted(topology_deps),
                        "index_dependencies": sorted(index_deps),
                    },
                )
            )
