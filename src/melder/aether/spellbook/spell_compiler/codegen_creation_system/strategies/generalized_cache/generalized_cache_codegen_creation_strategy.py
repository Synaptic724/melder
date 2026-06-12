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
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.generalized_cache_codegen_creation_state import (
    GeneralizedCacheCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.steps.generalized_cache_hydrate_step import (
    GeneralizedCacheLazyDoorStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.steps.generalized_cache_manifest_step import (
    GeneralizedCacheManifestStep,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class GeneralizedCacheCodegenCreationStrategy(SpellCodegenStrategy):
    """
    Manifest-first phase-11 family for generalized planner output.

    Purpose:
        Experimental sibling of the generalized family that flows the entire
        build through serialization-shaped data: a marshal-safe manifest is
        built first, then both final runtime doors are hydrated from that
        manifest through one shared hydrator. Cache export becomes "persist
        the manifest"; cache load becomes "hydrate the manifest" - the same
        single assembly program the live path runs.

    Contract:
        - Claims the same model/plan shape as `generalized_codegen_creation`.
        - Final runtime output remains exactly one `SpellCodegenCreation`
          carrying the two route-keyed doors.
        - Publishes the manifest into `SpellCodegenCreation.metadata` for the
          family cache codec.
        - Internal steps may change without widening the external
          `CodegenCreationSystem` contract.
    """

    __slots__ = [
        "_steps",
    ]

    def __init__(self) -> None:
        """
        Build the generalized_cache family facade and its ordered steps.
        """
        super().__init__()
        self._steps: Tuple[CodegenCreationFamilyStep, ...] = (
            GeneralizedCacheManifestStep(),
            GeneralizedCacheLazyDoorStep(),
        )

    @property
    def strategy_id(self) -> str:
        """
        Return the stable generalized_cache family id.
        """
        return "generalized_cache_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Execute the generalized_cache family over one mutable state object.
        """
        state = GeneralizedCacheCodegenCreationState(
            spell_codegen_model=spell_codegen_model,
            spell_codegen_plan=spell_codegen_plan,
            spell_codegen_creation=spell_codegen_creation,
        )
        for step in self._steps:
            step.apply(state)
        spell_codegen_creation.metadata["creation_context_strategy"] = (
            self.strategy_id
        )
