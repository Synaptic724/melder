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
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent

@mypyc_attr(native_class=True)
class DependencyTypeSanityStrategy(SpellSystemValidationStrategy):
    """
    Guard against unexpected callable-style dependency types in the system graph.

    This strategy checks whether rooted system dependencies are leaning on
    method/lambda spell types where the broader system graph is expected to be
    dominated by class or existing-creation nodes. It is intentionally a
    warning-level signal rather than a hard failure, because those callable
    nodes can still be valid, but they often indicate a system graph shape that
    deserves extra scrutiny.

    Contract:
        - Emits `dependency_type_unexpected` for method/lambda dependencies.
        - Uses WARNING severity so it informs system review without by itself
          gating resolution.
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
            spell_system_states: SpellSystemStates registry for topology and lineage data.
            spell_lookup: Mapping of visible spell version ids to spell objects.
            diagnostics: Collection that receives diagnostics.
            cancel_event: Optional cancellation signal.
        Returns:
            None.
        Raises:
            OperationCancelledError:
                If cancel_event`` is set while iterating.
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

