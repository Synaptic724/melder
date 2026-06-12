from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.manifest_creation_cache import (
    MANIFEST_METADATA_KEY,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.hydration.many_only_hydrator import (
    build_many_only_lazy_creation_executors,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.many_only_codegen_creation_state import (
    ManyOnlyCodegenCreationState,
)


class ManyOnlyLazyDoorStep(CodegenCreationFamilyStep):
    """
    Lazy-door publication step for the many_only family.

    Purpose:
        Publish both many_only runtime doors WITHOUT compiling anything at
        phase-11 time. The doors are cold closures over (manifest, root
        spell) that hydrate once at first meld and swap the hot doors into
        the published `CreationContext`.

    Contract:
        - No compile, exec, or door-template work happens here.
        - Code-object fields stay `None`; the family's cache currency is the
          manifest, not compiled code objects.
        - Metadata parity keys mirror the legacy many_only steps.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable many_only lazy-door step id.
        """
        return "many_only_lazy_doors"

    def apply(
            self,
            state: ManyOnlyCodegenCreationState,
    ) -> None:
        """
        Publish cold doors and metadata parity keys from manifest truth.
        """
        spell_codegen_creation = state.spell_codegen_creation
        manifest = spell_codegen_creation.metadata.get(MANIFEST_METADATA_KEY)
        if manifest is None:
            raise RuntimeError(
                "many_only lazy-door step requires a built manifest."
            )
        root_spell = state.root_spell
        if root_spell is None:
            raise RuntimeError("many_only lazy-door step requires root_spell.")

        cold_no_overrides_door, cold_overrides_door = (
            build_many_only_lazy_creation_executors(
                manifest=manifest,
                spell=root_spell,
            )
        )

        spell_codegen_creation.no_overrides_executor = cold_no_overrides_door
        spell_codegen_creation.overrides_executor = cold_overrides_door
        spell_codegen_creation.no_overrides_code_object = None
        spell_codegen_creation.overrides_code_object = None

        no_overrides_payload = manifest["no_overrides"]
        overrides_payload = manifest["overrides"]
        metadata = spell_codegen_creation.metadata
        metadata["hydration"] = "lazy_first_meld"
        metadata["no_overrides_lane_id"] = no_overrides_payload["lane_id"]
        metadata["no_overrides_root_spell_id"] = (
            no_overrides_payload["root_spell_id"]
        )
        metadata["no_overrides_step_count"] = len(
            no_overrides_payload["steps_rows"]
        )
        metadata["no_overrides_plan_kind"] = "many_only_no_overrides"
        metadata["no_overrides_executor_signature"] = (
            no_overrides_payload["executor_signature"]
        )
        metadata["_no_overrides_executor_signature"] = (
            no_overrides_payload["executor_signature"]
        )
        metadata["override_lane_id"] = overrides_payload["lane_id"]
        metadata["override_root_spell_id"] = overrides_payload["root_spell_id"]
        metadata["override_step_count"] = len(overrides_payload["plan_rows"])
        metadata["override_steps_rows_signature"] = (
            overrides_payload["plan_signature"][2]
        )
        metadata["route_key"] = manifest["route_key"]
