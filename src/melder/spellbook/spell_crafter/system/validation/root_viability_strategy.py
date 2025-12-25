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


class RootViabilityStrategy(SpellSystemValidationStrategy):
    """
    Emits a root-scoped ERROR diagnostic if any existing ERROR affects that root's DAG.
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
        # Pre-group diagnostics by root_id for existing errors.
        errors_by_root: Dict[str, int] = {}
        for diag in diagnostics:
            if diag.severity is not SystemDiagnosticSeverity.ERROR:
                continue
            root_id = diag.root_id
            if root_id is not None:
                errors_by_root[root_id] = errors_by_root.get(root_id, 0) + 1

        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if root_id in errors_by_root:
                diagnostics.append(
                    SystemDiagnostic(
                        code="root_not_viable",
                        message=(
                            f"Root '{root_id}' is not viable due to existing system-level errors."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=None,
                        root_id=root_id,
                    )
                )
