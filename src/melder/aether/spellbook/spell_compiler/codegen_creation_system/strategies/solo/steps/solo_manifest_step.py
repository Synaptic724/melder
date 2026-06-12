from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.manifest.solo_manifest import (
    MANIFEST_METADATA_KEY,
    build_solo_manifest,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state import (
    SoloCodegenCreationState,
)


class SoloManifestStep(CodegenCreationFamilyStep):
    """
    Manifest build step for the solo family.

    Purpose:
        Convert solo model/plan truth into the family's marshal-safe manifest
        before any executor work happens, and resolve the live root spell for
        the lazy-door step.

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
        Return the stable solo manifest step id.
        """
        return "solo_manifest"

    def apply(
            self,
            state: SoloCodegenCreationState,
    ) -> None:
        """
        Build and publish the solo manifest plus live root-spell facts.
        """
        manifest = build_solo_manifest(
            spell_codegen_model=state.spell_codegen_model,
            spell_codegen_plan=state.spell_codegen_plan,
        )
        root_spell_id = manifest["root_spell_id"]
        runtime_record = (
            state.spell_codegen_model.spell_runtime_shape.records_by_spell_id[
                root_spell_id
            ]
        )

        state.root_spell = runtime_record.spell
        state.root_spell_id = root_spell_id
        state.resolve_route_key = manifest["route_key"]
        state.solo_emit_key = manifest["solo_emit_key"]
        state.fast_transient_no_overrides_enabled = bool(
            manifest["fast_transient_no_overrides_enabled"]
        )
        state.spell_codegen_creation.metadata[MANIFEST_METADATA_KEY] = manifest
