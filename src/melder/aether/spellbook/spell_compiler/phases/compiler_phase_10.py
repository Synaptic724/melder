from typing import TYPE_CHECKING, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner import (
    SpellCodegenPlanner,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class CompilerPhase10(Cleanable):
    """
    Live compiler phase-10 wrapper over `SpellCodegenPlanner`.

    Purpose:
        Make the live phase-10 surface explicitly planner-backed instead of
        continuing to expose the old patch-map phase implementation as if it
        were still the current path.

    Contract:
        - Owns one `SpellCodegenPlanner`.
        - Consumes the artifact after processor work completed.
        - Publishes `SpellCodegenPlan` onto the artifact as
          `_spell_codegen_plan`.
        - Uses the processor-owned model as its only planning input.
        - Does not emit runtime-ready creation artifacts.

    Threading:
        Reusable facade with no per-call mutable state beyond the owned
        planner facade.

    Lifecycle:
        Owns only the planner facade it delegates to.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_codegen_planner",
    ]

    def __init__(self) -> None:
        """
        Build the live phase-10 wrapper.
        """
        super().__init__()
        self._codegen_planner = SpellCodegenPlanner()

    def cleanup(self) -> None:
        """
        Deterministically release phase-10 owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._codegen_planner.cleanup()
        del self._codegen_planner

    def run(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Execute the planner-backed live phase 10.

        Purpose:
            Build the planner-owned execution-semantics artifact from the
            processor-owned model already stored on the compiler artifact.

        Contract:
            - Delegates directly to `SpellCodegenPlanner.build(...)`.
            - Treats the `spell` parameter as compatibility-only for the
              current public phase signature.

        Args:
            spell:
                Legacy phase argument retained so the public compiler method
                shape stays stable while this wrapper substitutes the live
                implementation.
            artifact:
                Compiler artifact receiving `SpellCodegenPlan`.

        Returns:
            None.
        """
        _ = spell
        self._codegen_planner.build(artifact)
