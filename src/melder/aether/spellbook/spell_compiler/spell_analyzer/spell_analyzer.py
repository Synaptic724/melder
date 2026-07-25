from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional, Tuple

from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy_builder import (
    SpellAnalyzerStrategyBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellAnalyzer(Cleanable):
    """
    Compiler-side spell analyzer orchestrator.

    Purpose:
        Provide the post-phase-7 analysis seam that enriches
        `SpellCompilerArtifact` with deeper planning artifacts before later
        planning stages consume them.

    Contract:
        - Consumes `Spell` plus the existing `SpellCompilerArtifact`.
        - Does not choose or emit the final codegen plan.
        - Exposes explicit analysis entrypoints by strategy chain.
        - Runs the configured analyzer strategies in deterministic order inside
          each exposed analysis method by resolving them from the strategy
          builder.
        - Expects strategies to add or update compiler-owned analysis artifacts
          on `SpellCompilerArtifact`.

    Ownership:
        - Owns no runtime/compiler artifacts.
        - Owns only the analyzer strategy builder.

    Lifecycle:
        - Reusable across many spells.
        - Safe to construct with an empty strategy registry while the analyzer lane
          is being scaffolded.

    Registration:
        MELDER KERNEL - guarded. A compiler orchestrator; not user-bindable.

    Subsystem Context:
        The orchestrator of the `spell_analyzer` package: it owns a
        `SpellAnalyzerStrategyBuilder` and dispatches named strategy chains over a
        `Spell` + `SpellCompilerArtifact` pair.

    System Context:
        Phase 8 (occurrence analysis) of the conjure pipeline - the post-phase-7 seam
        that enriches `SpellCompilerArtifact` before the planning stages run.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-8 analyzer orchestrator: runs registered analyzer strategies "
        "(resolved from its owned SpellAnalyzerStrategyBuilder) over a Spell + "
        "SpellCompilerArtifact via analyze_occurrence. Enriches the artifact; does not choose the "
        "codegen plan."
    )
    __slots__ = Cleanable.__slots__ + [
        "_strategy_builder",
    ]

    def __init__(
            self,
    ) -> None:
        """
        Build one analyzer with a strategy builder.

        Purpose:
            Keep the analyzer itself small and make the strategy builder the
            owner of the named strategy registry.

        Contract:
            - Analyzer owns its strategy builder directly.
            - The analyzer does not clone strategy objects; it consumes them
              from the owned builder.
        """
        super().__init__()
        self._strategy_builder = SpellAnalyzerStrategyBuilder()

    def cleanup(self) -> None:
        """
        Deterministically release analyzer-owned state.

        Contract:
            - Idempotent.
            - Cleans the owned strategy builder directly.
            - Drops the analyzer's only owned reference so later use fails
              honestly through `check_cleaned()`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategy_builder.cleanup()
        del self._strategy_builder

    def analyze_occurrence(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            analysis_pass_cache: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Run all registered occurrence-analysis strategies.

        Purpose:
            Expose the occurrence-analysis entrypoint directly on the analyzer
            so callers do not need to know how the individual occurrence
            strategies are looked up or chained.

        Contract:
            - Runs the registered occurrence strategy chain in explicit order.
            - Validates that the target artifact is still live before dispatch.

        Args:
            spell:
                Spell whose occurrence/runtime-shape artifacts should be
                analyzed.
            artifact:
                Compiler-owned artifact that already contains the upstream
                phase truth and will receive analyzer-produced occurrence
                artifacts.

        Returns:
            None.
        """
        self._run_strategy_chain(
            strategy_ids=(
                "spell_occurrence_graph_analyzer",
            ),
            spell=spell,
            artifact=artifact,
            analysis_pass_cache=analysis_pass_cache,
        )

    def _run_strategy_chain(
            self,
            *,
            strategy_ids: Tuple[str, ...],
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            analysis_pass_cache: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Run one explicit analyzer strategy chain against the spell/artifact pair.

        Purpose:
            Centralize the common analyzer dispatch semantics so each exposed
            analysis method can stay small and explicit while the builder keeps
            the default strategy registry indexed by name.

        Contract:
            - Validates that the artifact is live before strategy dispatch.
            - Resolves strategies by name from the stored registry.
            - Missing strategy names are a hard contract error.
        """
        artifact.check_cleaned()
        strategies = self._strategy_builder.get_strategies(strategy_ids)
        for strategy in strategies:
            strategy.analyze(spell, artifact, analysis_pass_cache=analysis_pass_cache)
