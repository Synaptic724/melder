from dataclasses import dataclass

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)


@dataclass(frozen=True, slots=True)
class CodegenCreationDiscovery:
    """
    Discovery result for one codegen creation selection pass.

    Purpose:
        Hold the selected codegen creation strategy id plus one compact reason
        describing why that strategy was chosen.
    """

    selected_strategy_id: str
    discovery_reason: str


class CodegenCreationDiscoverySystem:
    """
    Select the best current codegen creation strategy for one model/plan pair.

    Purpose:
        Interpret `SpellCodegenModel` plus `SpellCodegenPlan` and choose which
        codegen creation strategy the creation system should use.

    Contract:
        - Reads the model and plan only.
        - Does not produce emitted code or runtime artifacts itself.
        - Defaults to `generalized_codegen_creation` until ranking logic exists.
    """

    __slots__ = ()

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> CodegenCreationDiscovery:
        """
        Select the current best codegen creation strategy.
        """
        _ = spell_codegen_model
        _ = spell_codegen_plan
        return CodegenCreationDiscovery(
            selected_strategy_id="generalized_codegen_creation",
            discovery_reason="default_generalized_codegen_creation_strategy",
        )
