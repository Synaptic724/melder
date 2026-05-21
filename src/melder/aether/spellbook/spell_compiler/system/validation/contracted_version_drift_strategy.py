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
            
from mypy_extensions import mypyc_attr

from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)

@mypyc_attr(native_class=True)
class ContractedVersionDriftStrategy(SpellSystemValidationStrategy):
    """
    Guard that the visible system index does not drift onto stale lineage versions.

    This strategy compares the version ids stored on `SpellSystemIndex` nodes
    against the currently visible spell versions for each lineage. It is aimed
    at contracted/borrowed visibility scenarios where the system graph can lag
    behind the active visible version set and end up validating or planning
    against an outdated node revision.
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
        Validate that index nodes align with visible lineage versions.

        Purpose:
            Surface cases where SpellSystemIndex references outdated spell
            version ids for a lineage visible in the spellbook.
        Contract:
            - Uses spell_lookup to determine visible current versions.
            - Emits errors when a node's spell_id is not a visible version.
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
                If cancel_event`` is set while iterating.
        """
        lineage_to_versions: Dict[str, Set[str]] = {}
        for spell_id, spell in spell_lookup.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            lineage_id = spell.spell_index.id
            lineage_to_versions.setdefault(lineage_id, set()).add(spell_id)

        for node in index.nodes.values():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            lineage_id = node.lineage_id
            if lineage_id is None:
                continue
            visible_versions = lineage_to_versions.get(lineage_id)
            if not visible_versions:
                continue
            if node.spell_id in visible_versions:
                continue
            diagnostics.append(
                SystemDiagnostic(
                    code="contracted_version_drift",
                    message=(
                        f"Spell '{node.spell_id}' is not a visible current version for "
                        f"lineage '{lineage_id}'."
                    ),
                    severity=SystemDiagnosticSeverity.ERROR,
                    spell_id=node.spell_id,
                    root_id=None,
                    details={
                        "spell_id": node.spell_id,
                        "lineage_id": lineage_id,
                        "visible_versions": sorted(visible_versions),
                    },
                )
            )



