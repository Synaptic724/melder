from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_manifest_state import (
    GeneralizedManifestState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.manifest.generalized_manifest import (
    MANIFEST_METADATA_KEY,
    build_generalized_manifest,
)


class GeneralizedManifestStep(CodegenCreationFamilyStep):
    """
    Manifest build step for the generalized family.

    Purpose:
        Convert phase-9 model and phase-10 plan truth into the family's
        marshal-safe manifest before any executor work happens, so executor
        hydration is a pure function of (manifest, resolver) downstream.

    Contract:
        - Publishes the manifest onto family-local state.
        - Mirrors the manifest into `SpellCodegenCreation.metadata` under
          `MANIFEST_METADATA_KEY` so the cache codec can export it without
          re-reading plan or model objects.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable manifest step id.
        """
        return "generalized_manifest"

    def apply(
            self,
            state: GeneralizedManifestState,
    ) -> None:
        """
        Build and publish the family manifest.
        """
        manifest = build_generalized_manifest(
            spell_codegen_model=state.spell_codegen_model,
            spell_codegen_plan=state.spell_codegen_plan,
        )
        state.manifest = manifest
        state.spell_codegen_creation.metadata[MANIFEST_METADATA_KEY] = manifest
