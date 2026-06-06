from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state import (
    GeneralizedCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_no_overrides_codegen_creation_step import (
    GeneralizedNoOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class FallbackNoOverridesCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Fallback public phase-11 strategy for no-overrides-only creation output.

    Purpose:
        Keep the existing fallback discovery/result contract while routing the
        actual work through the generalized no-overrides family step.
    """

    __slots__ = [
        "_step",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._step = GeneralizedNoOverridesCodegenCreationStep()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable fallback public strategy id.
        """
        return "generalized_no_overrides_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Populate the no-overrides runtime output through the generalized step.
        """
        state = GeneralizedCodegenCreationState(
            spell_codegen_model=spell_codegen_model,
            spell_codegen_plan=spell_codegen_plan,
            spell_codegen_creation=spell_codegen_creation,
        )
        self._step.apply(state)
