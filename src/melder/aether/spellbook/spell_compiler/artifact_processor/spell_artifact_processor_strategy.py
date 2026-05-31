from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
        SpellCodegenModel,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class SpellArtifactProcessorStrategy(ABC):
    """
    One artifact-processing strategy contract.

    Purpose:
        Define the execution seam for processor strategies that fit sections of
        `SpellCodegenModel` from upstream compiler truth.

    Contract:
        - Strategies run inside `SpellArtifactProcessor`.
        - Strategies may read `Spell` and `SpellCompilerArtifact`.
        - Strategies should write directly onto the supplied
          `SpellCodegenModel`.
        - Strategies may read analyzer-owned or legacy compiler truth from
          `SpellCompilerArtifact`.
        - Strategies must not generate final planner outputs.

    Ownership:
        - Strategy instances are processor helper objects only.
        - They do not own spell/runtime/compiler artifacts.

    Lifecycle:
        - Expected to be reusable across many spells.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ()

    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this processor strategy.

        Purpose:
            Provide one deterministic provenance label for later diagnostics,
            plan generation, and benchmark comparison.

        Contract:
            - Identifier must be stable for a given concrete strategy.
            - Identifier must be safe to persist into artifact-owned metadata.

        Returns:
            str:
                Stable strategy id used in processor diagnostics and plan
                provenance.
        """
        raise NotImplementedError

    @abstractmethod
    def process(
            self,
            spell: Spell,
            artifact: SpellCompilerArtifact,
            model: SpellCodegenModel,
    ) -> None:
        """
        Build or refine one concrete processor-owned artifact slice.

        Purpose:
            Let one concrete strategy consume current compiler truth and fit
            one bounded model section before planner work begins.

        Contract:
            - Reads from the supplied spell and artifact only.
            - Writes only the model section and compatibility fields owned by
              this strategy.
            - Must not generate final planner outputs directly.

        Args:
            spell:
                Spell whose compiler state is being processed.
            artifact:
                Compiler artifact supplying analyzer-owned or legacy compiler
                truth.
            model:
                Processor-owned codegen model being fitted by this strategy.

        Returns:
            None.
        """
        raise NotImplementedError
