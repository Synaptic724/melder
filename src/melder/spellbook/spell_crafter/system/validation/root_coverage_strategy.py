from typing import Dict, List, Optional, Set
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
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class RootCoverageStrategy(SpellSystemValidationStrategy):
    """
    Internal

    Purpose:
        Ensure root blueprints and index root flags stay in sync.
    Contract:
        - Emits ``root_missing_in_index`` when a blueprint root is absent from the index.
        - Emits ``root_not_marked_in_index`` when the index node is not marked as root.
        - Emits ``missing_root_blueprint`` when the index marks a root without a blueprint.
    """
    __slots__ = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Dict[str, object],
            broken_spell_ids: Set[str],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Validate root coverage across blueprints and the system index.

        Purpose:
            Guard against roots that are missing in one representation.
        Contract:
            - Blueprint roots must exist in the index and be marked as roots.
            - Index roots must have a corresponding blueprint entry.
            - Cancellation is honored between loops.
        Args:
            index: Spell system index being validated.
            blueprints: Root blueprints keyed by root spell id.
            phase4_results: Phase-4 validation artifacts keyed by spell id.
            broken_spell_ids: Set of broken spell ids.
            diagnostics: Collection that receives diagnostics.
            cancel_event: Optional cancellation signal.
        Returns:
            None.
        Raises:
            OperationCancelledError:
                If ``cancel_event`` is set while iterating.
        """
        for root_id in blueprints.keys():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            node = index.get_node(root_id)
            if node is None:
                diagnostics.append(
                    SystemDiagnostic(
                        code="root_missing_in_index",
                        message=(
                            f"Root '{root_id}' has a blueprint but is missing from SpellSystemIndex."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=root_id,
                        root_id=root_id,
                    )
                )
                continue

            if not node.is_root:
                diagnostics.append(
                    SystemDiagnostic(
                        code="root_not_marked_in_index",
                        message=(
                            f"Root '{root_id}' is not marked as root in SpellSystemIndex."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=root_id,
                        root_id=root_id,
                    )
                )

        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            if not node.is_root:
                continue
            if node.spell_id in blueprints:
                continue

            diagnostics.append(
                SystemDiagnostic(
                    code="missing_root_blueprint",
                    message=(
                        f"SpellSystemIndex marks '{node.spell_id}' as a root but no blueprint exists."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=node.spell_id,
                    root_id=node.spell_id,
                )
            )
