from typing import TYPE_CHECKING, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor import (
    SpellArtifactProcessor,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class CompilerPhase9(Cleanable):
    """
    Live compiler phase-9 wrapper over `SpellArtifactProcessor`.

    Purpose:
        Make the live phase-9 surface explicitly processor-backed instead of
        continuing to expose the old injection-plan phase implementation as if
        it were still the current path.

    Contract:
        - Owns one `SpellArtifactProcessor`.
        - Consumes the spell/artifact pair.
        - Publishes `SpellCodegenModel` onto the artifact.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_artifact_processor",
    ]

    def __init__(self) -> None:
        """
        Build the live phase-9 wrapper.
        """
        super().__init__()
        self._artifact_processor = SpellArtifactProcessor()

    def cleanup(self) -> None:
        """
        Deterministically release phase-9 owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._artifact_processor.cleanup()
        del self._artifact_processor

    def run(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Execute the processor-backed live phase 9.

        Args:
            spell:
                Spell whose processor-owned model should be fitted.
            artifact:
                Compiler artifact receiving `SpellCodegenModel`.

        Returns:
            None.
        """
        self._artifact_processor.process(spell, artifact)
