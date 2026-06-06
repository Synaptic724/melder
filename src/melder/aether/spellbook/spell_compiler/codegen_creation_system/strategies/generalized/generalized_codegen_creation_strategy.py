from typing import Tuple

from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state import (
    GeneralizedCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_creation_context_setup_step import (
    GeneralizedCreationContextSetupStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_finalize_creation_context_step import (
    GeneralizedFinalizeCreationContextStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_no_overrides_codegen_creation_step import (
    GeneralizedNoOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.steps.generalized_overrides_codegen_creation_step import (
    GeneralizedOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.shared_strategy_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class GeneralizedCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Generalized phase-11 family facade.

    Purpose:
        Preserve the current generalized phase-11 behavior behind one public
        strategy id, while the internal work is split into ordered family-local
        steps that operate on one mutable state object.

    Contract:
        - This is the public phase-11 generalized family id selected by
          discovery.
        - Internal steps may change over time without widening the external
          `CodegenCreationSystem` contract.
        - Final runtime output remains exactly one `SpellCodegenCreation`.
    """

    __slots__ = [
        "_steps",
    ]

    def __init__(self) -> None:
        """
        Build the generalized family facade and its ordered internal steps.
        """
        super().__init__()
        self._steps: Tuple[CodegenCreationFamilyStep, ...] = (
            GeneralizedCreationContextSetupStep(),
            GeneralizedNoOverridesCodegenCreationStep(),
            GeneralizedOverridesCodegenCreationStep(),
            GeneralizedFinalizeCreationContextStep(),
        )

    @property
    def strategy_id(self) -> str:
        """
        Return the stable generalized family id.
        """
        return "generalized_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Execute the generalized family over one mutable state object.
        """
        state = GeneralizedCodegenCreationState(
            spell_codegen_model=spell_codegen_model,
            spell_codegen_plan=spell_codegen_plan,
            spell_codegen_creation=spell_codegen_creation,
        )
        for step in self._steps:
            step.apply(state)
        spell_codegen_creation.metadata["creation_context_strategy"] = (
            self.strategy_id
        )
