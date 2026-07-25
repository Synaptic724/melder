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


class LineageAlignmentStrategy(SpellSystemValidationStrategy):
    """
    Guard that root-blueprint lineage metadata agrees with the system index.

    Root blueprints are version-id rooted, but they can still carry lineage
    metadata for DevOps and change-control consumers. This strategy checks that
    the optional root-lineage ids embedded in the blueprints stay aligned with
    the lineage ids tracked on the corresponding `SpellSystemIndex` nodes.

    Contract:
        - Emits `root_lineage_mismatch` when a root lineage id disagrees with
          the index.
        - Skips checks when a blueprint intentionally lacks lineage metadata.
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
        Validate that blueprint root lineage ids match index lineage ids.

        Purpose:
            Ensure the Phase-5 blueprint lineage metadata stays aligned with
            the SpellSystemIndex lineage ids used for system tracking.
        Contract:
            - Emits root_lineage_mismatch when the lineage ids differ.
            - Omits diagnostics when root lineage metadata is absent.
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
        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            root_lineage_id = blueprint.root_lineage_id
            if root_lineage_id is None:
                continue

            node = index.get_node(root_id)
            if node is None:
                continue

            if node.lineage_id == root_lineage_id:
                continue

            diagnostics.append(
                SystemDiagnostic(
                    code="root_lineage_mismatch",
                    message=(
                        f"Root '{root_id}' lineage '{root_lineage_id}' does not match "
                        f"SpellSystemIndex lineage '{node.lineage_id}'."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=root_id,
                    root_id=root_id,
                    details={
                        "root_lineage_id": root_lineage_id,
                        "index_lineage_id": node.lineage_id,
                    },
                )
            )



