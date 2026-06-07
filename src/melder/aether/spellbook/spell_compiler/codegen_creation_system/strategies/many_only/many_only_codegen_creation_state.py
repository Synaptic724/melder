from melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.generalized_codegen_creation_state import (
    GeneralizedCodegenCreationState,
)


class ManyOnlyCodegenCreationState(GeneralizedCodegenCreationState):
    """
    Family-local mutable state for the many-only creation strategy.

    Purpose:
        Give the many-only phase-11 family its own explicit state surface while
        it still reuses the common creation-step machinery and the current
        lane-plan data shape.
    """

    __slots__ = ()
