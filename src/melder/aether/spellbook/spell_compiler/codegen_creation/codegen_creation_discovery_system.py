from dataclasses import dataclass
from typing import Tuple

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
        Hold the ordered codegen creation strategy chain plus one compact
        reason describing why that chain was chosen.
    """

    selected_strategy_ids: Tuple[str, ...]
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
        - Defaults to the first generalized Phase-13 migration chain until the
          remaining creation lanes are ported fully.
    """

    __slots__ = ()

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
            spell_codegen_plan: SpellCodegenPlan,
    ) -> CodegenCreationDiscovery:
        """
        Select the current best ordered codegen creation strategy chain.

        Contract:
            - Reads planner metadata only for the current migration selection
              rule.
            - Returns a deterministic strategy tuple in execution order.
            - Does not mutate the model or plan.
        """
        _ = spell_codegen_model
        selected_plan_strategy_id = spell_codegen_plan.metadata.get(
            "selected_strategy_id"
        )
        if selected_plan_strategy_id == "generalized_codegen_plan":
            return CodegenCreationDiscovery(
                selected_strategy_ids=(
                    "generalized_creation_context_setup_codegen_creation",
                    "generalized_no_overrides_codegen_creation",
                    "generalized_overrides_codegen_creation",
                    "generalized_mutation_overrides_codegen_creation",
                ),
                discovery_reason=(
                    "default_generalized_plan_phase13_first_creation_chain"
                ),
            )
        return CodegenCreationDiscovery(
            selected_strategy_ids=(
                "generalized_no_overrides_codegen_creation",
            ),
            discovery_reason="fallback_no_overrides_creation_strategy",
        )
