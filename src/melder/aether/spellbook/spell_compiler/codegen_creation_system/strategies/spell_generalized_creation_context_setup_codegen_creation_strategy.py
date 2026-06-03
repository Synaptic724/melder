from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.spell_codegen_strategy import (
    SpellCodegenStrategy,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class SpellGeneralizedCreationContextSetupCodegenCreationStrategy(
    SpellCodegenStrategy
):
    """
    Generalized creation-context setup creation strategy.

    Purpose:
        Port the shared spell-static `CreationContextBuilder` inputs that do
        not belong to a single execution lane:
        `resolve_route_key` and `fast_transient_no_overrides_enabled`.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable setup strategy id.
        """
        return "generalized_creation_context_setup_codegen_creation"

    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Populate the shared top-level creation-context setup fields.

        Contract:
            - Derives `resolve_route_key` from processor-owned model truth.
            - Derives `fast_transient_no_overrides_enabled` from the
              no-overrides lane plan plus the resolved route key.
            - Does not populate lane payloads directly.
        """
        route_key = self._resolve_route_key(spell_codegen_model)
        spell_codegen_creation.resolve_route_key = route_key

        no_overrides_plan = spell_codegen_plan.no_overrides_plan
        fast_transient_no_overrides_enabled = False
        if no_overrides_plan is not None:
            fast_transient_no_overrides_enabled = (
                route_key == "many"
                and no_overrides_plan.fast_transient_plan is not None
            )
        spell_codegen_creation.fast_transient_no_overrides_enabled = (
            fast_transient_no_overrides_enabled
        )
        spell_codegen_creation.metadata["resolve_route_key"] = route_key
        spell_codegen_creation.metadata[
            "fast_transient_no_overrides_enabled"
        ] = fast_transient_no_overrides_enabled

    @staticmethod
    def _resolve_route_key(
            spell_codegen_model: SpellCodegenModel,
    ) -> str:
        """
        Resolve the current creation-context route key from model truth.

        Contract:
            - `build_kind == "existing_creation"` wins first.
            - Otherwise uses the processor-owned `route_family` directly.
            - Raises when the current model route family is unknown.
        """
        if spell_codegen_model.build_kind == "existing_creation":
            return "existing_creation"

        route_family = spell_codegen_model.route_family
        if route_family in (
                "spellspace",
                "unique_per_conduit",
                "many",
                "shared",
        ):
            return route_family

        raise RuntimeError(
            "SpellCodegenModel route_family is not ready for creation-context "
            f"setup: {route_family!r}."
        )
