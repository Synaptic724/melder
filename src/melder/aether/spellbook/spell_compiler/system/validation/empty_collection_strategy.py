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
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


class EmptyCollectionStrategy(SpellSystemValidationStrategy):
    """
    Guard that a required collection socket resolved to at least one provider.

    Purpose:
        By Phase 6 the per-root blueprints hold the combined, fully stitched
        DAGs. That is the authoritative place to answer "did this list[Frame]
        actually wire up to anything?" - a question no single phase-3 local
        frame can answer on its own. This strategy walks each rooted DAG and,
        for every spell that declares a required collection parameter, counts
        the DAG edges that fed that parameter. A required collection that wired
        zero providers cannot be satisfied, so it is reported as a system-level
        error at conjure time rather than crashing later with a missing-argument
        TypeError at meld.

    Contract:
        - Walks blueprints[root].dag (the combined Phase-5 graph), not the
          per-spell topology.
        - A collection parameter's members are the DAG parents of the owning
          node whose incoming param name matches the parameter.
        - Emits one collection_socket_no_providers ERROR per required
          (non-optional) collection parameter that wired zero providers.
        - Optional collection parameters are skipped: an optional list[Frame]
          may legitimately resolve to nothing.
        - Reads only; never mutates the blueprint, DAG, or index.
        - Honors cancellation between roots.
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
        Flag required collection sockets that wired zero providers in the DAG.

        Purpose:
            Convert an unsatisfiable required list[Frame] dependency into a
            clean fail-fast conjure error, decided from the combined Phase-5
            graph where every provider that could satisfy the socket is visible.

        Contract:
            - Iterates every root blueprint and every node in its combined DAG.
            - For each node that has a required collection requirement, counts
              the DAG parents whose incoming param name matches the parameter.
            - Emits a collection_socket_no_providers ERROR when that count is
              zero.
            - Skips optional collection parameters and nodes without
              requirements (existing-creation spells, missing artifacts).
            - Reads only; never mutates Phase 5/6 inputs.
            - Honors cancel_event between roots.

        Args:
            index:
                Frame-level spell system index being validated.
            blueprints:
                Root blueprints keyed by root spell id; each owns the combined
                Phase-5 DAG.
            phase4_results:
                Per-spell Phase 4 artifacts keyed by spell id.
            broken_spell_ids:
                Spell ids already known broken at the spell-validation layer.
            spell_system_states:
                System state registry (unused here; collection truth comes from
                the combined DAG plus per-spell requirements).
            spell_lookup:
                Visible spell version ids to spell objects for this scope.
            diagnostics:
                Shared list to append new diagnostics into.
            cancel_event:
                Optional cancellation signal honored during the walk.

        Returns:
            None.

        Raises:
            OperationCancelledError:
                If cancel_event is set while iterating.
        """
        seen: Set[str] = set()

        for root_id, blueprint in blueprints.items():
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()

            dag = blueprint.dag
            for node_id in dag.nodes.keys():
                if node_id in seen:
                    continue
                seen.add(node_id)

                spell = spell_lookup.get(node_id)
                if spell is None:
                    continue
                requirements = spell._compiler_artifact._requirements
                if requirements is None:
                    continue

                collection_params = [
                    param
                    for param in requirements.parameters
                    if param.di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION
                    and not param.is_optional
                ]
                if not collection_params:
                    continue

                wired_counts = self._count_wired_members_by_param(
                    dag=dag,
                    node_id=node_id,
                )

                for param in collection_params:
                    if wired_counts.get(param.name, 0) > 0:
                        continue
                    diagnostics.append(
                        SystemDiagnostic(
                            code="collection_socket_no_providers",
                            message=(
                                f"Spell '{node_id}' parameter '{param.name}' "
                                "declares a required collection dependency "
                                "(list[...]) but no providers wired into it in "
                                "the resolved graph. Bind at least one "
                                "implementation under its frame, or make the "
                                "parameter optional."
                            ),
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=node_id,
                            root_id=root_id,
                            details={
                                "spell_id": node_id,
                                "param_name": param.name,
                            },
                        )
                    )

    @staticmethod
    def _count_wired_members_by_param(
            *,
            dag: object,
            node_id: str,
    ) -> Dict[str, int]:
        """
        Count DAG parent edges feeding each constructor parameter of a node.

        Purpose:
            The number of providers wired into a collection socket equals the
            number of DAG parents of the owning node whose incoming edge is
            tagged with that parameter name.

        Contract:
            - Returns an empty mapping when the node is absent from the DAG.
            - Keys are constructor parameter names; values are wired provider
              counts.
            - Reads only.

        Args:
            dag:
                The combined Phase-5 DAG owning the node.
            node_id:
                The owning spell version id whose incoming edges are counted.

        Returns:
            Dict[str, int]: Parameter name to wired provider count.
        """
        node = dag.get_node(node_id)
        if node is None:
            return {}
        counts: Dict[str, int] = {}
        for parent_node in node.dependencies:
            param_name = node.incoming_params.get(parent_node)
            if param_name is None:
                continue
            counts[param_name] = counts.get(param_name, 0) + 1
        return counts
