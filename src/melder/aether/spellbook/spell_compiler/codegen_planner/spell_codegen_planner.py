from typing import ClassVar

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan_strategy_builder import (
    SpellCodegenPlanStrategyBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable


class SpellCodegenPlanner(Cleanable):
    """
    Phase 12 codegen-plan orchestrator.

    Purpose:
        Consume an assessed model, create one neutral planner-owned codegen
        plan shell, and then let planner strategies define the final output
        object.

    Contract:
        - Owns no runtime/compiler artifacts.
        - Owns only the plan-strategy builder.
        - Always starts from the same neutral codegen plan shell for a given
          model.
        - Applies registered plan strategies in deterministic order.
        - Returns the final `SpellCodegenPlan` after planner strategies mutate
          it in place.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_strategy_builder",
    ]

    def __init__(
            self,
    ) -> None:
        """
        Build one planner with a plan-strategy builder.
        """
        super().__init__()
        self._strategy_builder = SpellCodegenPlanStrategyBuilder()

    def cleanup(self) -> None:
        """
        Deterministically release planner-owned state.

        Contract:
            - Idempotent.
            - Cleans the owned strategy builder directly.
            - Drops the planner's only owned reference so later use fails
              honestly through `check_cleaned()`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._strategy_builder.cleanup()
        del self._strategy_builder

    def build(
            self,
            model: SpellCodegenModel,
    ) -> SpellCodegenPlan:
        """
        Build one Phase 12 codegen plan from the assessed model.

        Contract:
            - Planner does not hardcode concrete runtime/codegen families.
            - Planner creates one neutral plan shell first.
            - Planner strategies are responsible for defining the real planning
              outcome.
        """
        plan = self._build_plan(model)
        strategy_names = self._strategy_builder.registered_strategy_names()
        strategies = self._strategy_builder.get_strategies(strategy_names)
        for strategy in strategies:
            strategy.apply(model, plan)
            plan.plan_strategy_ids = plan.plan_strategy_ids + (strategy.strategy_id,)
        return plan

    @staticmethod
    def _build_plan(
            model: SpellCodegenModel,
    ) -> SpellCodegenPlan:
        """
        Build one neutral planner-owned codegen plan shell from the model.

        Purpose:
            Give planner strategies one owned plan object to mutate without the
            planner facade pre-deciding families, lane support, or runtime
            hints that should actually come from strategy logic later.
        """
        return SpellCodegenPlan(
            processor_strategy_ids=model.snapshot_applied_strategy_ids(),
            plan_strategy_ids=(),
            no_overrides_family=None,
            overrides_family=None,
            mutation_family=None,
            route_key=model.route_family,
            supports_no_overrides_lane=False,
            supports_overrides_lane=False,
            supports_mutation_lane=False,
            requires_spellspace_request=False,
            execution_plan_dispatch_route=None,
            step_count=model.node_count,
            unique_spell_count=model.node_count,
            max_occurrence_depth=model.max_depth,
            max_dependency_count=model.max_dependency_count,
            fast_transient_no_overrides_enabled=False,
            lock_strategy_hint=None,
            registration_strategy_hint=None,
            call_mode_hint=None,
            emitter_family_id=None,
            fallback_reason=None,
            step_rows=(),
            metadata={},
        )
