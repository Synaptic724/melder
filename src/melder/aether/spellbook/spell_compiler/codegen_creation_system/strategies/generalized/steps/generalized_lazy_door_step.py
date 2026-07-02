from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_manifest_state import (
    GeneralizedManifestState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_binding_resolver import (
    PlanBindingResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.hydration.generalized_hydrator import (
    build_lazy_creation_executors,
)


class GeneralizedLazyDoorStep(CodegenCreationFamilyStep):
    """
    Lazy-door publication step for the generalized family.

    Purpose:
        Publish both runtime doors WITHOUT hydrating anything at phase-11
        time. Conjure-time phase-11 cost for this family is the manifest step
        only; the doors published here are cold closures over
        (manifest, root spell) that hydrate once on the first meld call and
        then swap the hot executors into the published `CreationContext`.

    Contract:
        - No spell-lookup, step hydration, source emission, compile, exec, or
          door-template work happens here.
        - The only live object touched is the root spell reference, resolved
          from plan/runtime-shape truth.
        - Hydration at first meld runs the exact same assembly program the
          cache-load path runs (`hydrate_creation_executors` via
          `SpellbookBindingResolver`).
        - Code-object fields stay `None`; this family's cache currency is the
          manifest, not compiled code objects.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable lazy-door step id.
        """
        return "generalized_lazy_doors"

    def apply(
            self,
            state: GeneralizedManifestState,
    ) -> None:
        """
        Publish cold doors and metadata parity keys from manifest truth.
        """
        manifest = state.manifest
        if manifest is None:
            raise RuntimeError(
                "generalized lazy-door step requires a built manifest."
            )
        resolver = PlanBindingResolver(
            spell_codegen_model=state.spell_codegen_model,
            spell_codegen_plan=state.spell_codegen_plan,
        )
        root_spell = resolver.resolve_spell(manifest["root_spell_id"])
        resolver.cleanup()

        (
            cold_no_overrides_door,
            cold_no_overrides_instance_door,
            cold_overrides_door,
        ) = build_lazy_creation_executors(
            manifest=manifest,
            spell=root_spell,
        )

        spell_codegen_creation = state.spell_codegen_creation
        spell_codegen_creation.no_overrides_executor = cold_no_overrides_door
        spell_codegen_creation.no_overrides_instance_executor = (
            cold_no_overrides_instance_door
        )
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
        metadata["no_overrides_fast_transient_available"] = (
            no_overrides_payload["transient_schema"] is not None
        )
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
