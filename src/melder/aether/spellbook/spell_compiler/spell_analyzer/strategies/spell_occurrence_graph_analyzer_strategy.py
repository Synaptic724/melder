from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
    OccurrencePlanBuilder,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_8 import (
    CompilerPhase8,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_occurrence_graph_analysis import (
    SpellOccurrenceGraphAnalysis,
)

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
        RootResolutionBlueprint,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spellbook import Spellbook


class SpellOccurrenceGraphAnalyzerStrategy(SpellAnalyzerStrategy):
    """
    Build the occurrence-graph analysis artifact for one spell.

    Purpose:
        Reuse the current Phase 8 graph-expansion logic to produce the
        compiler-owned occurrence graph analysis surface. This strategy owns
        the first part of the medium split:
        - expanded occurrence graph
        - graph-level counts
        - shared-collapse eligibility
        - cache/signature companions used by later occurrence analysis steps

    Contract:
        - Consumes `Spell`, the existing `SpellCompilerArtifact`, the owning
          Spellbook spell pool, Phase 5 rooted blueprint truth, and current
          spell-system topology state.
        - Reuses the current Phase 8 fast-key and input-signature helpers for
          parity with the old phase.
        - Publishes only:
          - `_occurrence_graph_analysis`
          - `_occurrence_analysis_fast_key`
          - `_occurrence_analysis_input_signature`
        - Does not compute execution order, instance/sharedness, or contract
          payload routing artifacts. Later strategies own those artifacts.
        - Existing-creation spells no-op because they do not participate in
          occurrence expansion.

    Threading:
        - Runs inside compiler-thread orchestration only.
        - Assumes upstream compiler coordination serializes artifact mutation
          for one spell during this analysis pass.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this occurrence-graph strategy.
        """
        return "spell_occurrence_graph_analyzer"

    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Build and publish the occurrence-graph analysis artifact.

        Purpose:
            Port the graph-expansion portion of current Phase 8 into the new
            analyzer lane while keeping the cache/signature semantics needed
            for later occurrence analysis steps.
        """
        artifact.check_cleaned()
        if spell.is_existing_creation:
            return

        spellbook: Optional["Spellbook"] = spell._spellbook
        if spellbook is None:
            raise RuntimeError(
                "SpellOccurrenceGraphAnalyzerStrategy requires a live owning Spellbook."
            )
        root_blueprint: Optional["RootResolutionBlueprint"] = artifact._root_blueprint_phase5
        if root_blueprint is None:
            raise RuntimeError(
                "SpellOccurrenceGraphAnalyzerStrategy requires Phase 5 root blueprint truth."
            )

        spell_lookup = spellbook._spell_id_pool
        spell_system_states: "SpellSystemStates" = spell._spell_system_states
        phase8 = CompilerPhase8()
        fast_key = phase8._build_phase8_occurrence_plan_fast_key(
            root_blueprint=root_blueprint,
            spell_lookup=spell_lookup,
            spellbook=spellbook,
            spell_system_states=spell_system_states,
        )
        input_signature = phase8._build_phase8_occurrence_plan_input_signature(
            root_blueprint=root_blueprint,
            spell_lookup=spell_lookup,
            spellbook=spellbook,
            spell_system_states=spell_system_states,
        )
        if (
                fast_key is not None
                and artifact._occurrence_analysis_fast_key == fast_key
                and input_signature is not None
                and artifact._occurrence_analysis_input_signature == input_signature
                and artifact._occurrence_graph_analysis is not None
        ):
            return

        builder = OccurrencePlanBuilder(
            root_spell=spell,
            blueprint=root_blueprint,
            spell_lookup=spell_lookup,
            system_states=spell_system_states,
        )
        collapse_shared_occurrences = builder._should_collapse_shared_occurrences()
        occurrence_graph = builder._build_occurrence_graph(
            dag=root_blueprint.dag,
            root_spell_id=root_blueprint.root_spell_id,
            collapse_shared_occurrences=collapse_shared_occurrences,
        )
        builder._extend_occurrence_graph_with_ordered_nodes(
            occurrence_graph=occurrence_graph,
            ordered_node_ids=root_blueprint.ordered_node_ids,
            dag=root_blueprint.dag,
            collapse_shared_occurrences=collapse_shared_occurrences,
        )
        graph_analysis = SpellOccurrenceGraphAnalysis(
            root_spell_id=root_blueprint.root_spell_id,
            occurrence_graph=occurrence_graph,
            path_registry=root_blueprint.path_registry,
            occurrence_count=len(occurrence_graph),
            edge_count=self._count_occurrence_edges(occurrence_graph),
            topology_dependency_count=self._count_topology_dependencies(
                spell_system_states=spell_system_states,
                occurrence_graph=occurrence_graph,
            ),
            dag_fallback_dependency_count=self._count_dag_fallback_dependencies(
                spell_system_states=spell_system_states,
                occurrence_graph=occurrence_graph,
            ),
            mutation_override_dependency_count=self._count_mutation_override_dependencies(
                spell_lookup=spell_lookup,
            ),
            shared_collapse_enabled=collapse_shared_occurrences,
        )
        builder.cleanup()

        previous_graph = artifact._occurrence_graph_analysis
        artifact._occurrence_graph_analysis = graph_analysis
        artifact._occurrence_analysis_fast_key = fast_key
        artifact._occurrence_analysis_input_signature = input_signature
        self._cleanup_previous(previous_graph, graph_analysis)

    @staticmethod
    def _cleanup_previous(
            previous: Optional[SpellOccurrenceGraphAnalysis],
            current: SpellOccurrenceGraphAnalysis,
    ) -> None:
        """
        Best-effort cleanup for one superseded occurrence-graph analysis artifact.
        """
        if previous is None or previous is current:
            return
        try:
            previous.cleanup()
        except Exception:
            pass

    @staticmethod
    def _count_occurrence_edges(
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count the total number of dependency edges in the occurrence graph.
        """
        edge_count = 0
        for dependency_map in occurrence_graph.values():
            for dependency_occurrences in dependency_map.values():
                edge_count += len(dependency_occurrences)
        return edge_count

    @staticmethod
    def _count_topology_dependencies(
            *,
            spell_system_states: "SpellSystemStates",
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count edges whose spell ids have topology entries, which approximates
        topology-driven expansion pressure.
        """
        local_topologies = spell_system_states._local_topologies
        topology_dependency_count = 0
        for occurrence, dependency_map in occurrence_graph.items():
            spell_id, _ = occurrence
            if local_topologies.get(spell_id) is None:
                continue
            for dependency_occurrences in dependency_map.values():
                topology_dependency_count += len(dependency_occurrences)
        return topology_dependency_count

    @staticmethod
    def _count_dag_fallback_dependencies(
            *,
            spell_system_states: "SpellSystemStates",
            occurrence_graph: Dict[Tuple[str, int], Dict[str, List[Tuple[str, int]]]],
    ) -> int:
        """
        Count edges whose spell ids had to fall back to DAG metadata.
        """
        local_topologies = spell_system_states._local_topologies
        fallback_count = 0
        for occurrence, dependency_map in occurrence_graph.items():
            spell_id, _ = occurrence
            if local_topologies.get(spell_id) is not None:
                continue
            for dependency_occurrences in dependency_map.values():
                fallback_count += len(dependency_occurrences)
        return fallback_count

    @staticmethod
    def _count_mutation_override_dependencies(
            *,
            spell_lookup: Dict[str, "Spell"],
    ) -> int:
        """
        Count spells currently carrying mutation overrides.
        """
        mutation_override_count = 0
        for spell in spell_lookup.values():
            if spell.mutation_override:
                mutation_override_count += 1
        return mutation_override_count
