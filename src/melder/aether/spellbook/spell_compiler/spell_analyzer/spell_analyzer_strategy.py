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

    Ownership:
        - Strategy instances are compiler helper objects only.
        - They do not own spell/runtime/compiler artifacts.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ()

    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this analyzer strategy.

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
