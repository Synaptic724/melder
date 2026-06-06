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
        """
        raise NotImplementedError

    @abstractmethod
    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> Optional[CodegenCreationDiscovery]:
        """
        Inspect the model/plan pair and optionally produce a discovery result.
        """
        raise NotImplementedError
