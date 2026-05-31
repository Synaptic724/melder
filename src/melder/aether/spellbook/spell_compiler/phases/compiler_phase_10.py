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
        - Publishes `SpellCodegenPlan` onto the artifact.
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
