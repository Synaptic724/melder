from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.spell_generalized_codegen_lane_plan import (
    SpellGeneralizedCodegenPlanVariant,
    SpellSoloCodegenPlanBuilder,
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


class SpellGeneralizedSoloCodegenPlanStrategy(SpellCodegenPlanStrategy):
    """
    Solo category planner strategy.

    Purpose:
        Build the solo phase-10 lanes through a dedicated solo builder surface
        instead of routing directly through the generalized builder class.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable solo plan strategy id.
        """
        return "generalized_solo_codegen_plan"

    def apply(
            self,
            state: SpellCodegenModel,
            artifact: SpellCompilerArtifact,
            plan: SpellCodegenPlan,
    ) -> None:
        """
        Populate the solo category plan using the dedicated solo lane builder.
        """
        _ = artifact
        no_overrides_builder = SpellSoloCodegenPlanBuilder(
            state=state,
            plan_variant=SpellGeneralizedCodegenPlanVariant.NO_OVERRIDES,
        )
        overrides_builder = SpellSoloCodegenPlanBuilder(
            state=state,
            plan_variant=SpellGeneralizedCodegenPlanVariant.OVERRIDES,
        )
        plan.no_overrides_plan = no_overrides_builder.build()
        plan.overrides_plan = overrides_builder.build()
        plan.metadata["selected_strategy_id"] = self.strategy_id
        plan.metadata["discovery_reason"] = "solo_visible_spell_count_eq_1"
        plan.metadata["model_sections"] = state.section_names()
