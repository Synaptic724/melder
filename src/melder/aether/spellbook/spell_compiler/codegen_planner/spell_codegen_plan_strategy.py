from abc import ABC, abstractmethod
from typing import ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_state import (
    SpellArtifactProcessorState,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class SpellCodegenPlanStrategy(ABC):
    """
    One Phase 12 codegen-plan shaping strategy contract.

    Purpose:
        Define the seam where future plan strategies will transform assessed
        processor state into tighter `SpellCodegenPlan` variants.

    Contract:
        - Strategies operate after artifact processing has completed.
        - Strategies may replace the incoming plan object with a richer plan,
          but they must preserve compiler-owned ownership.
        - Concrete strategies are intentionally absent from this scaffold slice.

    Ownership:
        - Strategy instances are Phase 12 helper objects only.
        - They do not own spell/runtime/compiler artifacts.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ()

    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this plan strategy.

        Purpose:
            Provide one deterministic provenance label for plan-shaping
            diagnostics and later benchmark comparison.

        Contract:
            - Identifier must be stable for a given concrete strategy.

        Returns:
            str:
                Stable strategy id used in Phase 12 plan provenance.
        """
        raise NotImplementedError

    @abstractmethod
    def apply(
            self,
            state: SpellArtifactProcessorState,
            plan: SpellCodegenPlan,
    ) -> SpellCodegenPlan:
        """
        Apply this strategy to the current Phase 12 plan.

        Purpose:
            Let one concrete plan strategy refine or replace the current plan
            after artifact processing has completed.

        Contract:
            - Reads from the assessed processor state.
            - Returns the resulting compiler-owned plan object.
            - Must preserve compiler-owned ownership and not mutate borrowed
              compiler/runtime artifacts directly.

        Args:
            state:
                Assessed Phase 12 processor state.
            plan:
                Current compiler-owned codegen plan.

        Returns:
            SpellCodegenPlan:
                The resulting plan after this strategy is applied.
        """
        raise NotImplementedError
