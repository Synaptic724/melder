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

class BrokenSpellInDagStrategy(SpellSystemValidationStrategy):
    """
    Flags any root blueprint that contains a spell broken at Phase 4.
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
        if not broken_spell_ids:
            return

        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            dag = blueprint.dag
            for node_id in dag.nodes.keys():
                if node_id in broken_spell_ids:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="broken_spell_in_dag",
                            message=(
                                f"Broken spell '{node_id}' is reachable in root DAG '{root_id}'."
                            ),
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=node_id,
                            root_id=root_id,
                        )
                    )
