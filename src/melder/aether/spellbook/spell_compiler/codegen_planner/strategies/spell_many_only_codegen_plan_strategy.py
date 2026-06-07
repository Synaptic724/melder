from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.data.many_only_codegen_plan import (
    ManyOnlyCodegenPlanBuilder,
    ManyOnlyCodegenPlanVariant,
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


class SpellManyOnlyCodegenPlanStrategy(SpellCodegenPlanStrategy):
    """
    Standalone many-only phase-10 planner strategy.

    Purpose:
        Build the many-only phase-10 lanes through many-only-native builder
        surfaces instead of routing through generalized planner data classes.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable many-only plan strategy id.
        """
        return "many_only_codegen_plan"

    def apply(
            self,
            state: SpellCodegenModel,
            artifact: SpellCompilerArtifact,
            plan: SpellCodegenPlan,
    ) -> None:
        """
        Populate the many-only category plan using many-only-native builders.
        """
        _ = artifact
        no_overrides_builder = ManyOnlyCodegenPlanBuilder(
            state=state,
            plan_variant=ManyOnlyCodegenPlanVariant.NO_OVERRIDES,
        )
        overrides_builder = ManyOnlyCodegenPlanBuilder(
            state=state,
            plan_variant=ManyOnlyCodegenPlanVariant.OVERRIDES,
        )
        plan.no_overrides_plan = no_overrides_builder.build()
        plan.overrides_plan = overrides_builder.build()
        plan.metadata["selected_strategy_id"] = self.strategy_id
        plan.metadata["discovery_reason"] = "many_only_visible_spell_set"
        plan.metadata["model_sections"] = state.section_names()
