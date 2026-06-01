from typing import TYPE_CHECKING, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.spell_compiler.codegen_creation.codegen_creation_system import (
    CodegenCreationSystem,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spellbook import Spellbook


class CompilerPhase11(Cleanable):
    """
    Live compiler phase-11 wrapper over `CodegenCreationSystem`.

    Purpose:
        Make the live phase-11 surface explicitly codegen-creation-backed
        instead of continuing to expose the old execution-plan phase
        implementation as if it were still the current path.

    Contract:
        - Owns one `CodegenCreationSystem`.
        - Consumes the artifact after planner work completed.
        - Publishes `SpellCodegenCreation` onto the artifact as
          `_spell_codegen_creation`.
        - Produces the spell-static runtime handoff later consumed by
          `CreationContextBuilder`.
        - Does not execute runtime meld calls or per-call override
          specialization.

    Threading:
        Reusable facade with no per-call mutable state beyond the owned
        codegen-creation facade.

    Lifecycle:
        Owns only the codegen-creation facade it delegates to.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_codegen_creation_system",
    ]

    def __init__(self) -> None:
        """
        Build the live phase-11 wrapper.
        """
        super().__init__()
        self._codegen_creation_system = CodegenCreationSystem()

    def cleanup(self) -> None:
        """
        Deterministically release phase-11 owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._codegen_creation_system.cleanup()
        del self._codegen_creation_system

    def run(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            spellbook: "Spellbook",
    ) -> None:
        """
        Execute the codegen-creation-backed live phase 11.

        Purpose:
            Build the compiler-owned spell-static creation handoff from the
            already-fitted model and plan so runtime binders can consume one
            coherent artifact instead of rediscovering compiler packaging
            logic.

        Contract:
            - Delegates directly to `CodegenCreationSystem.build(...)`.
            - Treats `spell` and `spellbook` as compatibility-only parameters
              for the current public phase signature.

        Args:
            spell:
                Legacy phase argument retained so the compiler call signature
                stays stable while this wrapper substitutes the live
                implementation.
            artifact:
                Compiler artifact receiving `SpellCodegenCreation`.
            spellbook:
                Legacy phase argument retained so the compiler call signature
                stays stable while this wrapper substitutes the live
                implementation.

        Returns:
            None.
        """
        _ = spell
        _ = spellbook
        self._codegen_creation_system.build(artifact)
