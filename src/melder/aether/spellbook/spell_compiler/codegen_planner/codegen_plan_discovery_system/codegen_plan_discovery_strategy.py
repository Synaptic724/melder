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
        - Discovery strategies may narrow the set of concrete codegen styles
          that phase 11 is allowed to consider, but they do not choose the
          final style themselves.
        - Returning `None` means the strategy declines the model.
        - Returning `CodegenPlanDiscovery` means discovery should stop and use
          that result.

    Subsystem Context:
        The base of the `codegen_plan_discovery_system/strategies` family; instances
        register into `CodegenPlanDiscoveryStrategyBuilder`.

    System Context:
        Phase 10 (codegen planning) discovery of the conjure pipeline.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. ABC for phase-10 discovery strategies: strategy_id + "
        "discover(SpellCodegenModel) -> Optional[CodegenPlanDiscovery]. Reads the model only; "
        "return None to decline or a discovery to claim it. Chooses a planning family, not the "
        "final style."
    )
    __slots__ = ()

    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """
        Return the stable identifier for this discovery strategy.

        Returns:
            str: Registry key this strategy is registered and selected by.
        """
        raise NotImplementedError

    @abstractmethod
    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
    ) -> Optional[CodegenPlanDiscovery]:
        """
        Inspect the model and optionally claim it for a planning family.

        Contract:
            Reads only the processor-owned model; builds no planner artifacts.
            Per the class Contract, return None to decline, or a
            `CodegenPlanDiscovery` to stop discovery and use that result (it may
            narrow the concrete codegen styles phase 11 considers, but does not
            choose the final style).

        Args:
            spell_codegen_model:
                Processor-owned model for the current compile.

        Returns:
            Optional[CodegenPlanDiscovery]:
                The claim result, or None when this strategy declines the model.
        """
        raise NotImplementedError
