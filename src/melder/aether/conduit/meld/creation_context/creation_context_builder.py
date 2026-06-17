from typing import TYPE_CHECKING, Any, Callable, Optional

from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
)
from melder.utilities.custom_exceptions.meld_execution_error import (
    MeldExecutionError,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.utilities.synchronization.creation_gate import CreationGate


class CreationContextBuilder:
    """
    Build spell-bound `CreationContext` objects from phase-11 creation inputs.

    Contract:
        - Constructed spells require `spell_codegen_creation`.
        - Existing-creation spells may synthesize their local runtime doors
          without a compiler artifact.
        - `CreationContext` receives only the final 2 tuple-return runtime
          executors.
    """

    __slots__ = ()

    @staticmethod
    def build(
            spell: "Spell",
            *,
            dynamic_environment: bool = False,
            creation_gate: Optional["CreationGate"] = None,
            creation_gate_index_id: Optional[str] = None,
    ) -> CreationContext:
        """
        Build one spell-bound CreationContext.
        """
        artifact = spell._compiler_artifact
        spell_codegen_creation = artifact._spell_codegen_creation
        if spell.is_existing_creation:
            no_overrides_executor = CreationContextBuilder._build_existing_creation_no_overrides_executor(
                spell
            )
            overrides_executor = CreationContextBuilder._build_existing_creation_overrides_executor(
                spell
            )
        else:
            if spell_codegen_creation is None:
                raise RuntimeError(
                    "Cannot build CreationContext before spell_codegen_creation exists. "
                    "Run analyzer -> processor -> planner -> codegen creation first."
                )
            no_overrides_executor = spell_codegen_creation.no_overrides_executor
            overrides_executor = spell_codegen_creation.overrides_executor
            if no_overrides_executor is None:
                raise RuntimeError(
                    "SpellCodegenCreation did not populate no_overrides_executor."
                )
            if overrides_executor is None:
                raise RuntimeError(
                    "SpellCodegenCreation did not populate overrides_executor."
                )

        return CreationContext(
            spell=spell,
            dynamic_environment=dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=creation_gate_index_id,
            no_overrides_executor=no_overrides_executor,
            overrides_executor=overrides_executor,
        )

    @staticmethod
    def _build_existing_creation_no_overrides_executor(
            spell: "Spell",
    ) -> Callable[..., Any]:
        """
        Build the final no-overrides executor for an existing-creation spell.
        """
        def execute(
                caller_creations: Any,
                owner_creations: Any = None,
                caller_creations_lock_held: bool = False,
        ) -> tuple[Any, bool]:
            _ = caller_creations
            _ = owner_creations
            _ = caller_creations_lock_held
            instance = spell.user_created_object
            if instance is None:
                raise RuntimeError(
                    "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                    f"(spell_id={spell.spell_id})."
                )
            return instance, False

        return execute

    @staticmethod
    def _build_existing_creation_overrides_executor(
            spell: "Spell",
    ) -> Callable[..., Any]:
        """
        Build the final overrides executor for an existing-creation spell.
        """
        def execute(
                caller_creations: Any,
                overrides: Optional[dict[str, Any]],
                caller_creations_lock_held: bool = False,
        ) -> tuple[Any, bool]:
            _ = caller_creations
            _ = caller_creations_lock_held
            if overrides is not None:
                raise MeldExecutionError(
                    spell_id=spell.spell_index.selected_spell_id,
                    spell_name=spell.spell_name,
                    message=(
                        "Overrides were supplied for a spell instance that already exists. "
                        "Shared instances cannot be overridden after creation."
                    ),
                )
            instance = spell.user_created_object
            if instance is None:
                raise RuntimeError(
                    "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                    f"(spell_id={spell.spell_id})."
                )
            return instance, False

        return execute
