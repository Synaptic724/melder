from typing import Any, Dict, Sequence, Tuple

from melder.aether.conduit.meld.creation_context.creation_context import (
    OverrideRouteConfig,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.blueprints.phase13_overrides_executor import (
    compile_phase13_overrides_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_mutation_overrides_codegen_creation import (
    SpellMutationOverridesCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenLanePlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
    SharedCompilerExecutions,
)


class SpellGeneralizedMutationOverridesCodegenCreationStrategy(
    SpellCodegenStrategy
):
    """
    Generalized mutation-overrides codegen creation strategy.

    Purpose:
        Port the mutation-aware override route packaging that is currently
        assembled in `CreationContextBuilder` into the codegen-creation layer,
        using the generalized mutation-overrides lane plan as the source of
        truth.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable mutation-overrides creation strategy id.
        """
        return "generalized_mutation_overrides_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Populate the mutation-overrides creation payload.

        Contract:
            - Requires the planner to have already produced a
              mutation-overrides lane plan.
            - Builds the spell-static mutation route config from the
              generalized lane plan instead of reading old exported IR.
            - Prebuilds the empty-shape baseline override executor for later
              runtime reuse.
        """
        mutation_overrides_plan = spell_codegen_plan.mutation_overrides_plan
        if mutation_overrides_plan is None:
            raise RuntimeError(
                "Mutation-overrides codegen creation requires a mutation_overrides_plan."
            )

        override_route_config = self._build_override_route_config(
            spell_codegen_model=spell_codegen_model,
            mutation_overrides_plan=mutation_overrides_plan,
        )
        spell_codegen_creation.mutation_overrides_creation = (
            SpellMutationOverridesCodegenCreation(
                override_route_config=override_route_config,
                baseline_executor=override_route_config.baseline_executor,
                metadata={
                    "lane_id": mutation_overrides_plan.lane_id,
                    "root_spell_id": mutation_overrides_plan.root_spell_id,
                    "step_count": len(mutation_overrides_plan.steps),
                    "steps_rows_signature": (
                        override_route_config.plan_signature[2]
                    ),
                },
            )
        )

    def _build_override_route_config(
            self,
            *,
            spell_codegen_model: SpellCodegenModel,
            mutation_overrides_plan: SpellGeneralizedCodegenLanePlan,
    ) -> OverrideRouteConfig:
        """
        Build the spell-static mutation-aware override route config.

        Contract:
            - Uses the generalized mutation-overrides lane plan as the source
              of truth.
            - Derives deterministic plan rows compatible with the current
              override executor compiler.
            - Prebuilds the baseline empty-shape override executor.
        """
        steps_rows = self._build_steps_rows(mutation_overrides_plan.steps)
        steps_rows_signature = SharedCompilerExecutions.hash_codegen_signature(
            steps_rows
        )
        step_spell_ids = tuple(
            step.spell.spell_index.current
            for step in mutation_overrides_plan.steps
        )
        plan_signature = (
            "generalized_mutation_overrides_lane_plan",
            SharedCompilerExecutions.hash_codegen_signature(
                mutation_overrides_plan.lane_id,
                mutation_overrides_plan.root_spell_id,
                step_spell_ids,
                steps_rows_signature,
            ),
            steps_rows_signature,
        )
        spell_lookup = self._build_spell_lookup(mutation_overrides_plan)
        path_registry = None
        graph_shape = spell_codegen_model.graph_shape
        if graph_shape is not None:
            path_registry = graph_shape.path_registry

        baseline_executor = compile_phase13_overrides_executor(
            execution_plan=None,
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=path_registry,
            plan_rows=steps_rows,
            root_spell_id=mutation_overrides_plan.root_spell_id,
            spell_lookup=spell_lookup,
        )
        return OverrideRouteConfig(
            plan_signature=plan_signature,
            path_registry=path_registry,
            plan_rows=steps_rows,
            root_spell_id=mutation_overrides_plan.root_spell_id,
            spell_lookup=spell_lookup,
            empty_shape_key=(
                plan_signature,
                (),
                -1,
            ),
            baseline_executor=baseline_executor,
        )

    @staticmethod
    def _build_spell_lookup(
            mutation_overrides_plan: SpellGeneralizedCodegenLanePlan,
    ) -> Dict[str, Any]:
        """
        Build the spell-id lookup required by mutation-lane hydration.
        """
        spell_lookup: Dict[str, Any] = {}
        for step in mutation_overrides_plan.steps:
            spell_id = step.spell.spell_index.current
            if spell_id in spell_lookup:
                continue
            spell_lookup[spell_id] = step.spell
        return spell_lookup

    @staticmethod
    def _build_steps_rows(
            steps: Sequence[Any],
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Build mutation-aware schema rows from generalized lane steps.
        """
        return tuple(
            SharedCompilerExecutions.build_phase11_step_ir_row(
                step,
                include_override_metadata=True,
            )
            for step in steps
        )
