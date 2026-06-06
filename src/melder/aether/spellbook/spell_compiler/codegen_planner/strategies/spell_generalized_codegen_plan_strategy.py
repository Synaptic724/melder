from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenPlanBuilder,
    SpellGeneralizedCodegenPlanVariant,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy import (
    SpellCodegenPlanStrategy,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)


class SpellGeneralizedCodegenPlanStrategy(SpellCodegenPlanStrategy):
    """
    Generalized model-native codegen-plan strategy.

    Purpose:
        Build the current default planner output directly from
        `SpellCodegenModel` using the fully ported generalized lane-plan
        builder.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable plan strategy id.
        """
        return "generalized_codegen_plan"

    def apply(
            self,
            state: SpellCodegenModel,
            artifact: SpellCompilerArtifact,
            plan: SpellCodegenPlan,
    ) -> None:
        """
        Populate the generic plan container from fitted model truth.

        Contract:
            - Uses the fully ported generalized lane-plan builder.
            - Does not lift legacy `ExecutionPlan` objects into the output
              lanes.
            - `artifact` remains part of the planner strategy contract but is
              not needed by this model-native strategy body.
        """
        _ = artifact
        no_overrides_builder = SpellGeneralizedCodegenPlanBuilder(
            state=state,
            plan_variant=SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES,
        )
        overrides_builder = SpellGeneralizedCodegenPlanBuilder(
            state=state,
            plan_variant=SpellGeneralizedCodegenPlanVariant.OVERRIDES,
        )
        plan.no_overrides_plan = no_overrides_builder.build()
        plan.overrides_plan = overrides_builder.build()
        plan.metadata["selected_strategy_id"] = self.strategy_id
        plan.metadata["discovery_reason"] = (
            "default_generalized_model_native_strategy"
        )
        plan.metadata["model_sections"] = state.section_names()
