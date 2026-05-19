from typing import Dict, List, Mapping, Optional, Set

from mypy_extensions import mypyc_attr

# Melder imports
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent

@mypyc_attr(native_class=True)
class RootCoverageStrategy(SpellSystemValidationStrategy):
    """
    Guard that root designation stays aligned between blueprints and the index.

    Phase 5 produces two different root-facing views:

    - root blueprints used by later planning
    - `SpellSystemIndex` nodes with `is_root` metadata used by system-level
      reasoning and change control

    This strategy checks both directions so we catch roots that exist in one
    representation but not the other, or roots that are present in the index
    but not explicitly marked as such.
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
                        details={
                            "root_id": root_id,
                            "index_node_ids": sorted(index.nodes.keys()),
                            "index_root_ids": sorted(
                                index_node.spell_id
                                for index_node in index.nodes.values()
                                if index_node.is_root
                            ),
                        },
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
                        details={
                            "root_id": root_id,
                            "node_is_root": node.is_root,
                            "index_root_ids": sorted(
                                index_node.spell_id
                                for index_node in index.nodes.values()
                                if index_node.is_root
                            ),
                        },
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
                    details={
                        "root_id": node.spell_id,
                        "blueprint_root_ids": sorted(blueprints.keys()),
                        "index_root_ids": sorted(
                            index_node.spell_id
                            for index_node in index.nodes.values()
                            if index_node.is_root
                        ),
                    },
                )
            )

