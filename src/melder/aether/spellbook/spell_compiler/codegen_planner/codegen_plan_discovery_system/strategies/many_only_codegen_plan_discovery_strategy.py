from typing import Optional

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery import (
    CodegenPlanDiscovery,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.codegen_plan_discovery_system.codegen_plan_discovery_strategy import (
    CodegenPlanDiscoveryStrategy,
)


class ManyOnlyCodegenPlanDiscoveryStrategy(CodegenPlanDiscoveryStrategy):
    """
    Phase-10 discovery strategy for graphs made only of `Existence.many` spells.

    Purpose:
        Claim any model whose visible spell set contains more than one spell
        and every visible spell is `Existence.many`, so phase 10 can emit the
        dedicated many-only planning family.

    Registration:
        MELDER KERNEL - currently UNGUARDED (inherits the unguarded base). A built-in
        discovery strategy; not bound as a spell.

    Subsystem Context:
        A narrower claimant in the `codegen_plan_discovery_system/strategies` family;
        runs before the generalized fallback.

    System Context:
        Phase 10 (codegen planning) discovery of the conjure pipeline.
    """

    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Phase-10 discovery strategy: claims a model with >1 visible spell "
        "where ALL are Existence.many, selecting the many_only strategy/family. Reads the "
        "existence-occurrence shape only; declines otherwise."
    )
    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable discovery strategy id.
        """
        return "many_only_codegen_plan_discovery"

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
    ) -> Optional[CodegenPlanDiscovery]:
        """
        Claim the model when every visible spell is `Existence.many`.

        Contract:
            Declines (returns None) unless the model's existence-occurrence
            shape exists, has MORE than one visible spell, and ALL visible
            spells are `Existence.many`. On a match, selects the
            "many_only_codegen_plan" strategy / "many_only" family. Reads only
            the existence-occurrence shape.

        Args:
            spell_codegen_model:
                Processor-owned model whose existence-occurrence shape is
                inspected.

        Returns:
            Optional[CodegenPlanDiscovery]:
                The many-only selection, or None when the model is not all-many.
        """
        existence_occurrence_shape = spell_codegen_model.existence_occurrence_shape
        if existence_occurrence_shape is None:
            return None
        total_spell_count = existence_occurrence_shape.total_spell_count
        if total_spell_count <= 1:
            return None

        many_count = 0
        for existence, count in existence_occurrence_shape.existence_counts:
            if existence is Existence.many:
                many_count = count
                break
        if many_count != total_spell_count:
            return None

        return CodegenPlanDiscovery(
            selected_strategy_id="many_only_codegen_plan",
            discovery_reason="many_only_visible_spell_set",
            plan_family_id="many_only",
            candidate_codegen_style_ids=("many_only",),
        )
