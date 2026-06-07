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
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state import (
    SoloCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_creation_context_setup_step import (
    SoloCreationContextSetupStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_finalize_creation_context_step import (
    SoloFinalizeCreationContextStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_no_overrides_codegen_creation_step import (
    SoloNoOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_overrides_codegen_creation_step import (
    SoloOverridesCodegenCreationStep,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class SoloCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Solo phase-11 family facade.

    Purpose:
        Consume the dedicated phase-10 solo plan family through a real
        solo-owned phase-11 path instead of routing solo plans through
        generalized creation steps or generalized compiler helpers.
    """

    __slots__ = [
        "_steps",
    ]

    def __init__(self) -> None:
        """
        Build the solo family facade and its ordered internal steps.
        """
        super().__init__()
        self._steps: Tuple[CodegenCreationFamilyStep, ...] = (
            SoloCreationContextSetupStep(),
            SoloNoOverridesCodegenCreationStep(),
            SoloOverridesCodegenCreationStep(),
            SoloFinalizeCreationContextStep(),
        )

    @property
    def strategy_id(self) -> str:
        """
        Return the stable solo family id.
        """
        return "solo_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Execute the solo family over one mutable solo state object.
        """
        state = SoloCodegenCreationState(
            spell_codegen_model=spell_codegen_model,
            spell_codegen_plan=spell_codegen_plan,
            spell_codegen_creation=spell_codegen_creation,
        )
        for step in self._steps:
            step.apply(state)
