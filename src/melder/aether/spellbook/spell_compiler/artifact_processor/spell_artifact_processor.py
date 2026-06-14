from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy_builder import (
    SpellArtifactProcessorStrategyBuilder,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell


class SpellArtifactProcessor(Cleanable):
    """
    Processor facade over compiler artifact truth.

    Purpose:
        Build one shell `SpellCodegenModel`, hand analyzer-owned graph truth
        into it, run processor strategies in deterministic order, and publish
        the fitted model back onto `SpellCompilerArtifact`.

    Contract:
        - Owns only the strategy builder.
        - Does not classify or reinterpret the full compiler state after
          strategies run.
        - Leaves section fitting to processor strategies.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_strategy_builder",
    ]

    def __init__(self) -> None:
        """
        Build one processor with an owned strategy builder.
        """
        super().__init__()
        self._strategy_builder = SpellArtifactProcessorStrategyBuilder()

    def cleanup(self) -> None:
        """
        Deterministically release processor-owned state.

        Contract:
            - Idempotent.
            - Cleans the owned strategy builder directly.
            - Drops the processor's only owned reference so later use fails
              honestly through `check_cleaned()`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategy_builder.cleanup()
        del self._strategy_builder

    def process(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
    ) -> None:
        """
        Fit and publish the processor model for the supplied spell/artifact pair.

        Contract:
            - Creates a shell model first.
            - Runs every registered processor strategy against that model.
            - Records processor provenance only after the strategy pass.
            - Does not perform a second adapter/reclassification pass.
            - Publishes the fitted model onto `artifact._spell_codegen_model`.
        """
        previous_spell_codegen_model = artifact._spell_codegen_model
        model = self._build_model_shell(
            spell=spell,
            artifact=artifact,
        )
        strategy_names = self._strategy_builder.registered_strategy_names()
        strategies = self._strategy_builder.get_strategies(strategy_names)

        applied_strategy_ids: list[str] = []
        for strategy in strategies:
            strategy.process(spell, artifact, model)
            applied_strategy_ids.append(strategy.strategy_id)

        assessment = model.assessment
        assessment["processor_ready"] = True
        assessment["section_names"] = model.section_names()
        assessment["strategy_count"] = len(strategies)
        model.applied_strategy_ids.extend(applied_strategy_ids)
        assessment["applied_strategy_ids"] = model.snapshot_applied_strategy_ids()
        artifact._spell_codegen_model = model
        if (
                previous_spell_codegen_model is not None
                and previous_spell_codegen_model is not model
        ):
            try:
                previous_spell_codegen_model.cleanup()
            except Exception:
                pass

    @staticmethod
    def _build_model_shell(
            *,
            spell: Spell,
            artifact: SpellCompilerArtifact,
    ) -> SpellCodegenModel:
        """
        Build one shell model from spell-static and analyzer-owned truth only.

        Purpose:
            Seed the processor pass with the root spell posture plus the
            analyzer-owned graph section, while leaving all derived processor
            sections to the processor strategies.

        Contract:
            - Uses spell-static existence/build-kind facts.
            - Uses analyzer-owned graph truth only for raw graph handoff and
              cheap graph metrics.
            - Does not read old Phase 8/9/10/11 adapter profiles.
        """
        graph_shape = artifact._occurrence_graph_analysis
        build_kind = "existing_creation" if spell.is_existing_creation else "construct"
        existence: Optional[Existence]
        if spell.is_existing_creation:
            existence = None
            route_family = "existing_creation"
        else:
            existence = spell.existence
            if existence is Existence.unique_per_spell_space:
                route_family = "spellspace"
            elif existence is Existence.unique_per_conduit:
                route_family = "unique_per_conduit"
            elif existence is Existence.many:
                route_family = "many"
            elif existence is Existence.unique_per_conduit_lineage:
                route_family = "lineage"
            else:
                route_family = "shared"

        node_count = 0
        root_dependency_count = 0
        max_depth = 0
        max_width = 0
        if graph_shape is not None:
            node_count = graph_shape.occurrence_count
            root_occurrence = (
                graph_shape.root_spell_id,
                graph_shape.path_registry.root_path_id,
            )
            root_dependencies = graph_shape.occurrence_graph.get(root_occurrence, {})
            for dependency_occurrences in root_dependencies.values():
                root_dependency_count += len(dependency_occurrences)

            width_by_depth: Dict[int, int] = {}
            for _, path_id in graph_shape.occurrence_graph.keys():
                depth = graph_shape.path_registry.depth(path_id)
                width_by_depth[depth] = width_by_depth.get(depth, 0) + 1
                if depth > max_depth:
                    max_depth = depth
            max_width = max(width_by_depth.values(), default=0)

        return SpellCodegenModel(
            build_kind=build_kind,
            existence=existence,
            route_family=route_family,
            graph_shape=graph_shape,
            node_count=node_count,
            root_dependency_count=root_dependency_count,
            max_depth=max_depth,
            max_width=max_width,
        )
