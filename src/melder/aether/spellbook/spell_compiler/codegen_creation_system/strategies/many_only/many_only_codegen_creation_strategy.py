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
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_lazy_door_step import (
    ManyOnlyLazyDoorStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.steps.many_only_manifest_step import (
    ManyOnlyManifestStep,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class ManyOnlyCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Manifest-first phase-11 family for many-only planner output.

    Purpose:
        Modeled on the generalized and solo families: a marshal-safe manifest
        is built first, then both final runtime doors are published as lazy
        closures that hydrate at first meld through one shared hydrator.
        Cache export is "persist the manifest"; cache load is "hydrate the
        manifest" - the same single assembly program the live path runs.

    Contract:
        - Phase-11 conjure cost for this family is manifest construction
          only; executor compile and door work happens at first meld.
        - Final runtime output remains exactly one `SpellCodegenCreation`
          carrying the two route-keyed doors.
        - Publishes the manifest into `SpellCodegenCreation.metadata` under
          the shared manifest key for the cross-family cache envelope.
    """

    __slots__ = [
        "_steps",
    ]

    def __init__(self) -> None:
        """
        Build the many_only family facade and its ordered steps.
        """
        super().__init__()
        self._steps: Tuple[CodegenCreationFamilyStep, ...] = (
            ManyOnlyManifestStep(),
            ManyOnlyLazyDoorStep(),
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
        Execute the many_only family over one mutable state object.
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
