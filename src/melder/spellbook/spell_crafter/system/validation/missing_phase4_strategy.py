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


class MissingPhase4Strategy(SpellSystemValidationStrategy):
    """
    Flags any spell in a root DAG that lacks Phase-4 validation results.
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
        missing_ids: Set[str] = set()

        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            dag = blueprint.dag
            for node_id in dag.nodes.keys():
                if node_id not in phase4_results:
                    missing_ids.add(node_id)
                    diagnostics.append(
                        SystemDiagnostic(
                            code="missing_phase4_validation",
                            message=(
                                f"Spell '{node_id}' in root '{root_id}' has no Phase-4 validation result."
                            ),
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=node_id,
                            root_id=root_id,
                        )
                    )
