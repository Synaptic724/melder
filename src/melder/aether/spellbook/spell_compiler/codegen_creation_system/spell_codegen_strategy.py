from abc import ABC, abstractmethod

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_creation_system.codegen_creation.spell_codegen_creation import (
    SpellCodegenCreation,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


class SpellCodegenStrategy(ABC):
    """
    One codegen creation strategy contract.

    Purpose:
        Define the seam where codegen creation strategies consume the fitted
        model plus the chosen plan and populate the final artifact-owned
        `SpellCodegenCreation`.

    Contract:
        - Strategies read from `SpellCodegenModel` and `SpellCodegenPlan`.
        - Strategies mutate only the supplied `SpellCodegenCreation`.
        - Strategies do not mutate the planner or processor contracts.
    """

    __slots__ = ()

    @property
    @abstractmethod
    def strategy_id(self) -> str:
        """
        Return the stable strategy id.
        """
        raise NotImplementedError

    @abstractmethod
    def apply(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
            spell_codegen_creation: SpellCodegenCreation,
    ) -> None:
        """
        Populate the codegen creation output from model and plan truth.
        """
        raise NotImplementedError
