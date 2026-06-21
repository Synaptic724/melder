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
            


from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


class IdentityMixingStrategy(SpellSystemValidationStrategy):
    """
    Guard that dependency edges stay on version ids rather than lineage ids.

    The system graph is supposed to route concrete spell versions, while
    lineage ids are DevOps/control-plane identity. If a dependency edge starts
    pointing at lineage ids directly, later planning and resolution become
    ambiguous because the graph is no longer naming executable versions. This
    strategy catches that identity-layer mixing.
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
        Validate that dependency ids are version ids, not lineage ids.

        Purpose:
            Catch dependency edges that reference lineage ids directly, which
            can cause resolution to drift or fail.
        Contract:
            - Emits an error for each dependency id that matches a lineage id.
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
                If cancel_event is set while iterating.
        """
        lineage_ids: Set[str] = {
            node.lineage_id for node in index.nodes.values() if node.lineage_id is not None
        }
        spell_ids: Set[str] = set(index.nodes.keys())

        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            for dep_id in node.dependencies:
                if dep_id in spell_ids:
                    continue
                if dep_id not in lineage_ids:
                    continue

                diagnostics.append(
                    SystemDiagnostic(
                        code="identity_mixing_detected",
                        message=(
                            f"Spell '{node.spell_id}' depends on lineage id '{dep_id}' "
                            "instead of a version id."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=node.spell_id,
                        root_id=None,
                        details={
                            "spell_id": node.spell_id,
                            "dependency_id": dep_id,
                            "known_lineage_ids": sorted(lineage_ids),
                        },
                    )
                )



