from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

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
        - Concrete strategies stay narrow and composable so additional
          analysis groups can be added later without turning the analyzer back
          into a monolith.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ()

    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this analyzer strategy.

        Purpose:
            Give one stable name to the strategy for diagnostics, builder
            registration, benchmark output, and migration auditing.

        Contract:
            - Must be constant for the strategy type.
            - Must not depend on spell-local runtime values.

        Returns:
            str:
                Stable analyzer-strategy id for diagnostics and provenance.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Analyze the current spell/artifact pair and enrich the artifact.

        Purpose:
            Let one concrete analyzer strategy inspect current spell/compiler
            truth and add one bounded family of analysis artifacts back onto
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
