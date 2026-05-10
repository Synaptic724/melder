from typing import Dict, List, Mapping, Optional, Set

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


class RootViabilityStrategy(SpellSystemValidationStrategy):
    """
    Collapse existing root-affecting errors into one root-viability verdict.

    This strategy does not perform fresh structural analysis. Instead, it asks
    a simpler system-level question after earlier strategies have already run:
    "Given the errors already attached to this root's DAG, is this root viable
    for downstream planning?" If the answer is no, it emits a single root-level
    error that higher layers can use as a coarse viability signal.
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
        Emit a root-level viability error when any system error affects the DAG.

        Purpose:
            Collapse existing system-level errors into a single "root not viable"
            diagnostic for any root that already has error diagnostics.
        Contract:
            - Only roots with existing ERROR diagnostics receive a new error.
            - This strategy does not introduce new root analysis; it aggregates
              existing error diagnostics for clarity.
            - Emits at most one new viability diagnostic per root during a run.
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
                If cancel_event is set while iterating.
        """
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
