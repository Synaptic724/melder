from typing import Any, Dict, Optional, Sequence, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)
from melder.aether.spellbook.spell_compiler.blueprints.execution_plan import (
    ExecutionPlan,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


class SpellArtifactProcessor:
    """
    Phase 12 processor orchestrator over compiler artifact inputs.

    Purpose:
        Consume current compiler artifact truth, derive a distilled
        `SpellCodegenModel`, and then run the configured processor strategies
        over that model.

    Contract:
        - Owns no runtime/compiler artifacts itself.
        - Builds a fresh model per `process(...)` call.
        - Strategy execution is ordered and deterministic.
        - The scaffold slice allows an empty strategy sequence and still
          produces a valid assessed model.
        - Assessment defaults are recorded even when no concrete strategies
          exist yet, so later plan building has a stable baseline surface.
    """

    __slots__ = [
        "_strategies",
    ]

    def __init__(
            self,
            *,
            strategies: Optional[Sequence[SpellArtifactProcessorStrategy]] = None,
    ) -> None:
        """
        Build one processor with an ordered strategy sequence.
        """
        if strategies is None:
            self._strategies: Tuple[SpellArtifactProcessorStrategy, ...] = ()
        else:
            self._strategies = tuple(strategies)

    def process(
            self,
            artifact: SpellCompilerArtifact,
    ) -> SpellCodegenModel:
        """
        Build the model from the current artifact and run the strategy sequence.

        Args:
            artifact:
                Compiler-owned artifact supplying the current phase truth.

        Returns:
            SpellCodegenModel:
                Fresh model object after baseline assessment and strategy
                processing.
        """
        model = self._build_model(artifact)
        assessment = model.assessment
        assessment["processor_ready"] = True
        assessment["section_names"] = model.section_names()
        assessment["strategy_count"] = len(self._strategies)

        for strategy in self._strategies:
            strategy.process(model)
            model.applied_strategy_ids.append(strategy.strategy_id)

        assessment["applied_strategy_ids"] = model.snapshot_applied_strategy_ids()
        return model

    @staticmethod
    def _build_model(
            artifact: SpellCompilerArtifact,
    ) -> SpellCodegenModel:
        """
        Build one fresh Phase 12 codegen model from current artifact truth.

        Contract:
            - Uses current artifact state only.
            - Distills selector fields instead of copying raw artifact bags.
            - Short-circuits existing-creation mode when no construction-planning
              artifacts exist.
        """
        occurrence_shape_profile = artifact._occurrence_shape_profile_phase8 or {}
        injection_shape_profile = artifact._injection_shape_profile_phase9 or {}
        override_shape_profile = artifact._override_shape_profile_phase10 or {}
        execution_shape_profile = artifact._execution_shape_profile_phase11 or {}

        no_overrides_plan = artifact._execution_plan_phase11_no_overrides
        root_step = SpellArtifactProcessor._resolve_root_step(no_overrides_plan)
        if root_step is None:
            build_kind = "existing_creation"
            existence = None
            route_family = "existing_creation"
            node_count = 1
            root_dependency_count = 0
            max_depth = 0
            max_width = 1
            shared_node_count = 0
            graph_family = "single"
            max_dependency_count = 0
            dependency_arity_histogram: Tuple[Tuple[int, int], ...] = ()
            has_calln = False
            contract_payload_count = 0
            call_shape_family = "direct"
            fast_transient_eligible = False
        else:
            build_kind = "construct"
            existence = root_step.existence
            route_family = SpellArtifactProcessor._route_family_from_existence(
                existence,
            )
            node_count = int(
                occurrence_shape_profile.get(
                    "unique_spell_count",
                    execution_shape_profile.get("unique_spell_count", 0),
                )
            )
            root_dependency_count = len(root_step.dependency_keys)
            max_depth = int(
                occurrence_shape_profile.get(
                    "max_occurrence_depth",
                    execution_shape_profile.get("max_occurrence_depth", 0),
                )
            )
            max_width = int(occurrence_shape_profile.get("max_width", 0))
            shared_node_count = int(occurrence_shape_profile.get("shared_spell_count", 0))
            graph_family = SpellArtifactProcessor._graph_family(
                node_count=node_count,
                max_depth=max_depth,
                max_width=max_width,
                shared_node_count=shared_node_count,
            )
            max_dependency_count = int(
                execution_shape_profile.get(
                    "max_dependency_count",
                    artifact._execution_plan_max_dependency_count_phase11 or 0,
                )
            )
            dependency_arity_histogram = tuple(
                execution_shape_profile.get("dependency_arity_histogram", ())
            )
            has_calln = bool(
                execution_shape_profile.get(
                    "has_calln",
                    artifact._execution_plan_has_calln_phase11 or False,
                )
            )
            contract_payload_count = int(
                execution_shape_profile.get("contract_payload_step_count", 0)
            )
            call_shape_family = SpellArtifactProcessor._call_shape_family(
                root_dependency_count=root_dependency_count,
                max_dependency_count=max_dependency_count,
                has_calln=has_calln,
            )
            fast_transient_eligible = bool(
                execution_shape_profile.get("fast_transient_available", False)
                and existence is Existence.many
            )

        target_spec_count = int(override_shape_profile.get("target_spec_count", 0))
        targeted_socket_count = int(
            override_shape_profile.get("targeted_socket_count", 0)
        )
        max_targets_per_spec = int(
            override_shape_profile.get("max_targets_per_spec", 0)
        )
        max_target_path_depth = int(
            override_shape_profile.get("max_target_path_depth", 0)
        )
        root_positional_override_relevant = bool(
            injection_shape_profile.get("positional_override_instance_count", 0) > 0
        )
        override_shape_family = SpellArtifactProcessor._override_shape_family(
            target_spec_count=target_spec_count,
            max_targets_per_spec=max_targets_per_spec,
            max_target_path_depth=max_target_path_depth,
        )

        return SpellCodegenModel(
            build_kind=build_kind,
            existence=existence,
            route_family=route_family,
            node_count=node_count,
            root_dependency_count=root_dependency_count,
            max_depth=max_depth,
            max_width=max_width,
            shared_node_count=shared_node_count,
            graph_family=graph_family,
            max_dependency_count=max_dependency_count,
            dependency_arity_histogram=dependency_arity_histogram,
            has_calln=has_calln,
            contract_payload_count=contract_payload_count,
            call_shape_family=call_shape_family,
            target_spec_count=target_spec_count,
            targeted_socket_count=targeted_socket_count,
            max_targets_per_spec=max_targets_per_spec,
            max_target_path_depth=max_target_path_depth,
            root_positional_override_relevant=root_positional_override_relevant,
            override_shape_family=override_shape_family,
            fast_transient_eligible=fast_transient_eligible,
        )

    @staticmethod
    def _resolve_root_step(
            no_overrides_plan: Optional[ExecutionPlan],
    ) -> Optional[Any]:
        """
        Return the root execution step for the current no-overrides plan.
        """
        if no_overrides_plan is None or not no_overrides_plan.steps:
            return None
        root_instance_key = no_overrides_plan.root_instance_key
        for step in no_overrides_plan.steps:
            if step.instance_key == root_instance_key:
                return step
        return None

    @staticmethod
    def _route_family_from_existence(
            existence: Existence,
    ) -> str:
        """
        Convert root existence into the distilled route/storage family.
        """
        if existence is Existence.unique_per_spell_space:
            return "spellspace"
        if existence is Existence.unique_per_conduit:
            return "unique_per_conduit"
        if existence is Existence.many:
            return "many"
        return "shared"

    @staticmethod
    def _graph_family(
            *,
            node_count: int,
            max_depth: int,
            max_width: int,
            shared_node_count: int,
    ) -> str:
        """
        Classify the overall graph shape into a small planning family.
        """
        if node_count <= 1:
            return "single"
        if shared_node_count > 0:
            return "shared_dag"
        if max_depth <= 1:
            return "flat"
        if max_width <= 1:
            return "chain"
        return "complex"

    @staticmethod
    def _call_shape_family(
            *,
            root_dependency_count: int,
            max_dependency_count: int,
            has_calln: bool,
    ) -> str:
        """
        Classify the call shape that later planning should care about.
        """
        if has_calln:
            return "generic"
        if max_dependency_count <= 1:
            return "direct"
        if root_dependency_count >= 8:
            return "wide"
        return "generic"

    @staticmethod
    def _override_shape_family(
            *,
            target_spec_count: int,
            max_targets_per_spec: int,
            max_target_path_depth: int,
    ) -> str:
        """
        Classify the override-geometry shape for later plan building.
        """
        if target_spec_count <= 0:
            return "none"
        if max_target_path_depth > 1:
            return "deep"
        if max_targets_per_spec <= 1:
            return "simple"
        if max_targets_per_spec > 1:
            return "wide"
        return "complex"
