from typing import Tuple

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_state import (
    ManyOnlyCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_finalize_creation_context_step import (
    ManyOnlyFinalizeCreationContextStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_no_overrides_codegen_creation_step import (
    ManyOnlyNoOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_overrides_codegen_creation_step import (
    ManyOnlyOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class ManyOnlyCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Many-only phase-11 family facade.

    Purpose:
        Consume the dedicated phase-10 many-only plan family through a real
        many-only creation-family id and state surface instead of routing
        many-only plans back through generalized creation discovery.
    """

    __slots__ = [
        "_steps",
    ]

    def __init__(self) -> None:
        """
        Build the many-only family facade and its ordered internal steps.
        """
        super().__init__()
        self._steps: Tuple[CodegenCreationFamilyStep, ...] = (
            ManyOnlyNoOverridesCodegenCreationStep(),
            ManyOnlyOverridesCodegenCreationStep(),
            ManyOnlyFinalizeCreationContextStep(),
        )

    @property
    def strategy_id(self) -> str:
        """
        Return the stable many-only family id.
        """
        return "many_only_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Execute the many-only family over one mutable many-only state object.
        """
        state = ManyOnlyCodegenCreationState(
            spell_codegen_model=spell_codegen_model,
            spell_codegen_plan=spell_codegen_plan,
            spell_codegen_creation=spell_codegen_creation,
        )
        for step in self._steps:
            step.apply(state)
        spell_codegen_creation.metadata["creation_context_strategy"] = (
            self.strategy_id
        )
