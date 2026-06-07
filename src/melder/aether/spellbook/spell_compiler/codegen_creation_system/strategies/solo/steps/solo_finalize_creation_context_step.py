from melder.aether.conduit.meld.creation_context.creation_context_codegen import (
    compile_creation_context_hooks_no_overrides_executor,
    compile_creation_context_hooks_overrides_only_executor,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.shared_assets.codegen_creation_family_step import (
    CodegenCreationFamilyStep,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.solo_codegen_creation_state import (
    SoloCodegenCreationState,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)


class SoloFinalizeCreationContextStep(CodegenCreationFamilyStep):
    """
    Solo family final output step.

    Purpose:
        Finish the narrow `SpellCodegenCreation` output for the solo family
        after the solo-owned runtime executors are built.
    """

    __slots__ = ()

    @property
    def step_id(self) -> str:
        """
        Return the stable solo finalization step id.
        """
        return "solo_finalize_creation_context"

    def apply(
            self,
            state: SoloCodegenCreationState,
    ) -> None:
        """
        Publish the final solo runtime doors onto the output artifact.
        """
        resolve_route_key = state.resolve_route_key
        spell_codegen_creation = state.spell_codegen_creation
        root_spell = state.root_spell
        no_overrides_executor = state.no_overrides_executor
        overrides_executor = state.overrides_executor
        if root_spell is None:
            raise RuntimeError("Solo finalize requires root_spell.")
        if no_overrides_executor is None:
            raise RuntimeError("Solo finalize requires no_overrides_executor.")
        if overrides_executor is None:
            raise RuntimeError("Solo finalize requires overrides_executor.")

        spell_codegen_creation.no_overrides_executor = (
            compile_creation_context_hooks_no_overrides_executor(
                resolve_route_key=resolve_route_key,
                fast_transient_no_overrides_enabled=(
                    state.fast_transient_no_overrides_enabled
                ),
                spell=root_spell,
                spell_id=root_spell.spell_id,
                owner_creations=root_spell._owner_creations,
                no_overrides_executor=no_overrides_executor,
                spell_space_scope_error_type=SpellSpaceScopeError,
            )
        )
        spell_codegen_creation.overrides_executor = (
            compile_creation_context_hooks_overrides_only_executor(
                resolve_route_key=resolve_route_key,
                spell=root_spell,
                spell_id=root_spell.spell_id,
                owner_creations=root_spell._owner_creations,
                no_overrides_executor=no_overrides_executor,
                execute_with_overrides=overrides_executor,
                meld_execution_error_type=MeldExecutionError,
                spell_space_scope_error_type=SpellSpaceScopeError,
            )
        )
        spell_codegen_creation.no_overrides_code_object = (
            spell_codegen_creation.no_overrides_executor.__code__
        )
        spell_codegen_creation.overrides_code_object = (
            spell_codegen_creation.overrides_executor.__code__
        )
        spell_codegen_creation.metadata["solo_emit_key"] = state.solo_emit_key
        spell_codegen_creation.metadata["creation_context_strategy"] = (
            "solo_codegen_creation"
        )
