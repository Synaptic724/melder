from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class SpellGeneralizedCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Generalized placeholder codegen creation strategy.

    Purpose:
        Provide the first codegen creation strategy scaffold without yet
        implementing emitted-code behavior. It proves the new codegen creation
        layer can consume both the model and the plan and publish a final
        artifact-owned output object.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable strategy id.
        """
        return "generalized_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Populate the placeholder codegen creation output.

        Contract:
            - Does not implement emitted-code behavior yet.
            - Records model/plan provenance and lane availability only.
            - Leaves all 3 lane outputs as `None`.
        """
        spell_codegen_creation.selected_strategy_id = self.strategy_id
        spell_codegen_creation.discovery_reason = (
            "default_generalized_codegen_creation_strategy"
        )
        spell_codegen_creation.metadata["model_sections"] = (
            spell_codegen_model.section_names()
        )
        spell_codegen_creation.metadata["plan_strategy_ids"] = (
            spell_codegen_plan.plan_strategy_ids
        )
        spell_codegen_creation.metadata["has_no_overrides_plan"] = (
            spell_codegen_plan.no_overrides_plan is not None
        )
        spell_codegen_creation.metadata["has_overrides_plan"] = (
            spell_codegen_plan.overrides_plan is not None
        )
        spell_codegen_creation.metadata["has_mutation_overrides_plan"] = (
            spell_codegen_plan.mutation_overrides_plan is not None
        )
