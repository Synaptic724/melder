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
from melder.utilities.interfaces.interfaces import ISpell, ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class RootLineageConflictStrategy(SpellSystemValidationStrategy):
    """
    Internal

    Purpose:
        Detect multiple root spell ids mapped to the same lineage.
    Contract:
        - Emits ``root_lineage_conflict`` when a lineage produces multiple roots.
        - Skips roots missing from the index or without lineage metadata.
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
        Validate that each lineage maps to at most one root spell id.

        Purpose:
            Prevent multiple root spell versions for the same lineage across
            the blueprint set.
        Contract:
            - Each lineage with multiple roots yields diagnostics.
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
        lineage_to_roots: Dict[str, List[str]] = {}
        for root_id in blueprints.keys():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            node = index.get_node(root_id)
            if node is None or node.lineage_id is None:
                continue
            lineage_to_roots.setdefault(node.lineage_id, []).append(root_id)

        for lineage_id, root_ids in lineage_to_roots.items():
            if len(root_ids) <= 1:
                continue
            for root_id in root_ids:
                diagnostics.append(
                    SystemDiagnostic(
                        code="root_lineage_conflict",
                        message=(
                            f"Lineage '{lineage_id}' maps to multiple root spell ids: {root_ids}."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=root_id,
                        root_id=root_id,
                        details={
                            "lineage_id": lineage_id,
                            "root_ids": list(root_ids),
                        },
                    )
                )
