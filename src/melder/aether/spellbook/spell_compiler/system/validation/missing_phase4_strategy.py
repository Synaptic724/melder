from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Set

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.system.spell_system_index import (
        SpellSystemIndex,
    )
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.utilities.synchronization.cancellation_event_signal import (
        CancellationEvent,
    )
            


# Melder imports
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


class MissingPhase4Strategy(SpellSystemValidationStrategy):
    """
    Guard that every spell appearing in a root DAG has a Phase 4 result.

    This strategy bridges the spell-local and system-level validation layers.
    By the time Phase 6 runs, every node reachable through a root blueprint is
    expected to have already completed spell-local validation. If a spell is in
    the rooted system graph but has no Phase 4 artifact, later system verdicts
    become untrustworthy because the system layer would be validating an
    incompletely checked spell set.
    """
    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: SpellSystemStates,
            spell_lookup: Mapping[str, Spell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Emit diagnostics for spells missing Phase 4 validation results.

        Purpose:
            Surface spells present in root DAGs that never completed the
            spell-local validation phase.
        Contract:
            - Each missing spell id yields an error diagnostic.
            - The same missing spell may be reported under multiple roots when
              it is reachable from multiple root DAGs.
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



