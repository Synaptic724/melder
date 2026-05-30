from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spellbook import Spellbook
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class CompilerPhase12:
    """
    Compiler phase 12 strategy-selection placeholder.

    Purpose:
        Reserve the explicit compiler slot for the future execution
        strategy/right-sizing stage so the current backend-emitter phase can
        move to Phase 13 without leaving a numbering gap.

    Contract:
        - Slot-only phase surface with no explicit `__init__`.
        - Current behavior is a no-op placeholder.
        - Does not mutate spell, artifact, or runtime state in this rename
          slice.
    """

    __slots__ = ()

    def run(
            self,
            spellbook: "Spellbook",
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Phase 12 - strategy-selection placeholder.

        Purpose:
            Hold the future strategy/right-sizing slot without changing runtime
            behavior yet.

        Args:
            spellbook:
                Current spellbook compiler context.
            spell:
                Spell currently moving through compiler phases.
            artifact:
                Compiler artifact for the spell.

        Returns:
            None.
        """
        _ = spellbook
        _ = spell
        _ = artifact

