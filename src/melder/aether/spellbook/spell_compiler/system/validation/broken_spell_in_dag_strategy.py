from typing import TYPE_CHECKING, Dict, List, Mapping, Optional, Set

if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell import Spell

from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
@mypyc_attr(native_class=True)
class BrokenSpellInDagStrategy(SpellSystemValidationStrategy):
    """
    Guard that broken Phase 4 spells do not silently survive into root DAGs.

    This strategy lifts spell-local breakage into the rooted system view. If a
    spell is already known to be broken at Phase 4, every root blueprint that
    still reaches that spell should carry a system-level error so downstream
    planning and viability checks do not treat the root as structurally usable.
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
        Emit diagnostics when broken spells appear in root DAGs.

        Purpose:
            Surface Phase 4 broken spell ids that are still reachable in
            system-level root blueprints.
        Contract:
            - If no broken spell ids are provided, emits nothing.
            - Each broken node reachable from a root yields one diagnostic.
            - A single broken spell may contribute diagnostics to multiple
              roots when its lineage is shared across those rooted DAGs.
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
        if not broken_spell_ids:
            return

        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            dag = blueprint.dag
            for node_id in dag.nodes.keys():
                if node_id in broken_spell_ids:
                    diagnostics.append(
                        SystemDiagnostic(
                            code="broken_spell_in_dag",
                            message=(
                                f"Broken spell '{node_id}' is reachable in root DAG '{root_id}'."
                            ),
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=node_id,
                            root_id=root_id,
                        )
                    )


