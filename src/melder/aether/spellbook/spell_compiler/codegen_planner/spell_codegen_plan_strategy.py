from abc import ABC, abstractmethod
from typing import ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class SpellCodegenPlanStrategy(ABC):
    """
    One codegen-plan shaping strategy contract.

    Purpose:
        Define the seam where future planner strategies will transform assessed
        processor state into the final planner-owned codegen plan output.

    Contract:
        - Strategies operate after artifact processing has completed.
        - Strategies mutate `SpellCodegenPlan` in place.
        - Concrete strategies are intentionally absent from this scaffold slice.

    Ownership:
        - Strategy instances are planner helper objects only.
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
                Stable strategy id used in plan provenance.
        """
        raise NotImplementedError

    @abstractmethod
    def apply(
            self,
            state: SpellCodegenModel,
            plan: SpellCodegenPlan,
    ) -> None:
        """
        Apply this strategy to the current planner-owned codegen plan.

        Purpose:
            Let one concrete plan strategy refine the current planner-owned
            codegen plan after artifact processing has completed.

        Contract:
            - Reads from the assessed processor state.
            - Mutates only the supplied planner-owned codegen plan.
            - Must not mutate borrowed compiler/runtime artifacts directly.

        Args:
            state:
                Assessed codegen model.
            plan:
                Current planner-owned codegen plan.

        Returns:
            None.
        """
        raise NotImplementedError
