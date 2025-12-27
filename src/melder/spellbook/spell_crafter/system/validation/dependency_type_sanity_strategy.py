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
from melder.spellbook.spell_types.spell_types import SpellType
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class DependencyTypeSanityStrategy(SpellSystemValidationStrategy):
    """
    Internal

    Purpose:
        Flag dependency graphs that rely on method/lambda spell types.
    Contract:
        - Emits ``dependency_type_unexpected`` for method/lambda dependencies.
        - Uses WARNING severity to avoid gating resolution.
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
        Validate dependency spell types against system-level expectations.

        Purpose:
            Surface dependency chains that rely on callable spells rather than
            class/existing-creation spells.
        Contract:
            - Emits warnings for method/lambda dependency types.
            - Missing dependency nodes are ignored (handled elsewhere).
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
        disallowed_types = {
            SpellType.METHOD,
            SpellType.METHOD_WITH_BINDING_NAME,
            SpellType.METHOD_WITH_SPELLFRAME,
            SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            SpellType.LAMBDA_METHOD_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        }

        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            for dep_id in node.dependencies:
                dep_node = index.get_node(dep_id)
                if dep_node is None or dep_node.spell_type is None:
                    continue
                if dep_node.spell_type not in disallowed_types:
                    continue
                diagnostics.append(
                    SystemDiagnostic(
                        code="dependency_type_unexpected",
                        message=(
                            f"Spell '{node.spell_id}' depends on '{dep_id}' "
                            f"with type '{dep_node.spell_type.name}'."
                        ),
                        severity=SystemDiagnosticSeverity.WARNING,
                        spell_id=node.spell_id,
                        root_id=None,
                        details={
                            "spell_id": node.spell_id,
                            "dependency_id": dep_id,
                            "dependency_type": dep_node.spell_type.name,
                        },
                    )
                )
