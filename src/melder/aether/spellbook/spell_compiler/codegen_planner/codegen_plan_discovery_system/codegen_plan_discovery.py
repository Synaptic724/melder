from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, slots=True)
class CodegenPlanDiscovery:
    """
    Discovery result for one codegen-plan selection pass.

    Purpose:
        Hold the planner's current selected strategy plus the higher-level
        planning family decision that phase 11 will later consume.

    Contract:
        - `selected_strategy_id` identifies the phase-10 strategy that will
          populate `SpellCodegenPlan`.
        - `plan_family_id` describes the structural planning family selected
          from processor-owned truth.
        - `candidate_codegen_style_ids` lists the concrete codegen styles that
          phase 11 is allowed to consider for this plan family.
        - `discovery_reason` is compact provenance for why the result was
          chosen.
        - Phase 10 owns family selection, not final runtime-emitter choice.
        - The candidate style ids are a bounded allow-list for phase 11, not a
          final emitted-runtime decision.

    Registration:
        MELDER KERNEL - value dataclass. A frozen result payload;
        not a bind target. (Guard classification is the owner's call.)

    Subsystem Context:
        The output of the `codegen_plan_discovery_system`: produced by a
        `CodegenPlanDiscoveryStrategy` and consumed by the planner facade.

    System Context:
        Phase 10 (codegen planning) family selection of the conjure pipeline.
    """

    # Unannotated on purpose: annotated class vars can be misread as dataclass fields.
    __ast_helper_access__ = "internal"
    __agent_purpose__ = (
        "access: internal. Phase-10 discovery result: selected_strategy_id, plan_family_id, "
        "candidate_codegen_style_ids (a bounded allow-list for Phase 11), and discovery_reason. "
        "Chooses a family, not the final emitter."
    )
    selected_strategy_id: str
    discovery_reason: str
    plan_family_id: str = "unknown"
    candidate_codegen_style_ids: Tuple[str, ...] = ()
