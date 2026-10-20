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


class SoloCodegenPlanDiscoveryStrategy(CodegenPlanDiscoveryStrategy):
    """
    Phase-10 discovery strategy for the solo spell category.

    Purpose:
        Claim any model whose visible spell set contains exactly one spell,
        of any existence policy but `managed_spell_quantity`, so phase 10 can
        emit the dedicated solo planning family.

    Registration:
        MELDER KERNEL. A built-in
        discovery strategy; not bound as a spell.

    Subsystem Context:
        A narrower claimant in the `codegen_plan_discovery_system/strategies` family;
        runs before the generalized fallback.

    System Context:
        Phase 10 (codegen planning) discovery of the conjure pipeline.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Phase-10 discovery strategy: claims a single-visible-spell model
        (selecting the generalized_solo strategy / solo family), but declines when any
        collection socket is present - those route to collection-aware families.
        Collection-blind.
    """

    __slots__ = ()

    @property
    def strategy_id(self) -> str:
        """
        Return the stable discovery strategy id.
        """
        return "solo_codegen_plan_discovery"

    def discover(
            self,
            spell_codegen_model: SpellCodegenModel,
    ) -> Optional[CodegenPlanDiscovery]:
        """
        Claim the model when the visible spell count is exactly one.

        Contract:
            - Declines models whose injection shape carries any collection
              socket: the solo family is collection-blind by design, and a
              spell whose required collection wired zero providers still
              counts one visible spell yet must inject an empty list. Such
              models route to the collection-aware families instead.
            - Declines a model holding a `managed_spell_quantity` spell: its
              objects are leased through the generalized family's site plan
              (managed_spell_quantity S5, 2026-10-15), which the solo lowering
              does not dispense.
        """
        existence_occurrence_shape = spell_codegen_model.existence_occurrence_shape
        if existence_occurrence_shape is None:
            return None
        if existence_occurrence_shape.total_spell_count != 1:
            return None
        for existence, _count in existence_occurrence_shape.existence_counts:
            if existence is Existence.managed_spell_quantity:
                return None
        injection_shape = spell_codegen_model.injection_shape
        if injection_shape is not None:
            for instance_spec in injection_shape.instance_specs_by_instance_key.values():
                if instance_spec.collection_param_names:
                    return None
        return CodegenPlanDiscovery(
            selected_strategy_id="generalized_solo_codegen_plan",
            discovery_reason="solo_visible_spell_count_eq_1",
            plan_family_id="solo",
            candidate_codegen_style_ids=("generalized_solo",),
        )
