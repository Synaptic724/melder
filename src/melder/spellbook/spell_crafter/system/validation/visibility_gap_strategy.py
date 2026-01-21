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
from melder.utilities.interfaces.interfaces import ISpell, ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class VisibilityGapStrategy(SpellSystemValidationStrategy):
    """
    Detect dependencies filtered out by spellbook visibility.

    Purpose:
        Surface cases where a visible spell depends on spell ids that are not
        present in the current SpellSystemIndex because they are not visible
        to the spellbook (e.g., missing contracted dependencies).
    Contract:
        - Compares SpellSystemStates direct dependencies against index edges.
        - Emits one diagnostic per spell with missing dependencies.
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
        Validate that visible spells retain all direct dependencies.

        Purpose:
            Identify missing dependencies that were filtered out due to
            spell visibility constraints.
        Contract:
            - Uses SpellSystemStates as the source of truth for direct deps.
            - Emits errors when dependencies are missing from the index.
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

            state = spell_system_states.get_by_spell_id(node.spell_id)
            if state is None or state.direct_dependencies is None:
                continue

            state_deps = set(state.direct_dependencies)
            index_deps = set(node.dependencies)
            missing = state_deps.difference(index_deps)

            if not missing:
                continue

            diagnostics.append(
                SystemDiagnostic(
                    code="visibility_gap_dependency_filtered",
                    message=(
                        f"Spell '{node.spell_id}' depends on missing spell ids "
                        f"{sorted(missing)}, which are not visible in the current spellbook."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=node.spell_id,
                    root_id=None,
                    details={
                        "spell_id": node.spell_id,
                        "missing_dependency_ids": sorted(missing),
                        "state_dependencies": sorted(state_deps),
                        "index_dependencies": sorted(index_deps),
                    },
                )
            )
