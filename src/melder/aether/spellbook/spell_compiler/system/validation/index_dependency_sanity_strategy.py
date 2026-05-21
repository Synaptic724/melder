from typing import Dict, List, Mapping, Optional, Set

from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispell import ISpell
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent

@mypyc_attr(native_class=True)
class IndexDependencySanityStrategy(SpellSystemValidationStrategy):
    """
    Guard that every dependency edge recorded in `SpellSystemIndex` points to a
    real node.

    This is the index-local counterpart to the broader graph consistency check.
    Before later strategies reason about reachability, lineage, or root
    viability, the index itself must at least be internally self-consistent.

    Contract:
        - Emits `missing_index_dependency` when a node depends on a missing id.
        - Leaves diagnostics unchanged when all indexed dependencies are
          resolvable.
    """
    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, IRootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: SpellSystemStates,
            spell_lookup: Mapping[str, ISpell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Validate that all index dependencies resolve to known nodes.

        Purpose:
            Catch SpellSystemIndex entries that reference unknown dependencies.
        Contract:
            - Each missing dependency generates a missing_index_dependency`` diagnostic.
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
        known_ids = index.nodes.keys()
        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            for dep_id in node.dependencies:
                if dep_id in known_ids:
                    continue
                diagnostics.append(
                    SystemDiagnostic(
                        code="missing_index_dependency",
                        message=(
                            f"SpellSystemIndex node '{node.spell_id}' depends on missing spell '{dep_id}'."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=node.spell_id,
                        root_id=None,
                        details={
                            "spell_id": node.spell_id,
                            "dependency_id": dep_id,
                        },
                    )
                )

