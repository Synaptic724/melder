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


class OwnershipConsistencyStrategy(SpellSystemValidationStrategy):
    """
    Internal

    Purpose:
        Ensure a lineage is not associated with conflicting conduit ownership.
    Contract:
        - Emits ``lineage_conduit_conflict`` when a lineage maps to multiple
          non-None conduit ids.
        - Ignores None conduit ids (treated as unknown).
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
        Validate ownership consistency across index nodes.

        Purpose:
            Catch lineages that appear to be owned by multiple conduits.
        Contract:
            - Uses lineage_id as the grouping key.
            - Only non-None conduit ids are considered for conflicts.
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
        lineage_to_conduits: Dict[str, Set[str]] = {}
        lineage_to_spells: Dict[str, Set[str]] = {}

        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            lineage_id = node.lineage_id
            if lineage_id is None:
                continue
            lineage_to_spells.setdefault(lineage_id, set()).add(node.spell_id)

            conduit_id = node.conduit_id
            if conduit_id is None:
                continue
            lineage_to_conduits.setdefault(lineage_id, set()).add(conduit_id)

        for lineage_id, conduit_ids in lineage_to_conduits.items():
            if len(conduit_ids) <= 1:
                continue
            diagnostics.append(
                SystemDiagnostic(
                    code="lineage_conduit_conflict",
                    message=(
                        f"Lineage '{lineage_id}' maps to multiple conduits: {sorted(conduit_ids)}."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=None,
                    root_id=None,
                    details={
                        "lineage_id": lineage_id,
                        "conduit_ids": sorted(conduit_ids),
                        "spell_ids": sorted(lineage_to_spells.get(lineage_id, set())),
                    },
                )
            )
