from typing import Dict, List, Mapping, Optional, Set

from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent

@mypyc_attr(native_class=True)
class RootLineageConflictStrategy(SpellSystemValidationStrategy):
    """
    Guard that one lineage does not fan out into multiple structural roots.

    A root blueprint is supposed to represent a distinct root spell version in
    the frame. If multiple root spell ids map back to the same lineage, the
    system is effectively declaring multiple root revisions of one logical spell
    family at once. This strategy detects that root-lineage split before the
    planner treats those roots as separate entrypoints with independent
    occurrence, validation, or execution semantics.
    """
    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, IRootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: ISpellSystemStates,
            spell_lookup: Mapping[str, ISpell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Validate that each lineage maps to at most one root spell id.

        Purpose:
            Prevent the blueprint set from advertising multiple structural roots
            for one logical spell lineage.
        Contract:
            - Uses blueprint keys as the root set and resolves lineage identity
              from the system index.
            - Missing index nodes and lineage-less roots are ignored here so
              dedicated index/root coverage strategies can report those failures
              without duplicate noise.
            - Emits one ERROR diagnostic per conflicting root so every root id
              participating in the split is directly visible to operators.
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

