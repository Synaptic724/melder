from abc import ABC, abstractmethod
from typing import Optional

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery import (
    CodegenPlanDiscovery,
)


class CodegenPlanDiscoveryStrategy(ABC):
    """
    One phase-10 discovery strategy contract.

    Purpose:
        Define the seam where planner discovery strategies inspect the
        processor-owned model and optionally claim it.

    Contract:
        - Discovery strategies read only `SpellCodegenModel`.
        - Discovery strategies do not build planner artifacts directly.
        - Discovery strategies choose a planning family, not the final emitted
          runtime executors.
        - Returning `None` means the strategy declines the model.
        - Returning `CodegenPlanDiscovery` means discovery should stop and use
          that result.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this discovery strategy.
        """
        raise NotImplementedError

    @abstractmethod
    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
    ) -> Optional[CodegenPlanDiscovery]:
        """
        Inspect the model and optionally produce a planning-family result.
        """
        raise NotImplementedError
