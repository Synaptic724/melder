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


class SocketAmbiguityStrategy(SpellSystemValidationStrategy):
    """
    Internal

    Purpose:
        Detect ambiguous socket names that break unique override semantics.
    Contract:
        - Emits ``socket_ref_name_ambiguous`` when a param name appears more
          than once in a root's socket refs.
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
        Validate socket name uniqueness within each root blueprint.

        Purpose:
            Ensure unique override targeting (``*param``) remains unambiguous.
        Contract:
            - Each duplicated param_name yields a diagnostic.
            - Cancellation is honored between roots.
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
        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            counts: Dict[str, int] = {}
            for socket in blueprint.socket_refs:
                counts[socket.param_name] = counts.get(socket.param_name, 0) + 1

            for param_name, count in counts.items():
                if count <= 1:
                    continue
                diagnostics.append(
                    SystemDiagnostic(
                        code="socket_ref_name_ambiguous",
                        message=(
                            f"Root '{root_id}' has {count} sockets named '{param_name}', "
                            "which makes unique overrides ambiguous."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=root_id,
                        root_id=root_id,
                        details={
                            "param_name": param_name,
                            "count": count,
                        },
                    )
                )
