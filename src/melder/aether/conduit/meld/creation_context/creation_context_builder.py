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

    Owned State:
        None. `__slots__` is empty and every method is a `@staticmethod` - this
        is a namespaced pure builder, not an object with lifecycle.

    Threading:
        Stateless, therefore thread-safe by construction.

    Registration:
        MELDER KERNEL - guarded. Reached through `CreationContextFactory`;
        never user-instantiated and never bindable.

    Subsystem Context:
        The shape-decision layer between phase 11 and `CreationContext`.
        `CreationContextFactory` owns WHEN a context is built and the gate
        wiring; this class owns WHAT shape it takes. Keeping them apart is why
        the factory can stay lock-free - it never needs to know the difference
        between a constructed spell and an existing-creation spell.

    System Context:
        The existing-creation branch is the reason this class exists at all.
        A constructed spell has a phase 8-11 pipeline behind it and therefore a
        `spell_codegen_creation` to execute; an EXISTING-creation spell has no
        occurrence graph, no analyzer model, and no codegen payload, because
        the object already exists and was merely handed to Melder. It still
        needs a context, so this builder SYNTHESIZES its runtime doors locally
        instead of demanding a compiler artifact that will never exist.
        The refusal on the other branch is equally deliberate: a constructed
        spell with no `spell_codegen_creation` means the phases were skipped,
        and raising with the analyzer -> processor -> planner -> codegen
        ordering named is far more useful than letting a `None` executor
        surface as an obscure failure deep inside meld.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Build spell-bound `CreationContext` objects from phase-11 creation "
        "inputs. Melder kernel machinery: read it to understand the runtime, do not drive it "
        "directly."
    )

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

        Contract:
            Two shapes by spell kind: an EXISTING-creation spell synthesizes its
            three runtime executors locally (no compiler artifact required); a
            constructed spell pulls its no-overrides, no-overrides-instance, and
            overrides executors from `spell_codegen_creation` and refuses
            (raises) when that payload - or any of the three executors - is
            absent, since that means the analyzer -> processor -> planner ->
            codegen pipeline was skipped. The resulting context receives only
            the final tuple-return executors plus the gate wiring.

        Args:
            spell:
                Spell to bind the context to.
            dynamic_environment:
                When True, build the context for a dynamic meld environment.
            creation_gate:
                Optional creation gate the context coordinates through.
            creation_gate_index_id:
                Optional index id scoping the creation gate.

        Returns:
            CreationContext: The spell-bound creation context.

        Raises:
            RuntimeError: For a constructed spell, if `spell_codegen_creation`
                or any required executor was not populated.
        """
        artifact = spell._compiler_artifact
        spell_codegen_creation = artifact._spell_codegen_creation
        if spell.is_existing_creation:
            no_overrides_executor = CreationContextBuilder._build_existing_creation_no_overrides_executor(
                spell
            )
            no_overrides_instance_executor = (
                CreationContextBuilder
                ._build_existing_creation_instance_executor(spell)
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
            no_overrides_instance_executor = (
                spell_codegen_creation.no_overrides_instance_executor
            )
            overrides_executor = spell_codegen_creation.overrides_executor
            if no_overrides_instance_executor is None:
                raise RuntimeError(
                    "SpellCodegenCreation did not populate "
                    "no_overrides_instance_executor."
                )
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
            no_overrides_instance_executor=no_overrides_instance_executor,
            overrides_executor=overrides_executor,
        )

    @staticmethod
    def _build_existing_creation_instance_executor(
            spell: "Spell",
    ) -> Callable[..., Any]:
        """
        Build the instance-only no-overrides executor for an existing-creation
        spell.

        Contract:
            - `(meld) -> instance`; no `(instance, created)` tuple is built.
            - Same missing-object error as the tuple variant.
        """
        def execute(caller_creations: Any) -> Any:
            _ = caller_creations
            instance = spell.user_created_object
            if instance is None:
                raise RuntimeError(
                    "[MELD] EXISTING_CREATION spell has no `user_created_object` "
                    f"(spell_id={spell.spell_id})."
                )
            return instance

        return execute

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
