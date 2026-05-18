from typing import Dict, List, Mapping, Optional, Set
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
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class LineageVersionConflictStrategy(SpellSystemValidationStrategy):
    """
    Guard that one root DAG does not mix multiple versions of the same lineage.

    Root blueprints are version-id graphs, but they still represent one
    coherent runtime slice. If the same lineage appears multiple times under a
    single root as different version ids, the root is effectively depending on
    mutually conflicting revisions of the same logical spell family. This
    strategy checks the blueprint DAG against the index lineage map and turns
    that mismatch into a root-scoped error before later planning or execution
    phases reason over an internally inconsistent dependency closure.
    """
    __slots__: list[str] = []

    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: ISpellSystemStates,
            spell_lookup: Mapping[str, ISpell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Validate that each root DAG contains at most one version per lineage.

        Purpose:
            Prevent one root blueprint from resolving multiple concrete versions
            of the same logical spell lineage.
        Contract:
            - Uses blueprint DAG node ids as the candidate version set and the
              system index as the source of lineage identity.
            - Missing index nodes and lineage-less nodes are ignored here
              because other strategies already report broken index coverage.
            - Emits one ERROR diagnostic per conflicting lineage within a root,
              with the concrete spell ids that collided.
            - Blueprint, phase-4, and broken-spell inputs are accepted to match
              the shared strategy interface but are not consulted by this check.
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
                If cancel_event`` is set while iterating.
        """
        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            lineage_to_versions: Dict[str, Set[str]] = {}
            for node_id in blueprint.dag.nodes.keys():
                node = index.get_node(node_id)
                if node is None or node.lineage_id is None:
                    continue
                lineage_to_versions.setdefault(node.lineage_id, set()).add(node_id)

            for lineage_id, versions in lineage_to_versions.items():
                if len(versions) <= 1:
                    continue
                diagnostics.append(
                    SystemDiagnostic(
                        code="lineage_version_conflict",
                        message=(
                            f"Root '{root_id}' includes multiple versions for lineage "
                            f"'{lineage_id}': {sorted(versions)}."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=next(iter(versions)),
                        root_id=root_id,
                        details={
                            "lineage_id": lineage_id,
                            "spell_ids": sorted(versions),
                        },
                    )
                )

