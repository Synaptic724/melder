from abc import ABC, abstractmethod
from typing import Optional

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation_discovery_system.codegen_creation_discovery import (
    CodegenCreationDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class CodegenCreationDiscoveryStrategy(ABC):
    """
    One phase-11 discovery strategy contract.

    Purpose:
        Define the seam where codegen-creation discovery strategies inspect the
        current model/plan pair and optionally claim it.

    Contract:
        - Discovery strategies read only the current model and plan.
        - Discovery strategies do not build runtime artifacts directly.
        - Discovery strategies choose the concrete codegen style for the
          already-selected phase-10 plan family.
        - Discovery strategies may choose an ordered creation strategy chain,
          but they do not widen the final runtime contract beyond the two
          executor outputs.
        - Returning `None` means the strategy declines the pair.
        - Returning `CodegenCreationDiscovery` means discovery should stop and
          use that result.
    """

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
            spell_codegen_plan: SpellCodegenPlan,
    ) -> Optional[CodegenCreationDiscovery]:
        """
        Inspect the model/plan pair and optionally claim it for a codegen style.

        Contract:
            Reads only the passed model and plan; builds no runtime artifacts.
            Per the class Contract, return None to decline the pair, or a
            `CodegenCreationDiscovery` to stop discovery and use that result.

        Args:
            spell_codegen_model:
                Analyzed spell model for the current compile.
            spell_codegen_plan:
                Phase-10-selected plan whose concrete codegen style this
                strategy may choose.

        Returns:
            Optional[CodegenCreationDiscovery]:
                The claim result, or None when this strategy declines the pair.
        """
        raise NotImplementedError
