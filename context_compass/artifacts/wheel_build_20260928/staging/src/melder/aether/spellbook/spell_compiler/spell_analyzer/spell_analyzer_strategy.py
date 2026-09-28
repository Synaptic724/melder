from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Optional


if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellAnalyzerStrategy(ABC):
    """
    One spell-analyzer strategy contract.

    Purpose:
        Define the execution seam for analysis strategies that inspect the
        current `Spell` plus its upstream compiler artifact state and then add
        new analysis artifacts back onto `SpellCompilerArtifact`.

    Contract:
        - Strategies run inside `SpellAnalyzer`.
        - Strategies may read both `Spell` and `SpellCompilerArtifact`.
        - Strategies should add or update compiler-owned analysis artifacts on
          `SpellCompilerArtifact`.
        - Strategies do not choose or emit the final codegen plan.
        - Strategies are expected to be registered into one named analysis
          group on `SpellAnalyzerBuilder`, then invoked through the matching
          explicit `SpellAnalyzer` method.

    Ownership:
        - Strategy instances are compiler helper objects only.
        - They do not own spell/runtime/compiler artifacts.

    Design rule:
        - The builder is the registry holder.
        - The analyzer is the explicit method surface.
        - Concrete strategies stay narrow and composable, so additional
          analysis groups can be added later without turning the analyzer back
          into a monolith.

    Registration:
        MELDER KERNEL. Analyzer strategies register into the builder and are never
        bound as spells.

    Subsystem Context:
        The base of the `spell_analyzer/strategies` family: `SpellAnalyzerStrategyBuilder`
        registers instances by `strategy_id` and `SpellAnalyzer` invokes them.

    System Context:
        Phase 8 (occurrence analysis) of the conjure pipeline.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. ABC contract for analyzer strategies: strategy_id + analyze(spell,
        artifact, analysis_pass_cache). Reads Spell + SpellCompilerArtifact and writes its own
        analysis-artifact family back; never chooses the codegen plan.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this analyzer strategy.

        Purpose:
            Give the analyzer builder one deterministic registry key that the
            analyzer facade can reference explicitly in its strategy chains.

        Contract:
            - Identifier must be stable for a given concrete strategy.
            - Identifier must be safe to persist into analyzer diagnostics.

        Returns:
            str:
                Stable analyzer strategy id.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            analysis_pass_cache: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Analyze the current spell/artifact pair and enrich the artifact.

        `analysis_pass_cache`, when supplied, is one pass-scoped memo dict
        shared by every analyzer unit in the current pass so strategies can
        reuse pass-invariant artifacts instead of rebuilding them per spell.
        It dies with the pass units; no invalidation protocol exists.

        Purpose:
            Let one concrete analyzer strategy inspect the current spell / compiler truth and add one bounded family of analysis artifacts back onto
            `SpellCompilerArtifact`.

        Contract:
            - Reads from `spell` and `artifact`.
            - Writes only the artifact family owned by this strategy.
            - Leaves model distillation and final plan choice to later stages.

        Args:
            spell:
                Spell whose current compiler state is being analyzed.
            artifact:
                Existing compiler artifact that receives analyzer-produced
                artifacts.

        Returns:
            None.
        """
        raise NotImplementedError
