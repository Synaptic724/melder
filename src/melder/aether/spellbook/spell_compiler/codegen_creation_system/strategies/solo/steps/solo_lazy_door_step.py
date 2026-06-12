from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    MANIFEST_METADATA_KEY,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.hydration.solo_hydrator import (
    build_solo_lazy_creation_executors,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state import (
    SoloCodegenCreationState,
)


class SoloLazyDoorStep(CodegenCreationFamilyStep):
    """
    Lazy-door publication step for the solo family.

    Purpose:
        Publish both solo runtime doors WITHOUT compiling anything at
        phase-11 time. The doors are cold closures over (manifest, root
        spell) that compile the two root-only solo executors once at first
        meld and swap the hot doors into the published `CreationContext`.

    Contract:
        - No compile, exec, or door-template work happens here.
        - Code-object fields stay `None`; the family's cache currency is the
          manifest, not compiled code objects.
        - Metadata parity keys mirror the legacy solo steps.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable solo lazy-door step id.
        """
        return "solo_lazy_doors"

    def apply(
            self,
            state: SoloCodegenCreationState,
    ) -> None:
        """
        Publish cold doors and metadata parity keys from manifest truth.
        """
        spell_codegen_creation = state.spell_codegen_creation
        manifest = spell_codegen_creation.metadata.get(MANIFEST_METADATA_KEY)
        if manifest is None:
            raise RuntimeError(
                "solo lazy-door step requires a built manifest."
            )
        root_spell = state.root_spell
        if root_spell is None:
            raise RuntimeError("solo lazy-door step requires root_spell.")

        cold_no_overrides_door, cold_overrides_door = (
            build_solo_lazy_creation_executors(
                manifest=manifest,
                spell=root_spell,
            )
        )

        spell_codegen_creation.no_overrides_executor = cold_no_overrides_door
        spell_codegen_creation.overrides_executor = cold_overrides_door
        spell_codegen_creation.no_overrides_code_object = None
        spell_codegen_creation.overrides_code_object = None

        signature = (
            "solo",
            manifest["solo_emit_key"],
            int(manifest["fast_transient_no_overrides_enabled"]),
            int(root_spell.has_disposal_methods),
            int(root_spell.is_existing_creation),
        )
        metadata = spell_codegen_creation.metadata
        metadata["hydration"] = "lazy_first_meld"
        metadata["no_overrides_lane_id"] = manifest["no_overrides_lane_id"]
        metadata["no_overrides_root_spell_id"] = manifest["root_spell_id"]
        metadata["no_overrides_step_count"] = 1
        metadata["no_overrides_fast_transient_available"] = bool(
            manifest["fast_transient_no_overrides_enabled"]
        )
        metadata["no_overrides_executor_signature"] = signature
        metadata["_no_overrides_executor_signature"] = signature
        metadata["override_lane_id"] = manifest["override_lane_id"]
        metadata["override_root_spell_id"] = manifest["root_spell_id"]
        metadata["override_step_count"] = 1
        metadata["override_executor_signature"] = (
            "solo",
            manifest["solo_emit_key"],
            int(root_spell.has_disposal_methods),
            int(root_spell.is_existing_creation),
        )
        metadata["solo_emit_key"] = manifest["solo_emit_key"]
        metadata["route_key"] = manifest["route_key"]
