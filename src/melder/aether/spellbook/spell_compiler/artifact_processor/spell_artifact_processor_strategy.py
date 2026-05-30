from abc import ABC, abstractmethod
from typing import ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_state import (
    SpellArtifactProcessorState,
)


class SpellArtifactProcessorStrategy(ABC):
    """
    One Phase 12 artifact-processing strategy contract.

    Purpose:
        Define the execution seam for processor strategies that examine the
        full Phase 12 state and record assessments without generating code.

    Contract:
        - Strategies run inside `SpellArtifactProcessor`.
        - Strategies may read any part of the processor state.
        - Strategies should write only to `state.assessment` and
          `state.applied_strategy_ids`, not mutate borrowed compiler/runtime
          artifacts.
        - Concrete strategies are intentionally absent from this scaffold slice.

    Ownership:
        - Strategy instances are Phase 12 helper objects only.
        - They do not own spell/runtime/compiler artifacts.

    Lifecycle:
        - Expected to be reusable across many spells when future concrete
          strategies are added.
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
                Stable strategy id used in Phase 12 diagnostics and plan
                provenance.
        """
        raise NotImplementedError

    @abstractmethod
    def process(
            self,
            state: SpellArtifactProcessorState,
    ) -> None:
        """
        Examine the current processor state and record strategy output.

        Purpose:
            Let one concrete strategy contribute a specific assessment or
            classification result into the shared Phase 12 state.

        Contract:
            - Reads from the supplied state only.
            - Records outputs on the mutable state assessment surface.
            - Must not mutate borrowed runtime/compiler artifacts directly.

        Args:
            state:
                Phase 12 processor state being examined.

        Returns:
            None.
        """
        raise NotImplementedError
