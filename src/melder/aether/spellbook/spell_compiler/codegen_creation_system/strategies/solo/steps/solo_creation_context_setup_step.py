from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state import (
    SoloCodegenCreationState,
)


class SoloCreationContextSetupStep(CodegenCreationFamilyStep):
    """
    Solo family setup step.

    Purpose:
        Resolve the single visible root spell plus its route-family facts so
        later solo steps can compile exact root-only runtime doors.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable solo setup step id.
        """
        return "solo_creation_context_setup"

    def apply(
            self,
            state: SoloCodegenCreationState,
    ) -> None:
        """
        Populate solo route/setup facts on family-local state.
        """
        spell_codegen_model = state.spell_codegen_model
        spell_runtime_shape = spell_codegen_model.spell_runtime_shape
        root_spell_id = self._resolve_root_spell_id(spell_codegen_model)
        runtime_record = spell_runtime_shape.records_by_spell_id[root_spell_id]

        route_key = self._resolve_route_key(spell_codegen_model)
        fast_transient_no_overrides_enabled = (
            route_key == "many"
            and not runtime_record.has_disposal_methods
        )

        state.root_spell = runtime_record.spell
        state.root_spell_id = root_spell_id
        state.resolve_route_key = route_key
        state.fast_transient_no_overrides_enabled = (
            fast_transient_no_overrides_enabled
        )

    @staticmethod
    def _resolve_root_spell_id(
            spell_codegen_model: object,
    ) -> str:
        """
        Resolve the root spell id for the solo family.
        """
        graph_shape = spell_codegen_model.graph_shape
        if graph_shape is not None:
            return graph_shape.root_spell_id
        return next(
            iter(spell_codegen_model.spell_runtime_shape.records_by_spell_id.keys())
        )

    @staticmethod
    def _resolve_route_key(
            spell_codegen_model: object,
    ) -> str:
        """
        Resolve the current creation-context route key from model truth.
        """
        if spell_codegen_model.build_kind == "existing_creation":
            return "existing_creation"
        return spell_codegen_model.route_family
