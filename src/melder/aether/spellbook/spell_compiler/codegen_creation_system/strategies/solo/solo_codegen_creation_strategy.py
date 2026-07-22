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
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_lazy_door_step import (
    SoloLazyDoorStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.steps.solo_manifest_step import (
    SoloManifestStep,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class SoloCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Manifest-first phase-11 family for solo planner output.

    Purpose:
        Modeled on the generalized family: a marshal-safe manifest is built
        first, then both final runtime doors are published as lazy closures
        that compile the root-only solo executors at first meld. Cache export
        is "persist the manifest"; cache load is "hydrate the manifest" - the
        same single assembly program the live path runs.

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
        Build the solo family facade and its ordered steps.
        """
        super().__init__()
        self._steps: Tuple[CodegenCreationFamilyStep, ...] = (
            SoloManifestStep(),
            SoloLazyDoorStep(),
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

        Contract:
            Wraps the three inputs in a `SoloCodegenCreationState` and runs the
            ordered family steps (manifest, then lazy-door) over it; the steps
            populate the passed `spell_codegen_creation` in place. Finally stamps
            `creation_context_strategy` = this family's id into the creation's
            metadata. Returns nothing - the populated creation is the output.

        Args:
            spell_codegen_model:
                Fitted spell model for the current compile.
            spell_codegen_plan:
                Chosen plan whose single-spell lane the family realizes.
            spell_codegen_creation:
                Artifact-owned creation sink the steps populate in place.

        Returns:
            None.
        """
        state = SoloCodegenCreationState(
            spell_codegen_model=spell_codegen_model,
            spell_codegen_plan=spell_codegen_plan,
            spell_codegen_creation=spell_codegen_creation,
        )
        for step in self._steps:
            step.apply(state)
        spell_codegen_creation.metadata["creation_context_strategy"] = (
            self.strategy_id
        )
