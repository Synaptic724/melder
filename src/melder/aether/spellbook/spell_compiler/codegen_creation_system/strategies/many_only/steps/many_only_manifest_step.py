from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.manifest.many_only_manifest import (
    MANIFEST_METADATA_KEY,
    build_many_only_manifest,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_state import (
    ManyOnlyCodegenCreationState,
)


class ManyOnlyManifestStep(CodegenCreationFamilyStep):
    """
    Manifest build step for the many_only family.

    Purpose:
        Convert many_only model/plan truth into the family's marshal-safe
        manifest before any executor work happens, and resolve the live root
        spell for the lazy-door step.

    Contract:
        - Publishes the manifest onto family-local state and mirrors it into
          `SpellCodegenCreation.metadata` under the shared manifest key for
          the cross-family cache envelope.
        - Resolves `state.root_spell` (the only live object later steps need).
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable many_only manifest step id.
        """
        return "many_only_manifest"

    def apply(
            self,
            state: ManyOnlyCodegenCreationState,
    ) -> None:
        """
        Build and publish the many_only manifest plus the live root spell.
        """
        manifest = build_many_only_manifest(
            spell_codegen_model=state.spell_codegen_model,
            spell_codegen_plan=state.spell_codegen_plan,
        )
        root_spell_id = manifest["root_spell_id"]
        runtime_shape = state.spell_codegen_model.spell_runtime_shape
        if runtime_shape is not None:
            record = runtime_shape.records_by_spell_id.get(root_spell_id)
            if record is not None:
                state.root_spell = record.spell
        if state.root_spell is None:
            for step in state.spell_codegen_plan.no_overrides_plan.steps:
                if step.spell.spell_index.selected_spell_id == root_spell_id:
                    state.root_spell = step.spell
                    break
        if state.root_spell is None:
            raise RuntimeError(
                "many_only manifest step could not resolve the root spell."
            )
        state.spell_codegen_creation.metadata[MANIFEST_METADATA_KEY] = manifest
