from typing import TYPE_CHECKING, Optional, Sequence, Tuple

from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellAnalyzer:
    """
    Compiler-side spell analyzer orchestrator.

    Purpose:
        Provide the post-phase-7 analysis seam that enriches
        `SpellCompilerArtifact` with deeper planning artifacts before later
        planning stages consume them.

    Contract:
        - Consumes `Spell` plus the existing `SpellCompilerArtifact`.
        - Does not choose or emit the final codegen plan.
        - Runs the configured analyzer strategies in deterministic order.
        - Expects strategies to add or update compiler-owned analysis artifacts
          on `SpellCompilerArtifact`.

    Ownership:
        - Owns no runtime/compiler artifacts.
        - Owns only the ordered analyzer-strategy registry.

    Lifecycle:
        - Reusable across many spells.
        - Safe to construct with an empty strategy list while the analyzer lane
          is being scaffolded.
    """

    __slots__ = [
        "_strategies",
    ]

    def __init__(
            self,
            *,
            strategies: Optional[Sequence[SpellAnalyzerStrategy]] = None,
    ) -> None:
        """
        Build one analyzer with an ordered strategy registry.

        Args:
            strategies:
                Optional ordered analyzer strategies to run during
                `analyze(...)`.
        """
        if strategies is None:
            self._strategies: Tuple[SpellAnalyzerStrategy, ...] = ()
        else:
            self._strategies = tuple(strategies)

    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Run analyzer strategies against the current spell/artifact pair.

        Purpose:
            Give strategies a clean place to inspect the current spell and the
            already-built compiler artifacts from phases `1-7`, then add the
            deeper analysis artifacts needed for later planning work.

        Args:
            spell:
                Spell whose current compiler state is being analyzed.
            artifact:
                Compiler-owned artifact that already contains the upstream
                phase truth and will receive analyzer-produced artifacts.

        Returns:
            None.
        """
        artifact.check_cleaned()
        for strategy in self._strategies:
            strategy.analyze(spell, artifact)
