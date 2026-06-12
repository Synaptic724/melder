from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.generalized_cache_codegen_creation_state import (
    GeneralizedCacheCodegenCreationState,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.hydration.generalized_cache_binding_resolver import (
    PlanBindingResolver,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized_cache.hydration.generalized_cache_hydrator import (
    hydrate_creation_executors,
)


class GeneralizedCacheHydrateStep(CodegenCreationFamilyStep):
    """
    Executor hydration step for the generalized_cache family.

    Purpose:
        Build both final runtime doors from the manifest through the family's
        single hydrator, using the live plan-backed binding resolver.

    Contract:
        - Consumes only `state.manifest` plus model/plan identity through the
          resolver. Never reads plan steps directly, so the live build path
          exercises exactly the assembly program cache loads will use.
        - Publishes the two final doors, both code objects, and the metadata
          parity keys the generalized family publishes.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable hydration step id.
        """
        return "generalized_cache_hydrate"

    def apply(
            self,
            state: GeneralizedCacheCodegenCreationState,
    ) -> None:
        """
        Hydrate and publish both runtime doors from manifest truth.
        """
        manifest = state.manifest
        if manifest is None:
            raise RuntimeError(
                "generalized_cache hydrate step requires a built manifest."
            )
        resolver = PlanBindingResolver(
            spell_codegen_model=state.spell_codegen_model,
            spell_codegen_plan=state.spell_codegen_plan,
        )
        hydrated = hydrate_creation_executors(
            manifest=manifest,
            resolver=resolver,
        )
        state.hydrated_executors = hydrated

        spell_codegen_creation = state.spell_codegen_creation
        spell_codegen_creation.no_overrides_executor = (
            hydrated.no_overrides_executor
        )
        spell_codegen_creation.overrides_executor = hydrated.overrides_executor
        spell_codegen_creation.no_overrides_code_object = (
            hydrated.no_overrides_code_object
        )
        spell_codegen_creation.overrides_code_object = (
            hydrated.overrides_code_object
        )

        no_overrides_payload = manifest["no_overrides"]
        overrides_payload = manifest["overrides"]
        metadata = spell_codegen_creation.metadata
        metadata["no_overrides_lane_id"] = no_overrides_payload["lane_id"]
        metadata["no_overrides_root_spell_id"] = (
            no_overrides_payload["root_spell_id"]
        )
        metadata["no_overrides_step_count"] = len(
            no_overrides_payload["steps_rows"]
        )
        metadata["no_overrides_fast_transient_available"] = (
            hydrated.fast_transient_no_overrides
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
