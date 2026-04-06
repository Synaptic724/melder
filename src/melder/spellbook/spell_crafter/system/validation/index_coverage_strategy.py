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


class IndexCoverageStrategy(SpellSystemValidationStrategy):
    """
    Guard that the Phase 5 index and rooted blueprints describe the same node set.

    `SpellSystemIndex` is the frame-level catalog of nodes the system believes
    exist, while the root-blueprint set is the rooted structural view the later
    planning and validation phases actually walk. This strategy checks for
    drift between those two products by ensuring every indexed node appears in
    at least one rooted blueprint.
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
        Validate that index nodes are covered by root blueprints.

        Purpose:
            Catch spells that are present in the system index but never appear
            in any root DAG.
        Contract:
            - Each uncovered node yields a diagnostic.
            - Coverage is based on blueprint DAG membership, not just root ids.
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
        covered_ids: Set[str] = set()
        for blueprint in blueprints.values():
            covered_ids.update(blueprint.dag.nodes.keys())

        for spell_id in index.nodes.keys():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            if spell_id in covered_ids:
                continue
            diagnostics.append(
                SystemDiagnostic(
                    code="index_node_missing_from_blueprints",
                    message=(
                        f"SpellSystemIndex node '{spell_id}' is not present in any root blueprint."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=spell_id,
                    root_id=None,
                )
            )
